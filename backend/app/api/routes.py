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

    # Only return profile if:
    # - we already have 3 interests
    # - nothing is queued to show
    # (we never want to skip showing examples for a captured interest)
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

    extracted = llm.extract_interests(
        req.message, existing_interests=session["interests"]
    )

    interest_detected = False
    interest_added = None
    examples_models: list[PlaceCard] = []

    remaining = settings.MAX_INTERESTS - len(session["interests"])
    added_interests: list[str] = []

    # Add as many as we can from this message, up to remaining slots.
    for cand in extracted:
        if remaining <= 0:
            break
        added, canonical = store.add_interest_deduped(session, cand)
        if added and canonical:
            added_interests.append(canonical)
            remaining -= 1

    # Queue any extras (they will be auto-shown after the user clicks Yes/No)
    session["pending_interests"] = (
        added_interests[1:] if len(added_interests) > 1 else []
    )

    if added_interests:
        interest_detected = True
        interest_added = added_interests[0]

    assistant_message = llm.chat_reply(
        session["interests"], req.message, added_interests
    )

    # If we detected an interest to show now, fetch examples for it
    if interest_detected and interest_added:
        cache_key = store.normalize_interest(interest_added)
        try:
            ex = await places.get_examples(interest_added, cache_key)
            examples_models = [PlaceCard(**x) for x in (ex or [])]
            session["last_interest"] = interest_added
            session["last_examples"] = ex or []
        except Exception:
            # Never fail the chat endpoint due to places lookup
            examples_models = []
            session["last_interest"] = interest_added
            session["last_examples"] = []
    else:
        session["last_interest"] = None
        session["last_examples"] = []
        examples_models = []

    # Completion logic:
    # - If we are returning examples now, do NOT complete
    # - If we have queued interests to show, do NOT complete
    # - Only complete when we have 3 interests and nothing left to show
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

    # 1) If we have queued interests from the last user message, show the next one immediately
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

    # 2) No pending interests left. If we have 3 interests, finish now.
    if len(session["interests"]) >= settings.MAX_INTERESTS:
        profile = {"interests": session["interests"][: settings.MAX_INTERESTS]}
        return ChatResponse(
            assistant_message="Awesome, that’s 3. Here’s your profile.",
            interests=session["interests"],
            interest_detected=False,
            onboarding_complete=True,
            profile=profile,
        )

    # 3) Otherwise ask for the next interest
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
    # hard delete the session so next request starts clean
    if req.session_id in store.sessions:
        del store.sessions[req.session_id]

    return {"ok": True}
