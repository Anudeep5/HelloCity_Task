# HelloCity Engineering Exercise

AI-Powered Onboarding (Miami City Guide)

## Live Demo URL

`https://hello-city-task.vercel.app/`

---

# Overview

This project implements a **mobile-first AI onboarding experience** for HelloCity.

The assistant learns what a user enjoys doing in Miami by collecting **exactly three interests** through a conversational interface.

For every detected interest the system:

1. Extracts interests from natural language
2. Deduplicates and validates them
3. Fetches **real Miami venues** using Google Places
4. Shows examples for confirmation
5. Moves forward regardless of Yes/No
6. Stops after **three interests** and returns a structured user profile

The backend controls the full onboarding flow.

The LLM is used **only for reasoning and language understanding**.

---

# Tech Stack

## Frontend

- React (Vite)
- TypeScript
- Custom CSS styled to match HelloCity branding
- Mobile-first responsive layout
- Session ID stored in `sessionStorage` (resets when tab is closed)

## Backend

- FastAPI (Python)
- Gemini 2.5 Flash (Google GenAI SDK)
- Google Places API (venue discovery)
- In-memory session store (Redis-ready)

---

# LLM Details

Model

**Gemini 2.5 Flash**

SDK

**google-genai**

Gemini is responsible for:

- Extracting interest categories from natural language
- Generating conversational responses

Gemini **does not control application logic** .

All deterministic logic is handled server-side:

- onboarding flow
- interest limits
- deduplication
- session state
- venue lookup

This keeps the system predictable and reliable.

---

# Architecture Overview

## Conversation Flow

Frontend sends:

```json
{
    "session_id": "abc123",
    "message": "I like beaches and coffee shops"
}
```

Backend pipline:

- Gemini extracts structured interests
- Backend deduplicates interests
- Multiple interests per message are allowed
- First interest is shown immediately
- Remaining interests are queued
- Examples fetched from Google Places
- User confirms with Yes/No
- System automatically advances to the next queued interest
- Stops after exactly three interests

---

# Interest Extraction Strategy

Gemini returns strict JSON:

```json
{
    "interests": ["Beaches", "Coffee shops"]
}
```

Rules enforced by the prompt:

- Return **broad activity categories**
- Maximum **3 interests**
- No explanations
- Strict JSON output

Backend validation ensures:

- safe JSON parsing
- duplicate filtering
- max interest enforcement

---

# Venue Discovery (Google Places API)

Venue validation uses **Google Places Text Search** .

For each interest:

1. Build query
    ```
    "{interest} in Miami"
    ```
2. Call Google Places API
3. Return top three venues

Each venue card includes:

- Name
- Address
- Rating
- Review count
- Google Maps link

Example card data:

```
South Pointe Park
1 Washington Ave, Miami Beach
⭐ 4.8 (12k reviews)
```

Clicking a card opens the **exact Google Maps place page** using the place ID.

---

# Multi-Interest Handling

Users often mention multiple activities in a single message.

Example:

```
"I like beaches and coffee shops"
```

System behavior:

```
Interest 2 → Coffee shops
```

Flow:

1. Beaches shown first
2. User confirms Yes/No
3. Coffee shops shown next automatically

This ensures no interests are lost while maintaining a clean UX.

---

# Session State Management

Current implementation uses in-memory storage:

```python
{
  session_id: {
    interests: [],
    pending_interests: [],
    history: [],
    last_interest: None,
    last_examples: None
  }
}
```

Features:

- duplicate prevention
- queued interests
- deterministic onboarding flow
- auto-advance after feedback
- exactly three interests enforced

Sessions reset when:

- the browser tab closes
- backend restarts

The store is designed to be easily replaced by Redis.

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

Behavior

- Advances queued interests automatically
- Returns next venue examples if available
- Returns profile when onboarding completes

---

# UI Design

The UI is styled to reflect HelloCity branding.

Features:

- HelloCity yellow accent
- black venue cards
- white background
- iOS-style pill buttons
- soft yellow assistant chat bubbles
- light gray user bubbles
- sticky chat input bar
- smooth mobile scrolling

Layout optimized for mobile devices.

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
GOOGLE_PLACES_API_KEY=your_key
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
GOOGLE_PLACES_API_KEY=your_key
ALLOWED_ORIGINS=https://hello-city-task.vercel.app
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

- Origins must match exactly
- No trailing slashes
- Include correct Vercel domain

---

# Edge Cases Handled

- multiple interests in one message
- duplicate interest prevention
- strict three-interest limit
- invalid JSON from LLM
- graceful API failure handling
- Google Places downtime handling
- session isolation per user
- CORS preflight handling

---

# Design Decisions

Key design principles:

**Backend-controlled flow**

The onboarding progression is deterministic and never controlled by the LLM.

**LLM used only for reasoning**

Gemini performs:

- language understanding
- interest extraction
- conversational phrasing

**Google Places chosen for accuracy**

Compared to open datasets, Google Places provides:

- higher venue coverage
- better ranking
- more reliable geolocation

**Session storage designed for scalability**

Current in-memory store can easily migrate to Redis.

---

# Future Improvements

Potential enhancements:

- Redis session store
- Places API caching
- venue photos
- open hours
- distance ranking
- smarter interest taxonomy
- analytics
- rate limiting
- monitoring and logging

---

# Final Result

The system successfully:

- collects exactly three interests
- validates them using real Miami venues
- handles multi-interest messages
- auto-advances through confirmations
- maintains backend session state
- prevents duplicates
- returns a structured profile
- matches HelloCity branding
- deploys easily on modern cloud platforms

---
