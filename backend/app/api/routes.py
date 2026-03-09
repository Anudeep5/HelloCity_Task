from fastapi import APIRouter

from app.schemas.chat import (
    ChatRequest,
    FeedbackRequest,
    ChatResponse,
    PlaceCard,
    ResetRequest,
)
from app.core.config import settings
from app.core.storage import InMemoryStore
from app.services.gemini_service import GeminiService
from app.services.places_service import PlacesService

router = APIRouter()

store = InMemoryStore()
llm = GeminiService()
places = PlacesService(store.places_cache)


@router.get("/health")
def health():
    return {"ok": True}


@router.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session = store.get_session(req.session_id)

    # If already complete and nothing left queued, return profile immediately
    if len(session["interests"]) >= settings.MAX_INTERESTS and not (
        session.get("pending_interests") or []
    ):
        profile = {"interests": session["interests"][: settings.MAX_INTERESTS]}
        return ChatResponse(
            assistant_message="You’re all set. Here’s your profile.",
            interests=session["interests"],
            interest_detected=False,
            onboarding_complete=True,
            profile=profile,
        )

    # One Gemini call for both extraction + assistant reply
    analysis = await llm.analyze_message(
        user_text=req.message,
        existing_interests=session["interests"],
        max_interests=settings.MAX_INTERESTS,
    )

    extracted = analysis.get("interests", [])
    assistant_message = analysis.get(
        "assistant_reply", "Got it. What do you like doing around Miami?"
    )

    interest_detected = False
    interest_added = None
    examples_models: list[PlaceCard] = []

    remaining = settings.MAX_INTERESTS - len(session["interests"])
    added_interests: list[str] = []

    # Add as many as possible from this message
    for cand in extracted:
        if remaining <= 0:
            break

        added, canonical = store.add_interest_deduped(session, cand)
        if added and canonical:
            added_interests.append(canonical)
            remaining -= 1

    # Queue extras to show later via feedback flow
    session["pending_interests"] = (
        added_interests[1:] if len(added_interests) > 1 else []
    )

    if added_interests:
        interest_detected = True
        interest_added = added_interests[0]

    # Fetch examples only for the first interest we want to show now
    if interest_detected and interest_added:
        cache_key = store.normalize_interest(interest_added)
        try:
            ex = await places.get_examples(interest_added, cache_key)
            examples_models = [PlaceCard(**x) for x in (ex or [])]
            session["last_interest"] = interest_added
            session["last_examples"] = ex or []
        except Exception:
            # Never fail the endpoint because of places lookup
            session["last_interest"] = interest_added
            session["last_examples"] = []
            examples_models = []
    else:
        session["last_interest"] = None
        session["last_examples"] = []
        examples_models = []

    has_pending = bool(session.get("pending_interests"))
    has_examples = bool(examples_models)

    onboarding_complete = (
        len(session["interests"]) >= settings.MAX_INTERESTS
        and not has_pending
        and not has_examples
    )

    profile = (
        {"interests": session["interests"][: settings.MAX_INTERESTS]}
        if onboarding_complete
        else None
    )

    session["history"].append({"role": "user", "content": req.message})
    session["history"].append({"role": "assistant", "content": assistant_message})

    return ChatResponse(
        assistant_message=assistant_message,
        interests=session["interests"],
        interest_detected=interest_detected,
        interest_added=interest_added,
        examples=examples_models,
        onboarding_complete=onboarding_complete,
        profile=profile,
    )


@router.post("/api/feedback", response_model=ChatResponse)
async def feedback(req: FeedbackRequest):
    session = store.get_session(req.session_id)

    pending = session.get("pending_interests") or []

    # Show the next queued interest immediately
    if pending:
        next_interest = pending.pop(0)
        session["pending_interests"] = pending

        examples_models: list[PlaceCard] = []
        try:
            cache_key = store.normalize_interest(next_interest)
            ex = await places.get_examples(next_interest, cache_key)
            examples_models = [PlaceCard(**x) for x in (ex or [])]
            session["last_interest"] = next_interest
            session["last_examples"] = ex or []
        except Exception:
            session["last_interest"] = next_interest
            session["last_examples"] = []
            examples_models = []

        assistant_message = f"Nice. Here are a few Miami examples for {next_interest}."

        return ChatResponse(
            assistant_message=assistant_message,
            interests=session["interests"],
            interest_detected=True,
            interest_added=next_interest,
            examples=examples_models,
            onboarding_complete=False,
            profile=None,
        )

    # No pending interests left, finish if we have enough
    if len(session["interests"]) >= settings.MAX_INTERESTS:
        profile = {"interests": session["interests"][: settings.MAX_INTERESTS]}
        return ChatResponse(
            assistant_message="Awesome, that’s 3. Here’s your profile.",
            interests=session["interests"],
            interest_detected=False,
            onboarding_complete=True,
            profile=profile,
        )

    # Otherwise ask for the next interest
    remaining = settings.MAX_INTERESTS - len(session["interests"])
    msg = f"Cool. What else are you into in Miami? ({remaining} left)"
    return ChatResponse(
        assistant_message=msg,
        interests=session["interests"],
        interest_detected=False,
        onboarding_complete=False,
        profile=None,
    )


@router.post("/api/reset")
def reset(req: ResetRequest):
    if req.session_id in store.sessions:
        del store.sessions[req.session_id]

    return {"ok": True}
