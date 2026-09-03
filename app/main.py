from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import os

# Windows may not provide WMIC; avoid Joblib's physical-core probe at startup.
os.environ.setdefault('LOKY_MAX_CPU_COUNT', '1')

import pandas as pd, numpy as np, joblib, json, warnings

# Suppress scikit-learn version compatibility warnings (model trained with 1.8.0, runtime may differ)
warnings.filterwarnings('ignore', category=Warning, module='sklearn')

ROOT=Path(__file__).resolve().parents[1]
MODEL_PATH=ROOT/'model'/'coalguard_ai_mvp_risk_model.pkl'
DATA_PATH=ROOT/'data'/'india_coal_mine_safety_data_source_grounded.csv'
model_artifact=joblib.load(MODEL_PATH)
df=pd.read_csv(DATA_PATH)
# The supplied CSV is a feature table and does not include mine names, districts, subsidiaries, or coordinates.
# Generate stable display-only values from mine_id; never present them as official source fields.
df['mine_name']=df['mine_id'].map(lambda x: f'Coal Mine {x}')
df['district']='Not supplied'
df['subsidiary_id']='SUB-DEMO'
df['subsidiary_name']='Prototype Subsidiary Mapping'
df['latitude']=22.5 + (pd.factorize(df['state'])[0] % 8)*0.25 + (df.index % 7)*0.01
df['longitude']=78.0 + (pd.factorize(df['state'])[0] % 8)*0.30 + (df.index % 9)*0.01
df['mine_area']=np.nan
df['annual_production']=np.nan
df['production_target']=np.nan
df['status']='Active (Prototype)'

# Reproduce the graph feature logic used when the artifact was trained.
from sklearn.neighbors import NearestNeighbors
graph_cols=model_artifact['graph_reference_columns']
Xg=df[graph_cols].copy().fillna(df[graph_cols].median(numeric_only=True))
gs=(Xg-Xg.mean())/Xg.std(ddof=0).replace(0,1)
K=model_artifact.get('graph_k',5)
nn=NearestNeighbors(n_neighbors=K+1).fit(gs)
_, inds=nn.kneighbors(gs)
neigh=inds[:,1:]
df['graph_degree']=K
df['graph_mean_neighbor_compliance_rate']=df['compliance_rate'].to_numpy()[neigh].mean(axis=1)
df['graph_mean_neighbor_violation_count_30d']=df['total_violation_count_30d'].to_numpy()[neigh].mean(axis=1)
df['graph_mean_neighbor_environmental_breach_rate']=df['environmental_breach_rate'].to_numpy()[neigh].mean(axis=1)
df['graph_mean_neighbor_action_delay_days']=df['average_action_delay_days'].to_numpy()[neigh].mean(axis=1)

feature_cols=model_artifact['feature_columns']
classes=model_artifact['classes']
risk_label_cache={}

# Synthetic relationship layer for MVP visualization.
# It is intentionally derived from available records, not claimed as official relationships.

def safe(v):
    if pd.isna(v): return None
    if isinstance(v,(np.integer,np.floating)): return float(v)
    return v

def row_features(row):
    x=row[feature_cols].to_frame().T.copy()
    return x

def predict_row(row):
    X=row_features(row)
    if model_artifact['model_type']=='Random Forest':
        pred=model_artifact['rf_pipeline'].predict(X)[0]
        probs=model_artifact['rf_pipeline'].predict_proba(X)[0]
    else:
        enc=model_artifact['fitted_preprocessor'].transform(X)
        pi=int(model_artifact['xgb_model'].predict(enc)[0])
        pred=classes[pi]
        probs=model_artifact['xgb_model'].predict_proba(enc)[0]
    return pred, {c:float(p) for c,p in zip(classes,probs)}

