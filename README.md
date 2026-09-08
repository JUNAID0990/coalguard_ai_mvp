# CoalGuard AI

> **AI-assisted coal mine safety, compliance, activity monitoring, and risk intelligence — MVP**

CoalGuard AI is a prototype governance platform for exploring mine-level safety and compliance signals through a web dashboard. It combines a FastAPI backend, a pre-trained machine-learning artifact, a structured mine feature dataset, explainable risk factors, a GIS view, and a relationship/activity layer for investigation workflows.

⚠️ **Important:** This repository is an MVP/prototype. The bundled mine-level safety, inspection, violation, incident, environmental, zone, and contractor values are simulated features grounded by source-level coal-mine statistics. They must **not** be treated as official mine-specific measurements or used as a real-world safety decision system without validation.

---

## ✨ What CoalGuard AI Does

CoalGuard AI provides a centralized interface for:

- **Mine registry** — browse mine-level records and risk classifications.
- **Risk intelligence** — generate model-backed risk labels, probability estimates, and top contributing signals.
- **Compliance monitoring** — inspect compliance rates, open violations, and critical compliance gaps.
- **Inspection monitoring** — review inspection volume, missed inspections, completion rates, and observation activity.
- **Violation intelligence** — surface open, overdue, critical, repeat, and growing violation signals.
- **Corrective actions** — track overdue actions, action completion, delay, and pending verification.
- **GIS visualization** — display the mine registry on an interactive Leaflet map.
- **CoalGuard Graph** — visualize similarity/relationship context derived from the mine feature space.
- **Activity reasoning** — convert aggregate mine signals into explainable activity events, abnormal patterns, contributing factors, and recommended actions.
- **Audit-oriented views** — provide a governance-oriented interface for reviewing evidence and actions.
- **API access** — FastAPI automatically exposes interactive API documentation through `/docs`.

---

## 🧠 High-Level Architecture

```text
                    ┌───────────────────────────┐
                    │        Web Browser         │
                    │  HTML + CSS + JavaScript   │
                    │ Chart.js + Leaflet GIS     │
                    └─────────────┬─────────────┘
                                  │ HTTP / JSON
                                  ▼
                    ┌───────────────────────────┐
                    │        FastAPI App        │
                    │        app/main.py        │
                    ├───────────────────────────┤
                    │ Dashboard / Mine APIs     │
                    │ Risk / Compliance APIs    │
                    │ Inspections / Violations │
                    │ Actions / Graph / Audit   │
                    └───────┬─────────┬─────────┘
                            │         │
                ┌───────────┘         └────────────┐
                ▼                                  ▼
     ┌─────────────────────┐             ┌─────────────────────┐
     │ ML Model Artifact   │             │ Mine Feature Data   │
     │ .pkl / Joblib       │             │ CSV / 393 rows      │
     │ XGBoost or artifact │             │ 47 columns          │
     └─────────────────────┘             └─────────────────────┘
                │                                  │
                └────────────────┬─────────────────┘
                                 ▼
                    ┌───────────────────────────┐
                    │ Risk + Activity Reasoning │
                    │ + Graph-derived Signals   │
                    └───────────────────────────┘
```

### Graph / similarity layer

The backend reconstructs a **k-nearest-neighbor similarity graph** from graph reference features stored in the model artifact. Neighbor-level aggregate signals are then used to enrich mine context, including neighboring compliance, violations, environmental breaches, and action delays.

The UI also exposes a governance-style relationship path for investigation and demonstration purposes.

---

## 🤖 Machine Learning

The repository includes a pre-trained model artifact:

```text
model/coalguard_ai_mvp_risk_model.pkl
```

The application loads the artifact with Joblib and supports the model structure stored inside it. The current artifact records **XGBoost** as the selected MVP model type.

The backend uses the artifact's:

- feature columns
- fitted preprocessing object
- model object
- class labels
- graph reference columns
- graph neighborhood size
- target metadata

For each mine, CoalGuard produces a risk label from the model output and derives a probability distribution across the available classes.

### Risk labels shown by the application

```text
LOW
MEDIUM
HIGH
CRITICAL
```

The dashboard also maps these labels to an MVP risk score for visualization. That score is a presentation layer and should not be interpreted as a calibrated regulatory or actuarial score.

---

## 📊 Data & Provenance

The bundled feature dataset is:

```text
data/india_coal_mine_safety_data_source_grounded.csv
```

The accompanying notes file states that the dataset is grounded in the **Coal Directory of India 2024–25** source and represents:

