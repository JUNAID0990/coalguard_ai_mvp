# CoalGuard

> A practical dashboard for coal mine safety, compliance, inspections, incidents, and risk review.

CoalGuard is an MVP for bringing different mine-safety details into one dashboard. It uses a FastAPI backend with a browser-based interface, a saved risk model, mine feature data, a map, and a few views for investigating what is happening around a mine.

This is still a prototype. Some mine-level values in the included dataset are simulated for development and demonstration. They are not official mine records and should not be used for real safety decisions.

## Overview

The idea behind CoalGuard is fairly simple: put the available mine information in one place, make problems easier to spot, and give reviewers a way to move from a signal to a possible follow-up action.

The dashboard currently includes:

- Mine records and risk status
- Compliance information
- Inspection activity
- Violations and repeat violations
- Corrective actions
- Incident and environmental signals
- Contractor-related activity
- Interactive mine map
- Mine similarity and relationship views
- Risk factors and supporting signals
- Activity and investigation views
- Audit-oriented information
- FastAPI API documentation

## How It Works

```text
                         CoalGuard Dashboard
                                  |
                                  v
                           FastAPI Backend
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
             Mine Feature Data             Risk Model
                    |                           |
                    +-------------+-------------+
                                  |
                                  v
                         Risk & Activity Results
                                  |
                    +-------------+-------------+
                    |             |             |
                    v             v             v
                  Risk           Map          Reports
                    |
                    v
              Review & Action
```

When the application starts, the backend loads the supplied dataset and saved model. It prepares the feature data, builds the similarity information used by the graph views, and sends the resulting information to the browser through JSON endpoints.

## Main Sections

### Dashboard

The main dashboard gives a quick view of the mine dataset, risk categories, compliance figures, open violations, overdue actions, and other indicators.

### Mines

The mine registry contains basic mine information, location data, compliance values, violations, overdue actions, and the current model result.

### GIS Map

An interactive Leaflet map displays the mine records geographically.

### CoalGuard Graph

This view connects records using selected feature information. It is useful for looking at similarities and patterns between mines. It is not meant to show an official company or reporting structure.

### Compliance

Shows compliance rates, open violations, and critical compliance gaps across the available records.

### Inspections

Provides inspection counts, missed inspections, completion rates, observation activity, and time since the last inspection.

### Violations

Collects open, overdue, high-severity, critical, repeat, and growing violation signals in one place.

### Corrective Actions

Tracks action counts, overdue actions, completion, delays, on-time rates, and pending verification.

### Risk Intelligence

Shows the model result along with probabilities and selected signals that can help explain why a record needs attention.

### Audit Trail

Provides a place to review governance-related information and action history within the prototype.

## Risk Model

The repository contains the saved model here:

```text
model/coalguard_ai_mvp_risk_model.pkl
```

The current model artifact uses XGBoost. The application reads the saved metadata, preprocessing information, feature list, class labels, and graph reference columns from the artifact.

The application currently works with four risk categories:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

The probabilities shown in the dashboard come from the saved model. The extra numeric risk score is mainly used by the interface to represent the categories. It should not be treated as a calibrated safety score.

## Data

The included dataset is:

```text
data/india_coal_mine_safety_data_source_grounded.csv
```

The accompanying notes describe the dataset as being based on information from the Coal Directory of India 2024–25. It contains 393 records covering 373 operational coal mines and 20 operational lignite mines, with 47 columns.

The source material does not provide every mine-level field needed by this prototype. As a result, several fields related to safety observations, inspections, violations, incidents, environmental conditions, corrective actions, zones, and contractors are simulated.

More information is available in:

```text
data/india_coal_mine_safety_data_source_notes.txt
```

### Important note about the target

The supplied data does not contain a verified mine-level risk outcome. For the MVP, the model therefore uses a synthetic proxy target.

The model results in this repository are development results. They are not evidence of real-world predictive performance.

## Activity Review

