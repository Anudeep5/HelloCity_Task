# HelloCity Engineering Exercise

AI-Powered Onboarding (Miami City Guide)

## Live Demo URL

`https://hello-city-task.vercel.app/`

---

# Overview

This project implements a mobile-first AI onboarding experience for HelloCity.

The assistant collects exactly **three interests** about what a user enjoys doing in Miami. After each detected interest, the system:

1. Validates the interest
2. Fetches three real Miami venues
3. Asks the user to confirm
4. Moves forward regardless of confirmation
5. Stops after three interests and returns a structured profile

The backend fully controls progression logic and session state.
The LLM is used only for reasoning and structured extraction.

---

# Tech Stack

## Frontend

* React (Vite)
* TypeScript
* Custom CSS styled to match HelloCity branding
* Mobile-first responsive layout
* Session ID stored in `sessionStorage` (resets when tab is closed)

## Backend

* FastAPI (Python)
* Gemini 2.5 Flash (Google GenAI SDK)
* OpenStreetMap + Overpass API for venue discovery
* In-memory session storage (designed for easy Redis upgrade)

---

# LLM Details

Model: **Gemini 2.5 Flash**
SDK: **google-genai**

Gemini is used for:

* Extracting structured interest categories from natural language
* Generating short conversational responses

Gemini is not responsible for:

* Tracking progress
* Enforcing three interests
* Deduplication
* Session management

All deterministic logic is handled server-side.

---

# Architecture Overview

## Conversation Flow

Frontend sends:

```json
{
  "session_id": "abc123",
  "message": "I love Beaches"
}
```

Backend:

* Calls Gemini to extract structured interests
* Deduplicates interests
* Adds at most one new interest per message
* Fetches three real venues using Overpass
* Returns structured response
* Stops after exactly three interests

---

## Clear Separation of Responsibilities

### LLM Responsibilities

* Understand user input
* Extract interest categories
* Produce friendly tone

### Backend Responsibilities

* Maintain session state
* Prevent duplicate interests
* Enforce maximum of three interests
* Control onboarding progression
* Fetch venues from Overpass
* Construct final profile object

This ensures predictable behavior and prevents LLM-driven flow errors.

---

# Interest Extraction Strategy

Gemini is prompted to return strict JSON:

```json
{
  "interests": ["Beaches"]
}
```

Rules:

* Broad activity categories only
* Maximum three
* JSON only
* Backend validates output before use

If JSON parsing fails, fallback logic is triggered.

---

# Venue Validation (OpenStreetMap + Overpass)

Instead of Google Places, this implementation uses:

* OpenStreetMap data
* Overpass API

For each interest:

* Construct an Overpass query
* Search within Miami bounding box
* Filter relevant OSM tags
* Return top three matches

Each example includes:

* Name
* Address (when available)
* Map link

Regardless of Yes/No confirmation, the interest counts and flow continues.

---

# Session State Management

Current implementation uses in-memory storage:

```python
sessions = {
  session_id: {
    interests: [],
    history: [],
    last_interest: None,
    last_examples: None
  }
}
```

Behavior:

* Prevents duplicates
* Adds at most one interest per message
* Stops at exactly three
* Session resets when browser tab is closed
* Backend restart clears all sessions

Designed to be easily replaced with Redis.

---

# API Endpoints

## POST /api/chat

Request:

```json
{
  "session_id": "string",
  "message": "string"
}
```

Response:

```json
{
  "assistant_message": "string",
  "interests": ["..."],
  "interest_detected": true,
  "interest_added": "string",
  "examples": [...],
  "onboarding_complete": false,
  "profile": null
}
```

---

## POST /api/feedback

Request:

```json
{
  "session_id": "string",
  "interest": "string",
  "choice": "yes" | "no"
}
```

Returns updated assistant message and onboarding state.

---

# UI Design

The UI is styled to match HelloCity branding:

* HelloCity Yellow accent
* Black venue cards
* Clean white background
* iOS-style rounded pill buttons
* Light gray user bubbles
* Soft yellow assistant bubbles
* Smooth mobile scrolling

Designed mobile-first and responsive.

---

# Local Setup

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Create `.env`:

```
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-2.5-flash
ALLOWED_ORIGINS=http://localhost:5173
```

---

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Create `.env`:

```
VITE_API_BASE_URL=http://localhost:8000
```

---

# Deployment Guide

## Backend Deployment (Render)

1. Create a Web Service on Render
2. Set Root Directory to `backend`
3. Build Command:

```
pip install -r requirements.txt
```

4. Start Command:

```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. Set environment variables:

```
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-2.5-flash
ALLOWED_ORIGINS=https://your-vercel-domain.vercel.app
```

Verify health:

```
https://your-render-service.onrender.com/health
```

---

## Frontend Deployment (Vercel)

1. Import repo into Vercel
2. Set Root Directory to `frontend`
3. Build Command:

```
npm run build
```

4. Output Directory:

```
dist
```

5. Set environment variable:

```
VITE_API_BASE_URL=https://your-render-service.onrender.com
```

Redeploy after configuration.

---

# CORS Configuration

FastAPI CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Important:

* Origins must match exactly
* No trailing slashes
* Include correct Vercel domain

---

# Edge Cases Handled

* Duplicate interests prevented
* Strict three interest limit
* JSON parsing fallback
* Graceful API failure handling
* Session isolation per user
* Preflight CORS handling
* Overpass timeout handling

---

# Design Decisions

* Backend controls progression logic
* LLM used only for reasoning
* OpenStreetMap chosen for open data
* In-memory state sufficient for demo
* Deterministic onboarding flow
* Clean separation of concerns

---

# Future Improvements

* Redis for persistent sessions
* Caching Overpass responses
* Smarter interest taxonomy normalization
* Venue image enrichment
* Analytics
* Rate limiting
* Structured logging
* Monitoring and observability

---

# Final Result

The system:

* Collects exactly three interests
* Validates each using real Miami venues
* Maintains backend session state
* Prevents duplicates
* Returns structured profile
* Matches HelloCity branding
* Fully deployable on modern cloud platforms

---