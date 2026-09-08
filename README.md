# CoalGuard

> A practical dashboard for coal mine safety, compliance, inspections, incidents, and risk review.

CoalGuard is a working MVP built to bring mine information and safety-related signals into one place. The project combines a FastAPI backend, a browser dashboard, a pre-trained risk model, mine-level feature data, a map view, and several investigation-oriented views.

The project is still a prototype. A number of mine-level values in the included dataset are simulated and are provided for development and demonstration. They should not be treated as official mine records or used to make real-world safety decisions.

---

## Overview

The main goal of CoalGuard is simple: make it easier to look at mine conditions, spot areas that need attention, and follow the path from a reported signal to a possible corrective action.

The dashboard currently covers:

- Mine records and risk status
- Compliance information
- Inspection activity
- Violations and repeat violations
- Corrective actions
- Incident and environmental signals
- Contractor-related activity
- Interactive mine map
- Mine relationship and similarity views
- Risk factors and supporting signals
- Activity and investigation views
- Audit-oriented information
- FastAPI API documentation

---

## How It Works

```text
                         CoalGuard Dashboard
                                  │
                                  ▼
                            FastAPI Backend
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
              Mine Feature Data            Risk Model
                    │                           │
                    └─────────────┬─────────────┘
                                  ▼
                       Risk & Activity Results
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
                  Risk          Map          Reports
                    │
                    ▼
              Review & Action
```

The backend loads the supplied data and model when the application starts. It prepares the feature data, builds the similarity information used by the graph views, and provides the results to the browser through JSON endpoints.

---

## Main Sections

### Dashboard

A high-level view of the mine dataset, current risk categories, compliance figures, open violations, overdue actions, and other useful indicators.

### Mines

A mine registry with basic mine information, location data, compliance values, violations, overdue actions, and the current model result.

### GIS Map

An interactive Leaflet map used to display the mine records geographically.

### CoalGuard Graph

A similarity-based view that connects records using selected feature information. It is intended to help explore patterns between mines rather than represent an official organizational structure.

### Compliance

Shows compliance rates, open violations, and critical compliance gaps across the available records.

### Inspections

Provides inspection counts, missed inspections, completion rates, observation activity, and time since the last inspection.

### Violations

Brings together open, overdue, high-severity, critical, repeat, and growing violation signals.

### Corrective Actions

Tracks action counts, overdue actions, completion, delays, on-time rates, and pending verification.

### Risk Intelligence

Provides the model result together with probabilities and selected signals that can help explain why a record deserves attention.

### Audit Trail

Provides an interface for reviewing governance-related information and action history within the prototype.

---

## Risk Model

The repository contains a serialized model at:

```text
model/coalguard_ai_mvp_risk_model.pkl
```

The current model artifact uses XGBoost. The application reads the model metadata, preprocessing information, feature list, class labels, and graph reference columns from the saved artifact.

The current application works with these risk categories:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

The probabilities shown in the dashboard come from the saved model. The additional numeric risk score used by the interface is mainly a convenient way to display the categories and should not be considered a calibrated safety score.

---

## Data

The included dataset is:

```text
data/india_coal_mine_safety_data_source_grounded.csv
```

The accompanying notes describe the dataset as being based on information from the Coal Directory of India 2024–25. It contains 393 records covering 373 operational coal mines and 20 operational lignite mines, with 47 columns.

The source material does not contain all of the mine-level fields needed by this prototype. Because of that, several fields covering safety observations, inspections, violations, incidents, environmental conditions, corrective actions, zones, and contractors have been simulated.

More detail is available in:

```text
data/india_coal_mine_safety_data_source_notes.txt
```

### Important note about the target

The supplied data does not contain a verified mine-level risk outcome. The model therefore uses a synthetic proxy target for the MVP.

Model results from this repository should be treated as development results, not evidence of real-world predictive performance.

---

## Activity Review

CoalGuard also turns several feature values into activity records so that a user can see what may be driving attention toward a mine.

Examples include:

- Production utilization
- Workforce and attendance activity
- Inspection activity
- Safety observations
- Incidents
- Environmental monitoring
- Contractor activity
- Violations
- Corrective actions

The application groups these signals into states such as:

```text
STABLE_ACTIVITY
ELEVATED_ACTIVITY
CRITICAL_ACTIVITY
```

For selected records, the activity view can also show repeated activity, unusual patterns, contributing signals, evidence text, relationships between events, and a suggested next action.

These are generated from the available prototype fields and should be read as supporting context rather than verified findings.

---

## Graph / Similarity Layer

The backend rebuilds a k-nearest-neighbor graph from the graph reference features stored in the model artifact.

Neighbor information is used to calculate contextual values such as:

- Average neighboring compliance
- Average neighboring violation count
- Average neighboring environmental breach rate
- Average neighboring corrective-action delay

This provides another way to compare a mine with similar records in the dataset.

The relationship paths shown in the interface are part of the prototype and are not intended to describe official company, government, or reporting relationships.

---

## GIS Data

The original feature data does not contain verified mine-level coordinates. For that reason, the current backend creates stable display coordinates from the available state and row information.