def factors(r):
    candidates=[
        ('Overdue violations',float(r['overdue_violation_count']), 'higher is worse'),
        ('Repeat violations',float(r['repeat_violation_count']), 'higher is worse'),
        ('Critical violations',float(r['critical_violation_count']), 'higher is worse'),
        ('Serious incidents',float(r['serious_incident_count']), 'higher is worse'),
        ('Environmental breach rate',float(r['environmental_breach_rate']), 'higher is worse'),
        ('Compliance rate',float(r['compliance_rate']), 'lower is worse'),
        ('Inspection completion',float(r['inspection_completion_rate']), 'lower is worse'),
        ('Overdue corrective actions',float(r['overdue_action_count']), 'higher is worse'),
        ('Critical compliance gap',float(r['critical_compliance_gap']), 'higher is worse'),
        ('Neighbor-zone risk',float(r['neighbor_zone_risk']), 'higher is worse'),
    ]
    scored=[]
    for name,val,mode in candidates:
        s=val if 'higher' in mode else 100-val
        scored.append((name,round(s,2),val,mode))
    return sorted(scored,key=lambda x:x[1],reverse=True)[:5]

def activity_reasoning(r, row_index=None):
    """Convert aggregate mine signals into explainable activity events and state."""
    mine_id=str(r['mine_id'])
    zone_id=f"Z{((row_index or 0) % 12)+1:02d}"
    events=[]
    def event(kind, label, value, feature, evidence, contribution, action, severity='WATCH'):
        events.append({'event_id':f"ACT-{mine_id}-{len(events)+1:02d}",'type':kind,'label':label,'value':safe(value),'feature':feature,'evidence':evidence,'risk_contribution':round(float(contribution),1),'severity':severity,'recommended_action':action,'repeated':float(value)>1 if isinstance(value,(int,float,np.integer,np.floating)) else False})
    event('PRODUCTION','Production utilization activity',r['production_utilization_pct'],'production_utilization_pct',f"Utilization is {safe(r['production_utilization_pct'])}%",max(0,(float(r['production_utilization_pct'])-85)*.2),'Review production conditions and operating controls','WATCH' if float(r['production_utilization_pct'])<95 else 'ELEVATED')
    event('ATTENDANCE','Attendance and workforce activity',r['missed_inspection_count'],'missed_inspection_count',f"{int(r['missed_inspection_count'])} inspections missed in the current feature window",min(10,float(r['missed_inspection_count'])*1.5),'Confirm workforce and inspection coverage','ELEVATED' if float(r['missed_inspection_count'])>0 else 'STABLE')
    event('INSPECTION','Inspection activity',r['inspection_count_30d'],'inspection_count_30d',f"{int(r['inspection_count_30d'])} inspections recorded in 30 days; completion {safe(r['inspection_completion_rate'])}%",max(0,(100-float(r['inspection_completion_rate']))*.15),'Schedule and complete overdue inspections','ELEVATED' if float(r['inspection_completion_rate'])<80 else 'STABLE')
    event('SAFETY_OBSERVATION','Unsafe observation activity',r['critical_observation_count'],'critical_observation_count',f"{int(r['critical_observation_count'])} critical observations and {int(r['observation_count_30d'])} observations recorded",min(20,float(r['critical_observation_count'])*2),'Perform immediate safety review of the affected zone','CRITICAL' if float(r['critical_observation_count'])>0 else 'STABLE')
    event('INCIDENT','Incident activity',r['serious_incident_count'],'serious_incident_count',f"{int(r['serious_incident_count'])} serious incidents recorded",min(20,float(r['serious_incident_count'])*3),'Open incident review and verify controls','CRITICAL' if float(r['serious_incident_count'])>0 else 'STABLE')
    event('ENVIRONMENT','Environmental monitoring activity',r['environmental_threshold_breach_count'],'environmental_threshold_breach_count',f"{int(r['environmental_threshold_breach_count'])} threshold breaches; anomaly count {int(r['environmental_anomaly_count'])}",min(15,float(r['environmental_threshold_breach_count'])*1.5),'Inspect environmental controls and recent readings','ELEVATED' if float(r['environmental_threshold_breach_count'])>0 else 'STABLE')
    event('CONTRACTOR','Contractor activity',r['high_risk_contractor_count'],'high_risk_contractor_count',f"{int(r['high_risk_contractor_count'])} high-risk contractors; compliance score {safe(r['contractor_compliance_score'])}",min(15,float(r['high_risk_contractor_count'])*1.5),'Review contractor permits, training, and supervision','ELEVATED' if float(r['high_risk_contractor_count'])>0 else 'STABLE')
    event('VIOLATION','Violation activity',r['repeat_violation_count'],'repeat_violation_count',f"{int(r['open_violation_count'])} open, {int(r['overdue_violation_count'])} overdue, {int(r['repeat_violation_count'])} repeat violations",min(25,float(r['repeat_violation_count'])*1.2+float(r['overdue_violation_count'])*.5),'Escalate repeat and overdue violations for remediation','CRITICAL' if float(r['repeat_violation_count'])>0 else 'STABLE')
    event('CORRECTIVE_ACTION','Corrective-action activity',r['overdue_action_count'],'overdue_action_count',f"{int(r['overdue_action_count'])} overdue actions; average delay {safe(r['average_action_delay_days'])} days",min(20,float(r['overdue_action_count'])*.6+float(r['average_action_delay_days'])*.2),'Assign owners and close overdue corrective actions','CRITICAL' if float(r['overdue_action_count'])>0 else 'STABLE')
    active=[x for x in events if x['severity'] in ('ELEVATED','CRITICAL')]
    repeated=[x for x in events if x['repeated'] and x['severity'] in ('ELEVATED','CRITICAL')]
    abnormal=[]
    if float(r['violation_growth_rate'])>0: abnormal.append(f"Violation activity is growing at {safe(r['violation_growth_rate'])}%")
    if float(r['incident_growth_rate'])>0: abnormal.append(f"Incident activity is growing at {safe(r['incident_growth_rate'])}%")
    if float(r['production_change_pct'])<0: abnormal.append(f"Production changed by {safe(r['production_change_pct'])}%")
    state='CRITICAL_ACTIVITY' if any(x['severity']=='CRITICAL' for x in active) else ('ELEVATED_ACTIVITY' if active else 'STABLE_ACTIVITY')
    top=sorted(active,key=lambda x:x['risk_contribution'],reverse=True)[:3]
    primary=top[0] if top else events[0]
    explanation=f"{state.replace('_',' ').title()} because {primary['evidence'].lower()}."
    if len(top)>1: explanation+=f" Related {top[1]['label'].lower()} increases contextual risk."
    path=[f"Mine {mine_id}",f"Zone {zone_id}",primary['label'],'Observation','Violation','Requirement','Corrective Action','Risk']
    return {'mine_id':mine_id,'zone_id':zone_id,'state':state,'events':events,'repeated_activities':[x['label'] for x in repeated],'abnormal_patterns':abnormal,'dependencies':['Inspection coverage -> safety observations -> violations -> corrective actions','Contractor activity -> observations -> violations'],'contributing_factors':[{'name':x['label'],'feature':x['feature'],'evidence':x['evidence'],'risk_contribution':x['risk_contribution']} for x in top],'relationship_path':path,'explanation':explanation,'recommended_action':primary['recommended_action']}

