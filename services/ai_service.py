import re
from typing import Dict, List

from app.core.config import settings

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - fallback for environments without the package
    genai = None

if genai is not None and settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


class AIService:
    def __init__(self) -> None:
        self.model = None
        if genai is not None and settings.GEMINI_API_KEY:
            try:
                self.model = genai.GenerativeModel("gemini-1.5-flash")
            except Exception:
                self.model = None

    async def summarize_text(self, text: str, title: str) -> Dict[str, object]:
        if not self.model:
            return self._fallback_summary(text, title)

        prompt = f"""
        You are an expert academic summarizer.
        Create a concise, high-quality summary of the following note titled '{title}'.
        Return JSON with keys: summary, keyPoints, keywords, mcqs.
        The summary should be a short paragraph.
        keyPoints should be an array of 4-6 concise bullet points.
        keywords should be an array of 6-10 relevant keywords.
        mcqs should be an array of 3 multiple-choice questions with fields question, options, answer.
        Source text:
        {text}
        """

        try:
            response = self.model.generate_content(prompt)
            content = response.text or ""
            return self._parse_ai_response(content, text, title)
        except Exception:
            return self._fallback_summary(text, title)

    def _fallback_summary(self, text: str, title: str) -> Dict[str, object]:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        summary = " ".join(sentences[:3]).strip() if sentences else f"Summary for {title}"
        key_points = [
            "Key insight from the uploaded document.",
            "Important concept or takeaway.",
            "Supporting detail or example.",
            "Action item or conclusion.",
        ]
        keywords = self._extract_keywords(text)
        mcqs = [
            {
                "question": f"What is the main topic of {title}?",
                "options": ["Main concept", "Secondary detail", "Irrelevant item", "No answer"],
                "answer": "Main concept",
            }
        ]
        return {"summary": summary, "keyPoints": key_points, "keywords": keywords, "mcqs": mcqs}

    def _parse_ai_response(self, content: str, text: str, title: str) -> Dict[str, object]:
        try:
            json_start = content.find("{")
            json_end = content.rfind("}")
            if json_start != -1 and json_end != -1 and json_end > json_start:
                payload = content[json_start:json_end + 1]
                payload = payload.replace("```json", "").replace("```", "")
                import json
                parsed = json.loads(payload)
                return {
                    "summary": parsed.get("summary") or self._fallback_summary(text, title)["summary"],
                    "keyPoints": parsed.get("keyPoints") or [],
                    "keywords": parsed.get("keywords") or self._extract_keywords(text),
                    "mcqs": parsed.get("mcqs") or [],
                }
        except Exception:
            pass
        return self._fallback_summary(text, title)

    def _extract_keywords(self, text: str) -> List[str]:
        words = re.findall(r"[A-Za-z]{4,}", text.lower())
        freq = {}
        for word in words:
            freq[word] = freq.get(word, 0) + 1
        sorted_words = sorted(freq.items(), key=lambda item: (-item[1], item[0]))
        return [word for word, _ in sorted_words[:8]]


ai_service = AIService()