These coordinates exist only so that the map can be demonstrated. They are **not official mine locations**.

---

## Technology

### Backend

- Python
- FastAPI
- Uvicorn
- Pandas
- NumPy
- scikit-learn
- XGBoost
- Joblib

### Frontend

- HTML
- CSS
- JavaScript
- Chart.js
- Leaflet

### Storage used by the MVP

- CSV feature dataset
- Serialized Joblib model

The current version does not depend on a database for its basic local workflow.

---

## Project Structure

```text
coalguard_ai_mvp/
│
├── app/
│   ├── main.py
│   └── static/
│       ├── index.html
│       ├── styles.css
│       ├── app.js
│       └── logo.svg
│
├── data/
│   ├── india_coal_mine_safety_data_source_grounded.csv
│   └── india_coal_mine_safety_data_source_notes.txt
│
├── model/
│   └── coalguard_ai_mvp_risk_model.pkl
│
├── .env.example
├── requirements.txt
└── README.md
```

---

## Getting Started

### Requirements

- Python 3.10 or newer is recommended.
- pip
- Git

### Clone the project

```bash
git clone https://github.com/JUNAID0990/coalguard_ai_mvp.git
cd coalguard_ai_mvp
```

### Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install packages

```bash
pip install -r requirements.txt
```

### Start the server

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

FastAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

## API

The backend provides the data used by the dashboard through REST endpoints.

A basic health check is available at:

```http
GET /api/health
```

The application also provides endpoints for summary information, mines, compliance, inspections, violations, corrective actions, risk results, graph/activity information, and audit data.

For the complete list and request/response schemas, run the project and visit `/docs`.

---

## Environment Variables

The repository includes an example configuration file:

```text
.env.example
```

It currently contains placeholders for:

```env
FIREBASE_PROJECT_ID=
GOOGLE_APPLICATION_CREDENTIALS=
```

These values are not needed for the basic local dashboard flow. They leave room for future cloud or Firebase integration.

Do not commit passwords, tokens, private keys, service-account files, or other credentials to the repository.

---

## Current Limitations

This is an MVP, so there are several things that still need work before a production deployment.

### Data quality

- Several mine-level fields are simulated.
- Some source information is available only at an aggregate level.
- Map coordinates are generated for demonstration.
- Relationships shown in the graph are not official organizational relationships.

### Model quality

- The training target is a synthetic proxy.
- The model has not been validated against verified historical mine outcomes.
- The displayed probabilities have not been calibrated for operational use.
- No claim should be made about production-level accuracy from this repository.

### Security

The current MVP does not include a complete authentication and authorization system. It should therefore not be exposed to sensitive operational data on a public network without additional security controls.

---

## Moving Toward Production

A production version would need verified mine-level data and a stronger operational foundation.

### Data

- Replace simulated fields with trusted records.
- Keep source and timestamp information for important values.
- Validate mine IDs, states, locations, and organizational mappings.
- Add automated schema and data-quality checks.

### Model

- Define a verified target from historical outcomes.
- Use time-aware train/test evaluation.
- Measure performance separately for each risk category.
- Calibrate probability outputs.
- Monitor model drift after deployment.
- Keep model versions and training metadata.

### Application

- Add authentication and role-based permissions.
- Store operational data in a suitable database.
- Add automated tests and CI/CD.
- Add structured logging and monitoring.
- Add proper production deployment configuration.
- Keep an auditable record of important changes and actions.

### Governance

A useful production rule is to keep three things separate:

```text
Observed information
        ↓
Calculated / inferred result
        ↓
Human decision
```

This makes it easier for a reviewer to understand what came directly from the source data and what was produced by the application.

---

## Development Flow

```text
Source Data
    ↓
Validation
    ↓
Feature Preparation
    ↓
Model Training / Evaluation
    ↓
Saved Model
    ↓
FastAPI
    ↓
Dashboard
    ↓
Review
    ↓
Corrective Action
```

---

## Project Status

**MVP / Prototype**

The current repository demonstrates the complete flow from a mine feature dataset and saved model to a working web dashboard with risk review, map visualization, similarity information, activity analysis, and API access.

---

## Intended Use

CoalGuard is currently useful for:

- Project demonstrations
- Research and experimentation
- Safety dashboard development
- Data and model workflow testing
- Governance interface design
- Exploring graph-based mine similarity
- Building a foundation for a larger mine safety platform

It is not a replacement for statutory inspections, emergency procedures, certified safety systems, regulatory decisions, or professional safety judgment.

---

## Author

**Junaid Khan**

GitHub: https://github.com/JUNAID0990

Project: https://github.com/JUNAID0990/coalguard_ai_mvp

---

## License

There is currently no `LICENSE` file in the repository. Until a license is added, permission to reuse or redistribute the project should not be assumed.

---

## In Short

CoalGuard brings several parts of a mine safety workflow together in one application:

```text
Mine Data
   ↓
Safety Signals
   ↓
Risk Review
   ↓
Supporting Context
   ↓
Recommended Action
   ↓
Audit / Follow-up
```

The current version is deliberately a prototype. The next major step is to replace the simulated fields with verified mine-level data and validate the risk workflow against real historical outcomes.
