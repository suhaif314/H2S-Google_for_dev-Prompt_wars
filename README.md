# 🚨 TriageAI — AI-Powered Emergency Response Triage System

> **Transform chaotic emergency reports into structured, life-saving action plans in seconds.**

TriageAI is a multimodal AI system that accepts messy, unstructured emergency inputs — voice recordings, text descriptions, and PDF documents — and converts them into structured, validated triage reports with severity scoring, resource allocation, and actionable response plans using **Google Gemini 2.5 Flash** on **Vertex AI**.

---

## 🎯 Problem Statement

In emergency situations, critical information arrives in chaotic, unstructured formats:
- **Panicked voice calls** with fragmented, emotional descriptions
- **Messy text messages** with typos and incomplete details
- **Scanned documents** like medical records or incident reports

First responders and dispatchers must rapidly parse this chaos into actionable decisions. **Every second counts.** TriageAI bridges the gap between raw human communication and structured emergency response.

---

## 🏥 Selected Vertical: **Healthcare + Disaster Response**

TriageAI operates at the intersection of healthcare and disaster response, where the need for rapid, accurate triage is most critical. The system is designed for:
- Emergency dispatch centers
- First responder coordination
- Disaster response command centers
- Hospital intake triage

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Web App)                        │
│          HTML/CSS/JS with glassmorphism UI                   │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │  Voice   │  │   PDF    │  │   Text   │                  │
│  │  Input   │  │  Upload  │  │   Input  │                  │
│  └────┬─────┘  └────┬─────┘  └─────┬────┘                  │
│       └──────────────┴──────────────┘                       │
└──────────────────────────┼───────────────────────────────────┘
                           │ REST API
┌──────────────────────────┼───────────────────────────────────┐
│              BACKEND (FastAPI)                               │
│                          │                                   │
│  ┌───────────────────────▼────────────────────────────┐      │
│  │              Input Router / Preprocessor            │      │
│  └───────────┬──────────┬─────────────────────────────┘      │
│              │          │                                    │
│  ┌───────────▼──┐  ┌────▼────────┐                          │
│  │ Speech-to-   │  │ Document    │                          │
│  │ Text API     │  │ Parser      │                          │
│  └───────────┬──┘  └──┬──────────┘                          │
│              └─────────┘                                     │
│                   │                                          │
│  ┌────────────────┼──────────────────────────────────┐       │
│  │     CONTEXT ENRICHMENT                            │       │
│  │  ┌──────────┐  ┌──────────┐                       │       │
│  │  │ Weather  │  │ News     │                       │       │
│  │  │ API      │  │ API      │                       │       │
│  │  └──────────┘  └──────────┘                       │       │
│  └────────────────┬──────────────────────────────────┘       │
│                   │                                          │
│  ┌────────────────▼──────────────────────────────────┐       │
│  │         GEMINI 2.5 FLASH (Vertex AI)              │       │
│  │  Intent → Entity → Severity → Actions → Resources│       │
│  └────────────────┬──────────────────────────────────┘       │
│                   │ Structured JSON                          │
└───────────────────┼──────────────────────────────────────────┘
                    ▼
           Structured Triage Report
