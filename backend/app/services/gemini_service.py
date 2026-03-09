import asyncio
import json
import re
from typing import Any, Optional

from google import genai
from app.core.config import settings


class GeminiService:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def _generate_text(self, prompt: str) -> str:
        loop = asyncio.get_running_loop()

        resp = await loop.run_in_executor(
            None,
            lambda: self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
            ),
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
    def _clean_list(raw: Any, max_items: int = 3) -> list[str]:
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

            if len(out) >= max_items:
                break

        return out

    async def analyze_message(
        self,
        user_text: str,
        existing_interests: Optional[list[str]] = None,
        max_interests: int = 3,
    ) -> dict[str, Any]:
        existing_interests = existing_interests or []
        existing_str = ", ".join(existing_interests) if existing_interests else "none"

        prompt = f"""
Return ONLY valid JSON. No markdown. No explanation.

You are HelloCity's onboarding assistant for a Miami city guide.

Task:
From the user's message, do both of the following:
1. Extract up to {max_interests} "things to do in a city" interest categories
2. Write the short assistant reply to send back

Output schema:
{{
  "interests": ["..."],
  "assistant_reply": "..."
}}

Rules for interests:
- Return categories, not venue names
- Categories must be usable as Google Places / city activity search phrases
- Convert niche hobbies into venue-searchable categories when possible
  Example: "padel" -> "Padel courts", "gym" -> "Gyms"
- If the user lists multiple likes, include multiple categories up to {max_interests}
- Avoid duplicates of existing interests: {existing_str}
- If none are found, return "interests": []

Rules for assistant_reply:
- Friendly, concise, mobile-chat style
- If 1+ interests were captured: acknowledge briefly and say you'll show Miami examples
- If none were captured: ask one concrete follow-up question
- If the total count would now reach 3 interests, congratulate and say you'll summarize their profile
- Keep it short, 1 to 2 sentences max

Current interests: {existing_str}
User message: {user_text}
""".strip()

        raw = await self._generate_text(prompt)
        obj = self._safe_json_extract(raw) or {}

        interests = self._clean_list(obj.get("interests"), max_items=max_interests)

        existing_norm = {
            i.strip().lower() for i in existing_interests if isinstance(i, str)
        }

        filtered: list[str] = []
        for x in interests:
            key = x.strip().lower()
            if key not in existing_norm:
                filtered.append(x.strip())
            if len(filtered) >= max_interests:
                break

        assistant_reply = obj.get("assistant_reply")
        if not isinstance(assistant_reply, str) or not assistant_reply.strip():
            if filtered:
                total = len(existing_interests) + len(filtered)
                if total >= 3:
                    assistant_reply = "Awesome, I’ve got your three interests. I’ll summarize your Miami profile now."
                else:
                    assistant_reply = f"Nice, I’ve added {', '.join(filtered)}. I’ll show you some Miami examples."
            else:
                assistant_reply = "Got it. What do you like doing around Miami?"

        return {
            "interests": filtered,
            "assistant_reply": assistant_reply.strip(),
        }