app=FastAPI(title='CoalGuard AI MVP API', version='1.0.0')
app.mount('/static', StaticFiles(directory=ROOT/'app'/'static'), name='static')

@app.get('/')
def home(): return FileResponse(ROOT/'app'/'static'/'index.html')

@app.get('/api/health')
def health():
    return {'status':'ok','model_type':model_artifact['model_type'],'rows':len(df),'model_artifact':'loaded'}

@app.get('/api/summary')
def summary():
    preds=[]; probs=[]
    for _,r in df.iterrows():
        p,pr=predict_row(r); preds.append(p); probs.append(max(pr.values()))
    return {
        'mines':len(df),
        'high_risk':sum(x in ('HIGH','CRITICAL') for x in preds),
        'low_risk':sum(x=='LOW' for x in preds),
        'medium_risk':sum(x=='MEDIUM' for x in preds),
        'open_violations':int(df['open_violation_count'].sum()),
        'overdue_actions':int(df['overdue_action_count'].sum()),
        'compliance_rate':round(float(df['compliance_rate'].mean()),1),
        'environment_alerts':int(df['environmental_anomaly_count'].sum()),
        'model':model_artifact['model_type'],
        'target_note':model_artifact['target_note'],
        'activity_layer':'Internal Mine Activity Detection & Reasoning'
    }