```

### Google Cloud Services Used

| Service | Purpose |
|---|---|
| **Vertex AI (Gemini 2.5 Flash)** | Core AI engine — multimodal understanding, triage logic, structured output |
| **Cloud Speech-to-Text** | Convert voice recordings to text with emergency vocabulary boosting |
| **Cloud Run** | Serverless deployment of FastAPI backend |
| **Cloud Storage** | Store uploaded files (audio, PDFs) |
| **Cloud Firestore** | Persistent storage for triage reports and audit trail |
| **Google Maps API** | Find nearest hospitals and emergency facilities |

### External APIs
| API | Purpose |
|---|---|
| **OpenWeatherMap** | Real-time weather data for disaster context assessment |
| **NewsAPI** | Recent news alerts for situational awareness |

---

## ⚡ How It Works

1. **Input** — User provides emergency information via:
   - 📝 **Text**: Type or paste a description
   - 🎙️ **Voice**: Record audio directly in the browser
   - 📄 **Document**: Upload PDF files (medical records, reports)

2. **Processing** — The backend:
   - Routes input to appropriate processors (Speech-to-Text, PDF parser)
   - Fetches real-time **weather data** for the location
   - Fetches **recent news** for situational awareness
   - Combines all context into a comprehensive prompt

3. **AI Analysis** — Gemini 2.5 Flash analyzes everything holistically:
   - Extracts structured entities (who, what, where)
   - Assesses severity (1-5 scale with justification)
   - Generates prioritized action plans
   - Recommends resource allocation
   - Suggests appropriate medical facilities

4. **Output** — A structured triage report with:
   - 🔴 Severity score with justification
   - 📋 Incident summary and type classification
   - 🔍 Extracted details (location, injuries, hazards)
   - 🚨 Prioritized immediate actions with responsible parties
   - 🚑 Resource requirements (ambulances, fire trucks, police)
   - 🏥 Recommended facility type
   - 🌤️ Weather impact assessment
   - 📰 Related news context

---

## 📁 Project Structure

```
├── frontend/                    # Web-based UI
│   ├── index.html               # Main HTML page
│   ├── css/styles.css           # Glassmorphism dark theme
│   └── js/
│       ├── app.js               # Main application logic
│       ├── recorder.js          # Voice recording (MediaRecorder API)
│       ├── fileHandler.js       # PDF upload with drag-and-drop
│       └── api.js               # Backend API communication
│
├── backend/                     # FastAPI backend
│   ├── main.py                  # API routes and orchestration
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile               # Cloud Run deployment
│   ├── services/                # Service layer
│   │   ├── gemini_service.py    # Vertex AI Gemini integration
│   │   ├── speech_service.py    # Cloud Speech-to-Text
│   │   ├── document_service.py  # PDF text extraction
│   │   ├── weather_service.py   # OpenWeatherMap API
│   │   ├── news_service.py      # NewsAPI integration
│   │   └── maps_service.py      # Google Maps API
│   ├── prompts/
│   │   └── triage_prompt.py     # Engineered prompt templates
│   ├── models/                  # Pydantic data models
│   │   ├── input_models.py      # Request validation
│   │   └── output_models.py     # Structured report schema
│   ├── utils/
│   │   ├── validators.py        # Input sanitization
│   │   └── logger.py            # Structured logging
│   └── config/
│       └── settings.py          # Environment configuration
│
├── tests/                       # Test suite
│   ├── test_input_validation.py # Input validation tests
│   └── test_api_endpoints.py    # API endpoint tests
│
├── .env.example                 # Environment variable template
├── .gitignore
└── README.md
```

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.11+
- Google Cloud account with billing enabled
- GCP project with Vertex AI API enabled

### 1. Clone & Setup
```bash
git clone <repository-url>
cd H2S-Google_for_dev-Prompt_wars

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Google Cloud Setup
```bash
# Install gcloud CLI (if not installed)
# https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable \
  aiplatform.googleapis.com \
  speech.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  run.googleapis.com
```

### 3. Configure Environment
```bash
# Copy example env
cp .env.example .env

# Edit .env with your values:
# GOOGLE_CLOUD_PROJECT=your-project-id
# OPENWEATHER_API_KEY=your-key (optional)
# NEWS_API_KEY=your-key (optional)
```

### 4. Run Locally
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Open **http://localhost:8000** in your browser.

### 5. Deploy to Cloud Run (Optional)
```bash
gcloud run deploy triageai \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_input_validation.py -v
```

---

## 🔐 Security & Best Practices

| Aspect | Implementation |
|---|---|
| **API Key Protection** | All keys stored in `.env`, never committed to git |
| **Input Sanitization** | Text sanitized for null bytes, excessive whitespace |
| **File Validation** | Strict type + size checks for audio and PDF uploads |
| **Rate Limiting** | Can be added via FastAPI middleware for production |
| **CORS** | Configured for allowed origins |
| **AI Safety** | Disclaimer that AI outputs are recommendations only |
| **Responsible AI** | Never provides medical diagnosis — triage-level only |

---

## ⚡ Performance & Cost Optimization

- **Gemini 2.5 Flash**: Fastest Gemini model, optimized for speed + cost
- **Structured JSON output**: `response_mime_type="application/json"` for reliable parsing
- **Low temperature (0.2)**: Consistent, deterministic outputs
- **Lazy initialization**: Services initialized only when first used
- **Context truncation**: Large PDFs truncated to prevent token overflow
- **Async processing**: All I/O operations are async for concurrent handling

---

## 📊 Evaluation Alignment

| Criterion | How TriageAI Satisfies It |
|---|---|
| **Code Quality** | Clean architecture, Pydantic models, typed Python, modular services |
| **Security** | Input sanitization, file validation, API key protection |
| **Efficiency** | Gemini 2.5 Flash, async I/O, lazy init, structured JSON mode |
| **Testing** | Pytest suite covering validators, API endpoints, edge cases |
| **Accessibility** | Semantic HTML, ARIA labels, keyboard navigation, responsive |
| **Google Services** | 6+ GCP services deeply integrated |
| **Real-world Usability** | Directly applicable to emergency dispatch |
| **Context-aware AI** | Weather + news enrichment for holistic assessment |
| **Decision Making** | Severity scoring, resource allocation, facility routing |

---

## ⚠️ Assumptions

- Users have a stable internet connection for Gemini API calls
- Audio recordings are in supported formats (WebM, WAV, MP3)
- PDF documents contain extractable text (not scanned images)
- Weather and news APIs are optional — app works without them
- AI outputs are recommendations for trained professionals, not autonomous decisions

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3 (glassmorphism), Vanilla JavaScript
- **Backend**: Python 3.13, FastAPI, Pydantic
- **AI**: Google Gemini 2.5 Flash via Vertex AI
- **Cloud**: Google Cloud Platform (Vertex AI, Speech-to-Text, Cloud Run)
- **APIs**: OpenWeatherMap, NewsAPI

---

## 📄 License

Built for the PromptWars Hackathon by H2S team.
