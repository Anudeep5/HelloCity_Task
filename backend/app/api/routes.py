from fastapi import APIRouter
from app.schemas.chat import ChatRequest, FeedbackRequest, ChatResponse, PlaceCard
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

    if len(session["interests"]) >= settings.MAX_INTERESTS:
        profile = {"interests": session["interests"][: settings.MAX_INTERESTS]}
        return ChatResponse(
            assistant_message="You’re all set. Here’s your profile.",
            interests=session["interests"],
            interest_detected=False,
            onboarding_complete=True,
            profile=profile,
        )

    extracted = llm.extract_interests(req.message)

    interest_detected = False
    interest_added = None
    examples_models: list[PlaceCard] = []

    # Add at most one new interest per message (cleaner UX)
    for cand in extracted:
        added, canonical = store.add_interest_deduped(session, cand)
        if added:
            interest_detected = True
            interest_added = canonical
            break

    assistant_message = llm.chat_reply(
        session["interests"], req.message, interest_added
    )

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

    onboarding_complete = len(session["interests"]) >= settings.MAX_INTERESTS
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

    if len(session["interests"]) >= settings.MAX_INTERESTS:
        profile = {"interests": session["interests"][: settings.MAX_INTERESTS]}
        return ChatResponse(
            assistant_message="Done. Here’s your profile.",
            interests=session["interests"],
            interest_detected=False,
            onboarding_complete=True,
            profile=profile,
        )

    remaining = settings.MAX_INTERESTS - len(session["interests"])
    msg = f"Cool. What else are you into in Miami? ({remaining} left)"
    return ChatResponse(
        assistant_message=msg,
        interests=session["interests"],
        interest_detected=False,
        onboarding_complete=False,
        profile=None,
    )