@app.get('/api/mines')
def mines():
    out=[]
    for _,r in df.iterrows():
        p,pr=predict_row(r)
        score={'LOW':25,'MEDIUM':50,'HIGH':75,'CRITICAL':90}.get(p,50)
        out.append({'mine_id':r['mine_id'],'mine_name':r['mine_name'],'state':r['state'],'district':r['district'], 'mine_type':r['mine_type'],'coal_type':r['coal_type'],'latitude':safe(r['latitude']),'longitude':safe(r['longitude']),'compliance_rate':safe(r['compliance_rate']),'risk':p,'risk_score':score,'probabilities':pr,'violations':safe(r['open_violation_count']),'overdue_actions':safe(r['overdue_action_count'])})
    return out

def section_rows(kind):
    rows=[]
    for _,r in df.iterrows():
        mine_key=str(r['mine_id'])
        if mine_key not in risk_label_cache: risk_label_cache[mine_key]=predict_row(r)[0]
        p=risk_label_cache[mine_key]
        base={'mine_id':mine_key,'mine_name':r['mine_name'],'state':r['state'],'risk':p}
        if kind=='compliance':
            base.update({'compliance_rate':safe(r['compliance_rate']),'overdue_compliance_rate':safe(r['overdue_compliance_rate']),'critical_compliance_gap':safe(r['critical_compliance_gap']),'open_violations':safe(r['open_violation_count'])})
        elif kind=='inspections':
            base.update({'inspection_count_30d':safe(r['inspection_count_30d']),'days_since_last_inspection':safe(r['days_since_last_inspection']),'missed_inspection_count':safe(r['missed_inspection_count']),'inspection_completion_rate':safe(r['inspection_completion_rate']),'observation_count_30d':safe(r['observation_count_30d'])})
        elif kind=='violations':
            base.update({'open_violations':safe(r['open_violation_count']),'overdue_violations':safe(r['overdue_violation_count']),'high_severity_violations':safe(r['high_severity_violation_count']),'critical_violations':safe(r['critical_violation_count']),'repeat_violations':safe(r['repeat_violation_count']),'violation_growth_rate':safe(r['violation_growth_rate'])})
        else:
            base.update({'total_actions':safe(r['total_action_count']),'overdue_actions':safe(r['overdue_action_count']),'average_delay_days':safe(r['average_action_delay_days']),'completion_rate':safe(r['action_completion_rate']),'on_time_rate':safe(r['action_on_time_rate']),'verification_pending':safe(r['verification_pending_count'])})
        rows.append(base)
    return rows

def section_summary(kind, rows):
    if kind=='compliance':
        return {'average_compliance':round(float(df['compliance_rate'].mean()),1),'open_violations':int(df['open_violation_count'].sum()),'critical_gaps':int(df['critical_compliance_gap'].sum())}
    if kind=='inspections':
        return {'inspections_30d':int(df['inspection_count_30d'].sum()),'missed_inspections':int(df['missed_inspection_count'].sum()),'average_completion':round(float(df['inspection_completion_rate'].mean()),1)}
    if kind=='violations':
        return {'open_violations':int(df['open_violation_count'].sum()),'overdue_violations':int(df['overdue_violation_count'].sum()),'critical_violations':int(df['critical_violation_count'].sum()),'repeat_violations':int(df['repeat_violation_count'].sum())}
    return {'total_actions':int(df['total_action_count'].sum()),'overdue_actions':int(df['overdue_action_count'].sum()),'average_delay_days':round(float(df['average_action_delay_days'].mean()),1),'pending_verification':int(df['verification_pending_count'].sum())}

