import json
import re
from typing import Any, Optional

from google import genai
from app.core.config import settings


class GeminiService:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def _generate_text(self, prompt: str) -> str:
        resp = self.client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )
        text = getattr(resp, "text", None)
        if isinstance(text, str) and text.strip():
            return text.strip()
        return str(resp).strip()

    @staticmethod
    def _safe_json_extract(text: str) -> dict[str, Any] | None:
        if not text:
            return None

        text = re.sub(r"```(?:json)?\s*", "", text, flags=re.I)
        text = text.replace("```", "").strip()

        try:
            obj = json.loads(text)
            return obj if isinstance(obj, dict) else None
        except Exception:
            pass

        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            return None
        try:
            obj = json.loads(m.group(0))
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None

    @staticmethod
    def _clean_list(raw: Any) -> list[str]:
        if not isinstance(raw, list):
            return []
        out: list[str] = []
        seen: set[str] = set()
        for x in raw:
            if not isinstance(x, str):
                continue
            s = re.sub(r"\s+", " ", x).strip()
            if not s:
                continue
            key = s.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(s)
            if len(out) >= 3:
                break
        return out

    def extract_interests(
        self, user_text: str, existing_interests: Optional[list[str]] = None
    ) -> list[str]:
        existing_interests = existing_interests or []
        existing_str = ", ".join(existing_interests) if existing_interests else "none"

        prompt = f"""
Return ONLY valid JSON. No markdown. No explanation.

Task:
Extract up to 3 "things to do in a city" interest categories from the user message.
These must be usable as Google Places Text Search category phrases.

Schema:
{{ "interests": ["..."] }}

Rules:
- Return categories, not venue names.
- Convert niche hobbies into venue-searchable categories when possible.
  Example: "padel" -> "Padel courts", "gym" -> "Gyms"
- If the user lists multiple likes in one message, include multiple categories (max 3).
- Avoid duplicates of existing interests: {existing_str}
- If none, return {{ "interests": [] }}

User message:
{user_text}
""".strip()

        raw = self._generate_text(prompt)
        obj = self._safe_json_extract(raw) or {"interests": []}
        interests = self._clean_list(obj.get("interests"))

        # final duplicate filter vs existing
        existing_norm = {
            i.strip().lower() for i in existing_interests if isinstance(i, str)
        }
        filtered: list[str] = []
        for x in interests:
            if x.strip().lower() not in existing_norm:
                filtered.append(x.strip())
            if len(filtered) >= 3:
                break
        return filtered

    def chat_reply(
        self, interests: list[str], user_text: str, interests_added: list[str]
    ) -> str:
        interests_str = ", ".join(interests) if interests else "none yet"
        added_str = ", ".join(interests_added) if interests_added else "none"

        prompt = f"""
You are HelloCity's onboarding assistant for a Miami city guide.
Tone: friendly, concise, mobile-chat style.

Context:
- We are collecting EXACTLY 3 interests about what the user likes to do in the city.
- Current interests: {interests_str}
- The user just said: {user_text}
- Newly captured interests from that message: {added_str}

Instructions:
- If we captured 1+ interests: acknowledge them briefly (one sentence) and say you'll show Miami examples.
- If we captured none: ask one concrete follow-up question to get a category.
- If we now have 3 interests: congratulate and say you'll summarize their profile.
Keep it short (1 to 2 sentences).
""".strip()

        return (
            self._generate_text(prompt)
            or "Got it. What do you like doing around Miami?"
        )