- **373 operational coal mines**
- **20 operational lignite mines**
- **393 total rows**
- **47 columns**, including `mine_id` and `state`

However, the source material is primarily aggregate-level information. Mine-level safety, inspection, violation, action, incident, environmental, zone, and contractor attributes in the CSV are therefore **simulated** for MVP development.

See:

```text
data/india_coal_mine_safety_data_source_notes.txt
```

### Synthetic proxy target

The existing model was trained against a **synthetic proxy risk label** because the supplied CSV does not contain a verified mine-level risk target.

Therefore:

> **Do not report the model's displayed performance as real-world predictive accuracy.**

The system is intended for architecture validation, product prototyping, UI demonstration, and experimentation with the governance workflow.

---

## 🖥️ Frontend

The frontend is a lightweight static application served directly by FastAPI.

```text
app/static/
├── index.html
├── styles.css
├── app.js
└── logo.svg
```

### Frontend technologies

- HTML5
- CSS3
- Vanilla JavaScript
- [Chart.js](https://www.chartjs.org/) for charts
- [Leaflet](https://leafletjs.com/) for GIS mapping

The UI includes navigation for:

```text
Dashboard
Mines
GIS Map
CoalGuard Graph
Compliance
Inspections
Violations
Corrective Actions
Risk Intelligence
Audit Trail
```

---

## ⚙️ Backend

The API is implemented with **FastAPI** in:

```text
app/main.py
```

FastAPI serves both the application UI and JSON endpoints.

### Health endpoint

```http
GET /api/health
```

Returns basic application/model health information, including the loaded model type and dataset row count.

### Other application endpoints

The backend also exposes endpoints used by the dashboard for summary data, mine records, compliance, inspections, violations, corrective actions, risk information, graph/activity data, and audit-oriented information.

The exact interactive API schema is available from FastAPI at:

```text
http://127.0.0.1:8000/docs
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/JUNAID0990/coalguard_ai_mvp.git
cd coalguard_ai_mvp
```

### 2. Create a virtual environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
uvicorn app.main:app --reload
```

### 5. Open CoalGuard AI

Application:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 🔐 Environment Configuration

An example environment file is provided:

```text
.env.example
```

Current placeholders:

```env
FIREBASE_PROJECT_ID=
GOOGLE_APPLICATION_CREDENTIALS=
```

The current MVP does not require these variables for the basic local dashboard flow. They are provided as configuration placeholders for integrations/extensions such as Firebase or Google Cloud services.

**Never commit real credentials, service-account JSON files, tokens, or private keys to Git.**

---

## 📁 Repository Structure

```text
coalguard_ai_mvp/
│
├── app/
│   ├── main.py                         # FastAPI application + model/data logic
│   └── static/
│       ├── index.html                  # Main dashboard shell
│       ├── styles.css                  # UI styling
│       ├── app.js                      # Client-side application logic
│       └── logo.svg                    # CoalGuard branding
│
├── data/
│   ├── india_coal_mine_safety_data_source_grounded.csv
│   └── india_coal_mine_safety_data_source_notes.txt
│
├── model/
│   └── coalguard_ai_mvp_risk_model.pkl # Pre-trained MVP model artifact
│
├── .env.example
├── requirements.txt
└── README.md
```

> `app/__pycache__/` may appear in a working tree from local Python execution and should normally not be tracked in source control.

---

## 📦 Dependencies

The project currently pins/declares the following core packages:

| Package | Purpose |
|---|---|
| FastAPI | Backend API and application server |
| Uvicorn | ASGI server |
| Pandas | Tabular data loading and processing |
| NumPy | Numerical operations |
| scikit-learn | Preprocessing and nearest-neighbor graph construction |
| XGBoost | Risk model support |
| Joblib | Loading the serialized model artifact |
| python-multipart | Multipart/form-data support |

Install all dependencies with:

```bash
pip install -r requirements.txt
```

---

## 🔎 Explainability & Activity Reasoning

CoalGuard includes an additional reasoning layer on top of model predictions.

Rather than only displaying a risk label, the backend converts measurable feature signals into explainable activity events such as:

- production utilization activity
- attendance/workforce activity
- inspection activity
- unsafe observation activity
- incident activity
- environmental monitoring activity
- contractor activity
- violation activity
- corrective-action activity

These signals are used to identify:

```text
Stable Activity
Elevated Activity
Critical Activity
```

The activity layer can also expose:

- repeated activities
- abnormal patterns
- dependencies between activity types
- contributing factors
- relationship paths
- evidence text
- recommended actions

This makes the MVP more suitable for **investigation and governance workflows** than a simple classification demo.

---

## 🗺️ GIS View

The dashboard includes a Leaflet-based map for mine visualization.

Because the supplied feature dataset does not provide verified mine-level coordinates, the application currently generates **stable display-only coordinates** from available row/state information. These coordinates are for prototype visualization only and must not be presented as official mine locations.

---

## ⚠️ Prototype Limitations

This project intentionally contains several MVP limitations:

1. **Synthetic mine-level features** — many safety/compliance fields are simulated.
2. **Synthetic target** — the risk target is a proxy rather than a verified historical outcome.
3. **No claim of production accuracy** — model outputs are not validated for operational safety decisions.
4. **Display-only GIS coordinates** — the current map locations are generated for visualization.
5. **Prototype relationships** — some governance relationship mappings are demonstration logic rather than authoritative organizational relationships.
6. **Version compatibility** — the backend suppresses scikit-learn compatibility warnings because the serialized artifact may have been trained under a specific scikit-learn version.
7. **No authentication/authorization layer in the basic MVP flow** — the application should not be exposed publicly with sensitive operational data without an appropriate security architecture.

---

## 🛡️ Production Considerations

Before using a system like CoalGuard AI with real mine or regulatory data, the following should be addressed:

### Data

- replace simulated features with verified mine-level records
- establish data ownership and provenance
- validate timestamps, identifiers, locations, and organizational relationships
- implement data quality checks and schema validation

### Machine learning

- define a verified target variable
- establish train/validation/test splits by time and mine
- calibrate probabilities
- measure precision/recall and class-specific performance
- perform drift monitoring
- test model robustness and fairness
- maintain model/version metadata

### Governance

- retain source evidence for every actionable signal
- distinguish observed facts from model inference
- provide human review and override workflows
- maintain immutable audit records
- define escalation policies

### Security

- add authentication and role-based access control
- protect credentials and service accounts
- use HTTPS/TLS
- validate uploads and API inputs
- enforce least-privilege access
- add logging, monitoring, rate limiting, and secret management

### Reliability

- add automated tests
- add CI/CD
- containerize deployment
- add health/readiness checks
- use structured application logging
- introduce observability and alerting

---

## 🧪 Development Notes

The application loads the model artifact and CSV during backend startup. For local development, `uvicorn --reload` is convenient, but production deployments should use an appropriate process model and deployment configuration.

The application also sets a CPU-related environment value to avoid Joblib/Locy-style physical-core probing issues on environments where system utilities such as WMIC are unavailable.

---

## 🛠️ Suggested Development Workflow

```text
Source Data
   ↓
Schema Validation
   ↓
Feature Engineering
   ↓
Verified Target / Labels
   ↓
Model Training + Evaluation
   ↓
Model Artifact Registry
   ↓
FastAPI Inference Layer
   ↓
Explainability + Activity Reasoning
   ↓
Dashboard / GIS / Governance Views
   ↓
Human Review + Audit
```

---

## 🎯 Intended Use

CoalGuard AI is best suited for:

- AI/ML prototype demonstrations
- research and experimentation
- safety analytics interface development
- governance workflow design
- graph + tabular risk intelligence experiments
- portfolio and technical project demonstrations

It is **not** a replacement for statutory inspection, certified safety systems, regulatory decisions, emergency response procedures, or qualified professional judgment.

---

## 📌 Project Status

**Status:** MVP / Prototype

The repository demonstrates an end-to-end architecture spanning data ingestion, model inference, graph-derived context, explainable activity reasoning, REST APIs, dashboard visualization, and GIS presentation.

---

## 👤 Author

**Junaid Khan**

GitHub: [@JUNAID0990](https://github.com/JUNAID0990)

Repository: [coalguard_ai_mvp](https://github.com/JUNAID0990/coalguard_ai_mvp)

---

## 📄 License

No explicit license file is currently included in the repository. Until a `LICENSE` file is added, reuse and redistribution rights should not be assumed.

---

## ⭐ Why This MVP Matters

CoalGuard AI is designed around a practical idea: **risk intelligence should connect prediction with evidence, relationships, activity signals, and corrective action.**

Instead of treating an ML model as the entire product, this MVP places the model inside a broader governance workflow:

```text
Signals → Context → Risk → Explanation → Action → Audit
```

That architecture provides a foundation for evolving the project from a demonstration into a validated, evidence-backed mine safety intelligence platform.
