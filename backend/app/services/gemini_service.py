import json
import re
from typing import Any

from google import genai  # Google GenAI SDK
from app.core.config import settings

class GeminiService:
    def __init__(self) -> None:
        # Official client pattern: genai.Client(api_key=...) :contentReference[oaicite:3]{index=3}
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def _generate_text(self, prompt: str) -> str:
        resp = self.client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )
        # Most examples treat response.text as the rendered text output
        text = getattr(resp, "text", None)
        if isinstance(text, str) and text.strip():
            return text.strip()

        # Fallback: stringify
        return str(resp).strip()

    def extract_interests(self, user_text: str) -> list[str]:
        prompt = f"""
You extract city-going-out interests (activity categories) from messy text.
Return ONLY valid JSON. No markdown, no explanation.

Schema:
{{ "interests": ["string", "..."] }}

Rules:
- interests are broad activity categories (e.g., "Rooftop bars", "Live jazz", "Art galleries", "Beach activities")
- Normalize into short category phrases
- Max 3 interests
- If none, return {{ "interests": [] }}

Text:
{user_text}
""".strip()

        raw = self._generate_text(prompt)

        def parse_json(s: str) -> dict[str, Any] | None:
            try:
                return json.loads(s)
            except Exception:
                m = re.search(r"\{.*\}", s, re.DOTALL)
                if not m:
                    return None
                try:
                    return json.loads(m.group(0))
                except Exception:
                    return None

        obj = parse_json(raw) or {"interests": []}
        interests = obj.get("interests", [])
        if not isinstance(interests, list):
            return []
        out: list[str] = []
        for x in interests[:3]:
            if isinstance(x, str) and x.strip():
                out.append(x.strip())
        return out

    def chat_reply(self, interests: list[str], user_text: str, interest_added: str | None) -> str:
        interests_str = ", ".join(interests) if interests else "none yet"
        prompt = f"""
You are HelloCity's onboarding assistant for a Miami city guide.
Tone: friendly, concise, mobile-chat style.

Context:
- We are collecting EXACTLY 3 interests about what the user likes to do in the city.
- Current interests: {interests_str}
- The user just said: {user_text}
- Newly captured interest (if any): {interest_added or "none"}

Instructions:
- If we just captured an interest: acknowledge it in one sentence and tell the user you’ll show a few Miami examples.
- If we did not capture an interest: ask a simple follow-up question to learn what they like doing in Miami.
- If we have 3 interests: congratulate and say you’ll summarize their profile.
Keep it short (1 to 2 sentences).
""".strip()

        return self._generate_text(prompt) or "Got it. What do you like doing around Miami?"