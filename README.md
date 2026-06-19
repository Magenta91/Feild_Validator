# Xeno Transaction Validator

A modular monolith web platform for transaction data validation and processing.

## Architecture

**Pattern:** Modular Monolith with Base + Worker classes  
**Backend:** FastAPI (Python)  
**Frontend:** Streamlit  
**Backend Hosting:** Render.com  
**Frontend Hosting:** Streamlit Cloud  

```
xeno-validator/
├── backend/
│   ├── main.py                  # FastAPI routes + orchestration
│   ├── base/
│   │   ├── base_validator.py    # Abstract base for validators
│   │   ├── base_processor.py    # Abstract base for processors
│   │   └── base_ingestion.py    # Abstract base for ingestion
│   ├── workers/
│   │   ├── ingestion_worker.py  # CSV parsing
│   │   ├── phone_worker.py      # Phone number validation
│   │   ├── date_worker.py       # Date/time validation
│   │   ├── integrity_worker.py  # Null, duplicate, format checks
│   │   ├── cleaner_worker.py    # Clean and tag rows
│   │   └── splitter_worker.py   # Split large CSVs
│   ├── models/
│   │   ├── validation_result.py # ValidationResult dataclass
│   │   └── request_models.py    # Pydantic models
│   └── config/
│       └── country_codes.py     # Phone rules per country
└── frontend/
    ├── app.py                   # Streamlit UI
    └── .streamlit/secrets.toml  # API URL config
```

---

## Local Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
API docs available at: http://localhost:8000/docs

### Frontend
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

---

## Deploy to Render (Backend)

1. Push this repo to GitHub
2. Go to render.com → New → Web Service
3. Connect your GitHub repo
4. Set Root Directory to `backend`
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Click Deploy
8. Copy your Render URL (e.g. `https://xeno-validator.onrender.com`)

---

## Deploy to Streamlit Cloud (Frontend)

1. Go to share.streamlit.io
2. Connect your GitHub repo
3. Set Main file path to `frontend/app.py`
4. Go to Advanced Settings → Secrets
5. Add: `API_URL = "https://your-render-url.onrender.com"`
6. Click Deploy

---

## Validation Features

| Feature | Details |
|---|---|
| Phone Validation | Country-specific rules (IN: 10 digits, SG: 8 digits, etc.) |
| Date Validation | Tries all supported formats, standardises to YYYY-MM-DD |
| Null Checks | Flags empty critical fields |
| Duplicate Detection | Flags duplicate order IDs |
| Payment Mode | Validates against allowed modes |
| Numeric Checks | Flags negative or non-numeric amounts |
| Email Format | Basic @ and domain check |
| CSV Splitting | Splits output into configurable chunk sizes |

---

## Approach & Tradeoffs

**What I built:** Modular monolith with abstract base classes and polymorphic worker pattern.  
**What I chose not to build:** True microservices (4 separate deployments would cause cold-start latency on free tier) and a database layer (stateless processing is sufficient for this use case).  
**Key tradeoff:** Simplicity of single deployment vs. independent scalability of each validation module. The modular design means splitting into microservices later requires no refactoring — just separating the workers into their own FastAPI apps.
