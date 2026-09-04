# CoalGuard AI MVP

End-to-end prototype using the supplied CoalGuard risk-model `.pkl` artifact and the supplied CSV.

## Architecture

Browser UI → FastAPI → loaded PKL model + CSV → prediction / graph features → dashboard.

- **Model:** XGBoost (the supplied artifact selected XGBoost during the MVP notebook run).
- **Graph:** a k-nearest-neighbor similarity graph is reconstructed from the artifact's graph reference features. The UI also renders a governance relationship chain for demonstration.
- **Data:** the supplied dataset is used as the source of mine-level features.
- **Target:** the model was trained against a **synthetic proxy risk label**, because the supplied CSV has no verified risk target. Do not claim the displayed accuracy as real-world predictive performance.

## Run

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

## Project layout

```text
coalguard_ai_mvp/
  app/
    main.py
    static/
      index.html
      styles.css
      app.js
  data/
    india_coal_mine_safety_data_source_grounded.csv
    india_coal_mine_safety_data_source_notes.txt
  model/
    coalguard_ai_mvp_risk_model.pkl
  requirements.txt
  .env.example
```

## MVP features

- Executive command dashboard
- Mine registry
- GIS map
- CoalGuard relationship graph
- PKL-backed risk predictions
- Prediction probabilities
- Top risk factors
- Compliance / violation / action signal cards
- Responsive tablet/mobile layout
- Health endpoint
- Clear synthetic-data / prototype disclaimer