CoalGuard also turns several feature values into activity records so a reviewer can see which signals may be drawing attention to a mine.

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

For selected records, the activity view can show repeated activity, unusual patterns, contributing signals, evidence text, relationships between events, and a suggested next action.

These details are generated from the prototype fields and should be treated as supporting context, not verified findings.

## Graph / Similarity Layer

The backend rebuilds a k-nearest-neighbor graph from the graph reference features stored in the model artifact.

The neighboring records are used to calculate contextual values such as:

- Average neighboring compliance
- Average neighboring violation count
- Average neighboring environmental breach rate
- Average neighboring corrective-action delay

This gives the dashboard another way to compare a mine with similar records in the dataset.

The relationship paths shown in the interface are part of the prototype. They do not represent official company, government, or reporting relationships.

## GIS Data

The original feature data does not contain verified mine-level coordinates. Because of that, the current backend creates stable display coordinates from the available state and row information.

These coordinates are only there to make the map usable for demonstration. They are **not official mine locations**.

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

The current version does not require a database for the basic local workflow.

## Project Structure

```text
coalguard_ai_mvp/
|
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

## Getting Started

### Requirements

- Python 3.10 or newer is recommended
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

## API

The backend provides the information used by the dashboard through REST endpoints.

A basic health check is available at:

```http
GET /api/health
```

There are also endpoints for summary information, mines, compliance, inspections, violations, corrective actions, risk results, graph/activity information, and audit data.

For the complete endpoint list and request/response schemas, run the project and open `/docs`.

## Environment Variables

The repository includes:

```text
.env.example
```

It currently contains placeholders for:

```env
FIREBASE_PROJECT_ID=
GOOGLE_APPLICATION_CREDENTIALS=
```

These values are not required for the basic local dashboard. They are kept for possible cloud or Firebase integration later.

Do not commit passwords, tokens, private keys, service-account files, or other credentials to the repository.

## Current Limitations

CoalGuard is an MVP, so there are still several areas that need work before it would be suitable for production.

### Data quality

- Several mine-level fields are simulated.
- Some source information is available only at an aggregate level.
- Map coordinates are generated for demonstration.
- Relationships shown in the graph are not official organizational relationships.

### Model quality

- The training target is a synthetic proxy.
- The model has not been validated against verified historical mine outcomes.
- The displayed probabilities have not been calibrated for operational use.
- No production-level accuracy claim should be made from this repository.

### Security

The current MVP does not include a complete authentication and authorization system. It should not be exposed to sensitive operational data on a public network without additional security controls.

## Moving Toward Production

A production version would need verified mine-level data as well as a stronger application and data foundation.

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
        |
        v
Calculated / inferred result
        |
        v
Human decision
```

Keeping these stages separate makes it easier for a reviewer to see what came directly from the source data and what was produced by the application.

## Development Flow

```text
Source Data
    |
    v
Validation
    |
    v
Feature Preparation
    |
    v
Model Training / Evaluation
    |
    v
Saved Model
    |
    v
FastAPI
    |
    v
Dashboard
    |
    v
Review
    |
    v
Corrective Action
```

## Project Status

**MVP / Prototype**

The repository currently demonstrates the flow from a mine feature dataset and saved model to a working web dashboard. It includes risk review, map visualization, similarity information, activity analysis, and API access.

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

## Author

**Junaid Khan**

GitHub: https://github.com/JUNAID0990

Project: https://github.com/JUNAID0990/coalguard_ai_mvp

## License

There is currently no `LICENSE` file in the repository. Until a license is added, permission to reuse or redistribute the project should not be assumed.

## In Short

CoalGuard brings several parts of a mine safety workflow into one application:

```text
Mine Data
   |
   v
Safety Signals
   |
   v
Risk Review
   |
   v
Supporting Context
   |
   v
Recommended Action
   |
   v
Audit / Follow-up
```

The current version is deliberately a prototype. The next major step is to replace the simulated fields with verified mine-level data and test the risk workflow against real historical outcomes.