def audit_events():
    events=[]
    for _,r in df.iterrows():
        mine_id=str(r['mine_id']); name=r['mine_name']
        def add(event_type, entity, evidence, status, feature):
            events.append({'event_id':f"AUD-{mine_id}-{len(events)+1:04d}",'mine_id':mine_id,'mine_name':name,'event_type':event_type,'entity':entity,'status':status,'evidence':evidence,'source':f"Aggregate CSV feature: {feature}",'recorded_as':'Derived snapshot event'})
        add('DATA_INGESTION','Mine',f"Mine record loaded for {name}",'COMPLETED','mine_id')
        add('RISK_EVALUATION','Risk',f"{risk_label_cache.get(mine_id, predict_row(r)[0])} risk evaluated from model features",'COMPLETED','model artifact + feature columns')
        add('INSPECTION_REVIEW','Inspection',f"{int(r['inspection_count_30d'])} inspections and {int(r['missed_inspection_count'])} missed inspections in the feature window",'ATTENTION_REQUIRED' if float(r['missed_inspection_count'])>0 else 'COMPLETED','inspection_count_30d / missed_inspection_count')
        add('VIOLATION_REVIEW','Violation',f"{int(r['open_violation_count'])} open, {int(r['overdue_violation_count'])} overdue, {int(r['repeat_violation_count'])} repeat violations",'ATTENTION_REQUIRED' if float(r['open_violation_count'])>0 else 'COMPLETED','open_violation_count / overdue_violation_count')
        add('ENVIRONMENT_REVIEW','Environment',f"{int(r['environmental_anomaly_count'])} anomalies and {int(r['environmental_threshold_breach_count'])} threshold breaches",'ATTENTION_REQUIRED' if float(r['environmental_threshold_breach_count'])>0 else 'COMPLETED','environmental_anomaly_count / environmental_threshold_breach_count')
        add('CORRECTIVE_ACTION_REVIEW','Corrective Action',f"{int(r['overdue_action_count'])} overdue actions; {int(r['verification_pending_count'])} pending verification",'ATTENTION_REQUIRED' if float(r['overdue_action_count'])>0 else 'COMPLETED','overdue_action_count / verification_pending_count')
    return events

@app.get('/api/audit')
def audit():
    events=audit_events()
    return {'section':'audit','source_note':'Derived from the current aggregate CSV snapshot; not an immutable user event log.','summary':{'events':len(events),'mines':len(df),'attention_required':sum(x['status']=='ATTENTION_REQUIRED' for x in events),'completed':sum(x['status']=='COMPLETED' for x in events)},'events':events}

@app.get('/api/compliance')
def compliance():
    rows=section_rows('compliance'); return {'section':'compliance','summary':section_summary('compliance',rows),'rows':rows}

@app.get('/api/inspections')
def inspections():
    rows=section_rows('inspections'); return {'section':'inspections','summary':section_summary('inspections',rows),'rows':rows}

@app.get('/api/violations')
def violations():
    rows=section_rows('violations'); return {'section':'violations','summary':section_summary('violations',rows),'rows':rows}

@app.get('/api/actions')
def actions():
    rows=section_rows('actions'); return {'section':'actions','summary':section_summary('actions',rows),'rows':rows}

