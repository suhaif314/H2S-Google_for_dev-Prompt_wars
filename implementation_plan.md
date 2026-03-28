# 🚀 TriageAI — Updated Implementation Plan

## Changes from v1
- ❌ Removed image/photo upload and Vision API
- ✅ Added **Weather API** integration (real-time weather context for disaster assessment)
- ✅ Added **News API** integration (recent news/alerts for situational awareness)
- ✅ Using **full GCP with Vertex AI** (user has GCP credits)

---

## 🏗️ Updated Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Web App)                        │
│          HTML/CSS/JS with modern glassmorphism UI            │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │  Voice   │  │   PDF    │  │   Text   │                  │
│  │  Input   │  │  Upload  │  │   Input  │                  │
│  └────┬─────┘  └────┬─────┘  └─────┬────┘                  │
│       └──────────────┴──────────────┘                       │
│                          │                                   │
└──────────────────────────┼───────────────────────────────────┘
                           │ REST API
┌──────────────────────────┼───────────────────────────────────┐
│              BACKEND (FastAPI on Cloud Run)                   │
│                          │                                   │
│  ┌───────────────────────▼────────────────────────────┐      │
│  │              Input Router / Preprocessor            │      │
│  │   • Detects input type (audio/pdf/text)            │      │
│  │   • Validates & sanitizes input                     │      │
│  └───────────┬──────────┬─────────────────────────────┘      │
│              │          │                                    │
│  ┌───────────▼──┐  ┌────▼────────┐                          │
│  │ Speech-to-   │  │ Document    │                          │
│  │ Text API     │  │ AI Parser   │                          │
│  │ (voice→text) │  │ (pdf→text)  │                          │
│  └───────────┬──┘  └──┬──────────┘                          │
│              └─────────┘                                     │
│                   │ Combined text context                    │
│                   │                                          │
│  ┌────────────────┼──────────────────────────────────┐       │
│  │     CONTEXT ENRICHMENT LAYER                      │       │
│  │                │                                  │       │
│  │  ┌─────────────▼──┐  ┌─────────────────┐         │       │
│  │  │  Weather API   │  │   News API      │         │       │
│  │  │  (real-time    │  │   (recent       │         │       │
│  │  │   conditions)  │  │    alerts/news) │         │       │
│  │  └───────┬────────┘  └────────┬────────┘         │       │
│  │          └────────────────────┘                   │       │
│  └────────────────┬──────────────────────────────────┘       │
│                   │ Enriched context                         │
│  ┌────────────────▼──────────────────────────────────┐       │
│  │           GEMINI AI ENGINE (Vertex AI)             │       │
│  │                                                    │       │
│  │  1. Intent Extraction    → What happened?          │       │
│  │  2. Entity Extraction    → Who, Where, What?       │       │
│  │  3. Weather Context      → How does weather impact?│       │
│  │  4. News Context         → Related incidents?      │       │
│  │  5. Severity Assessment  → How critical? (1-5)     │       │
│  │  6. Action Generation    → What to do next?        │       │
│  │  7. Resource Allocation  → What resources needed?  │       │
│  └──────────────────────┬────────────────────────────┘       │
│                         │ Structured JSON                    │
│  ┌──────────────────────▼────────────────────────────┐       │
│  │              Response Builder                      │       │
│  │  • Validates AI output against schema              │       │
│  │  • Enriches with Maps data (nearest hospital)      │       │
│  │  • Stores in Firestore for audit trail             │       │
│  └──────────────────────┬────────────────────────────┘       │
│                         │                                    │
└─────────────────────────┼────────────────────────────────────┘
                          │
              ┌───────────▼───────────┐
              │      STORAGE LAYER    │
              │  • Firestore (reports)│
              │  • Cloud Storage      │
              │    (uploaded files)   │
              └───────────────────────┘
```

### GCP Services Used

| Service | Purpose |
|---|---|
| **Vertex AI (Gemini 2.0 Flash)** | Core AI — multimodal understanding, triage logic |
| **Cloud Run** | Host the FastAPI backend |
| **Cloud Speech-to-Text** | Convert voice recordings to text |
| **Cloud Firestore** | Store triage reports, audit trail |
| **Cloud Storage** | Store uploaded files (PDFs, audio) |
| **Google Maps API** | Find nearest hospitals/emergency services |

### External APIs

| API | Purpose |
|---|---|
| **OpenWeatherMap API** | Real-time weather data for disaster context |
| **NewsAPI / Google News** | Recent news alerts for situational awareness |

---

## 📁 Updated Project Structure

```
H2S-Google_for_dev-Prompt_wars/
│
├── frontend/
│   ├── index.html
│   ├── css/styles.css
│   ├── js/
│   │   ├── app.js
│   │   ├── recorder.js
│   │   ├── fileHandler.js
│   │   └── api.js
│   └── assets/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_service.py
│   │   ├── speech_service.py
│   │   ├── document_service.py
│   │   ├── weather_service.py    # NEW: Weather API
│   │   ├── news_service.py       # NEW: News API
│   │   └── maps_service.py
│   │
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── triage_prompt.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── input_models.py
│   │   └── output_models.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py
│   │   └── logger.py
│   │
│   └── config/
│       ├── __init__.py
│       └── settings.py
│
├── tests/
│   ├── test_gemini_service.py
│   ├── test_input_validation.py
│   └── test_api_endpoints.py
│
├── .env.example
├── .gitignore
├── README.md
└── cloudbuild.yaml
```

---

## ⚙️ Phase-by-Phase Execution

### Phase 1: GCP Console Setup (Step-by-step guide)
1. Go to Google Cloud Console
2. Create/select project
3. Enable required APIs
4. Set up authentication (ADC)
5. Create Firestore database
6. Create Cloud Storage bucket

### Phase 2: Project Foundation
1. Create folder structure
2. Set up Python virtual environment
3. Install dependencies
4. Configure environment variables
5. Basic FastAPI app with health check

### Phase 3: Core AI Pipeline
1. Gemini service with triage prompt
2. Speech-to-Text service
3. Document parser service
4. Weather enrichment service
5. News enrichment service

### Phase 4: Frontend
1. Modern glassmorphism UI
2. Voice recorder
3. PDF upload
4. Text input
5. Results display

### Phase 5: Integration & Polish
1. Firestore storage
2. Maps integration
3. Testing
4. README
5. Deployment to Cloud Run
