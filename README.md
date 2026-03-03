# HelloCity Engineering Exercise

AI-Powered Onboarding (Miami City Guide)

## Live Demo URL

  `https://hello-city-task.vercel.app/`

---

# Overview

This project implements a mobile-first AI onboarding experience for HelloCity.

The assistant collects exactly **3 user interests** about what they enjoy doing in Miami. After each detected interest, the system:

1. Validates the interest
2. Fetches 3 real Miami venues
3. Asks the user to confirm
4. Moves forward regardless of confirmation
5. Stops after 3 interests and returns a structured profile

The backend fully controls state and progression logic. The LLM is used strictly for reasoning and structured extraction.

---

# Tech Stack

## Frontend

* React (Vite)
* TypeScript
* Custom CSS styled to match HelloCity branding
* Mobile-first responsive design

## Backend

* FastAPI (Python)
* Gemini 2.5 Flash (Google GenAI SDK)
* OpenStreetMap + Overpass API for venue discovery
* In-memory session storage (designed for easy Redis upgrade)

---

# LLM Used

**Model:** Gemini 2.5 Flash
**SDK:** Google GenAI SDK

Gemini is used for:

* Extracting structured interest categories from user input
* Generating short, friendly conversational responses

Gemini is NOT used to manage state or progression logic.

---

# Architecture Overview

## 1. Conversation Flow

Frontend sends:

```json
{
  "session_id": "abc123",
  "message": "I love Beach"
}
```

Backend:

* Calls Gemini to extract structured interests
* Deduplicates interests
* Adds at most 1 new interest per message
* Fetches 3 real Miami venues using Overpass
* Returns structured response
* Stops after exactly 3 interests

---

## 2. Clear Separation of Responsibilities

### LLM Responsibilities

* Natural language understanding
* Structured JSON extraction
* Friendly assistant tone

### Backend Responsibilities

* Session state management
* Interest deduplication
* Enforcing exactly 3 interests
* Progression control
* Venue fetching via Overpass
* Final profile construction

The backend is deterministic. The LLM does not control onboarding progression.

---

# Interest Extraction Strategy

Gemini is prompted to return strict JSON:

```json
{
  "interests": ["Beach"]
}
```

Rules enforced:

* Broad activity categories
* Maximum 3 interests
* JSON-only output
* Backend validates and deduplicates

If parsing fails, the backend falls back safely.

---

# Venue Validation (OpenStreetMap + Overpass)

Instead of Google Places, this implementation uses:

* **OpenStreetMap data**
* **Overpass API**

For each interest:

* Construct Overpass query
* Search within Miami bounding box
* Filter by relevant OSM tags (e.g., `amenity=bar`, `amenity=cafe`, `tourism=gallery`)
* Return top 3 results

Each example includes:

* Name
* Address (when available)
* OSM ID
* Map link
* Latitude/Longitude

Regardless of user confirmation (Yes/No), the interest counts and the flow continues.

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

Features:

* Prevents duplicate interests
* Adds at most one new interest per message
* Stops at exactly 3 interests
* Easy to upgrade to Redis

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

Response:

* Advances conversation
* Returns updated state

---

# UI Design

The UI matches HelloCity branding:

* HelloCity Yellow accent
* Black venue cards
* Clean white base background
* iOS-style rounded pills
* Light gray user bubbles
* Soft yellow assistant bubbles
* Mobile-first layout
* Smooth scroll behavior

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

# Edge Cases Handled

* Duplicate interests prevented
* JSON parsing safety for Gemini output
* Graceful error handling
* At most one interest added per message
* Exactly 3 interests enforced
* Session isolation per user
* Mobile scroll handling

---

# Design Decisions

* Backend controls all progression logic
* LLM only used for reasoning
* Overpass API chosen for open, free geographic data
* Deterministic onboarding flow
* Clean separation of concerns

---

# Possible Improvements

If more time were available:

* Redis-based persistent session storage
* Caching Overpass responses
* Smarter OSM tag mapping per interest
* Add venue images via Wikimedia or additional APIs
* Add rate limiting
* Add production logging
* Add analytics on interest trends
* Improve taxonomy normalization

---

# Final Result

The system:

* Collects exactly 3 interests
* Validates each with real Miami venues via OSM
* Maintains backend session state
* Prevents duplicates
* Returns a structured profile
* Matches HelloCity brand style
* Is fully deployable