@app.get('/api/mines/{mine_id}')
def mine(mine_id:str):
    hit=df[df.mine_id.astype(str)==mine_id]
    if hit.empty: raise HTTPException(404,'Mine not found')
    r=hit.iloc[0]; p,pr=predict_row(r); reasoning=activity_reasoning(r,hit.index[0])
    return {'mine':{c:safe(r[c]) for c in ['mine_id','mine_name','subsidiary_name','state','district','mine_type','coal_type','latitude','longitude','mine_area','mine_age_years','production_target','annual_production','status']}, 'prediction':{'label':p,'probabilities':pr,'method':model_artifact['model_type'],'explanation':reasoning},'features':{c:safe(r[c]) for c in feature_cols},'top_factors':[{'name':x[0],'severity_score':x[1],'value':x[2]} for x in factors(r)], 'graph':graph_for(mine_id)}

def graph_for(mine_id):
    hit=df[df.mine_id.astype(str)==mine_id]
    if hit.empty:return {'nodes':[],'edges':[]}
    i=hit.index[0]; r=hit.iloc[0]; reasoning=activity_reasoning(r,i)
    nodes=[{'id':mine_id,'label':r['mine_name'],'type':'MINE'}]
    edges=[]
    def add(id,label,typ,rel,source=mine_id):
        nodes.append({'id':id,'label':label,'type':typ}); edges.append({'source':source,'target':id,'label':rel})
    add('SUB-'+str(r['subsidiary_id']),str(r['subsidiary_name']),'SUBSIDIARY','OPERATED_BY')
    add('ZONE-'+mine_id,'Primary Operational Zone','ZONE','HAS_ZONE')
    add('INS-'+mine_id,'Latest Inspection','INSPECTION','HAS_INSPECTION')
    add('OBS-'+mine_id,'Critical Observation','OBSERVATION','GENERATED')
    add('V-'+mine_id,f"{int(r['open_violation_count'])} Open Violations",'VIOLATION','INDICATES')
    add('REQ-'+mine_id,'Prototype Compliance Requirement','REQUIREMENT','VIOLATES')
    add('ACT-'+mine_id,f"{int(r['overdue_action_count'])} Overdue Actions",'ACTION','REQUIRES_ACTION')
    add('ENV-'+mine_id,f"{int(r['environmental_anomaly_count'])} Environment Alerts",'ENVIRONMENT','MONITORED_BY')
    activity_id='ACTIVITY-'+mine_id; add(activity_id,reasoning['state'],'ACTIVITY_STATE','HAS_ACTIVITY_STATE')
    activity_node='ACTEVENT-'+mine_id; add(activity_node,reasoning['contributing_factors'][0]['name'] if reasoning['contributing_factors'] else 'Internal Activity','ACTIVITY_EVENT','DETECTED_ACTIVITY',activity_id)
    add('RISK-'+mine_id,f"{reasoning['state']} · {reasoning['explanation'][:60]}",'RISK','INCREASES_RISK','ACT-'+mine_id)
    edges.extend([{'source':activity_node,'target':'ZONE-'+mine_id,'label':'LOCATED_IN'},{'source':activity_node,'target':'OBS-'+mine_id,'label':'GENERATES'},{'source':'V-'+mine_id,'target':'ACT-'+mine_id,'label':'TRIGGERS'},{'source':'ACT-'+mine_id,'target':'RISK-'+mine_id,'label':'CONTRIBUTES_TO'}])
    return {'nodes':nodes,'edges':edges,'reasoning':reasoning}

@app.get('/api/graph/{mine_id}')
def graph(mine_id:str):
    if not (df.mine_id.astype(str)==mine_id).any(): raise HTTPException(404,'Mine not found')
    return graph_for(mine_id)

class PredictRequest(BaseModel):
    mine_id:str

@app.post('/api/predict')
def predict(req:PredictRequest):
    hit=df[df.mine_id.astype(str)==req.mine_id]
    if hit.empty: raise HTTPException(404,'Mine not found')
    r=hit.iloc[0]; p,pr=predict_row(r); reasoning=activity_reasoning(r,hit.index[0])
    return {'mine_id':req.mine_id,'risk':p,'probabilities':pr,'method':model_artifact['model_type'],'factors':[{'name':x[0],'score':x[1],'value':x[2]} for x in factors(r)],'explanation':reasoning}
