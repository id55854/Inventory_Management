"""
Gemini API integration for natural language shelf analysis (Section 6.2).

Uses Gemini vision to analyze shelf images and generate reports when
`GEMINI_API_KEY` / `settings.gemini_api_key` is set.
"""

from __future__ import annotations

import asyncio
import base64
import io
import json
import logging
import re
from typing import Any

from config import settings

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    from PIL import Image
except ImportError:  # pragma: no cover
    genai = None  # type: ignore
    Image = None  # type: ignore


def is_gemini_available() -> bool:
    return bool(settings.gemini_api_key and genai is not None and Image is not None)


class GeminiInsightEngine:
    """Gemini Pro / Flash vision + text — matches Section 6.2."""

    def __init__(self) -> None:
        if not genai or not settings.gemini_api_key:
            raise RuntimeError("Gemini not configured")
        genai.configure(api_key=settings.gemini_api_key)
        self._model = genai.GenerativeModel(settings.gemini_model)

    def _run_generate(self, *args: Any, **kwargs: Any) -> Any:
        return self._model.generate_content(*args, **kwargs)

    async def analyze_shelf(
        self,
        image_bytes: bytes,
        detections: list[dict],
        occupancy: float,
        issues: list[dict],
        store_context: str,
    ) -> str:
        """Single narrative analysis (Section 6.2)."""
        buf = io.BytesIO(image_bytes)
        image = Image.open(buf).convert("RGB")

        prompt = f"""You are RetailPulse AI, an expert retail shelf analyst.
Analyze this shelf image from a Croatian grocery store.

Context: {store_context}
Current occupancy: {occupancy}%
Detected products: {len(detections)}
Issues found: {len(issues)}

Detection details:
{self._format_detections(detections)}

Issues:
{self._format_issues(issues)}

Provide a concise analysis (3-5 sentences) covering:
1. Overall shelf health assessment
2. Most critical issue requiring immediate action
3. Specific restock recommendation with quantities
4. Revenue impact estimate if issues are not addressed

Be specific, actionable, and quantitative. Use product names when possible.
Respond in English (the dashboard is in English)."""

        response = await asyncio.to_thread(self._run_generate, [prompt, image])
        return self._response_text(response)

    async def analyze_shelf_insight_json(
        self,
        image_bytes: bytes,
        context: str | None,
    ) -> dict[str, Any]:
        """Structured insight for POST /insights/analyze-shelf."""
        buf = io.BytesIO(image_bytes)
        image = Image.open(buf).convert("RGB")
        ctx = context or "No extra context."
        prompt = f"""You are RetailPulse AI. Analyze this Croatian grocery shelf photo.

Context: {ctx}

Return ONLY valid JSON (no markdown fences) with exactly these keys:
- "summary": string (2-4 sentences, English)
- "issues": array of objects with "type" (string), "severity" ("low"|"medium"|"high"), "region" (string)
- "recommendations": array of strings (max 5, actionable)

Be specific to what you see in the image."""

        response = await asyncio.to_thread(self._run_generate, [prompt, image])
        text = self._response_text(response)
        return self._parse_json_response(text)

    async def generate_store_report(self, store_data: dict) -> dict[str, Any]:
        """Daily store health report as JSON (Section 6.2)."""
        prompt = f"""Generate a daily store health briefing for a Croatian grocery store manager.

Store data: {json.dumps(store_data, ensure_ascii=False)}

Format as JSON with these fields:
- "executive_summary": 2-3 sentence overview
- "critical_actions": list of immediate actions needed
- "positive_trends": what's going well
- "predicted_issues": issues likely to occur in next 24h
- "revenue_impact": estimated EUR impact of current issues (string or number)
- "recommendations": prioritized list of actions

Be specific and quantitative. Respond in English."""

        response = await asyncio.to_thread(self._run_generate, prompt)
        return self._parse_json_response(self._response_text(response))

    async def daily_brief(self, store_id: int, scan_history: list) -> str:
        """Morning briefing text (Section 6.2)."""
        prompt = f"""Create a morning briefing for the store manager.

Store id: {store_id}
Yesterday's scan data: {json.dumps(scan_history, ensure_ascii=False, default=str)}

Format as a short, punchy briefing the manager reads at 7am:
- Top 3 priority actions for today
- Items that need restocking first
- Any anomalies detected
- Expected busy periods and preparation needed

Keep it under 200 words. Conversational but data-driven. English."""

        response = await asyncio.to_thread(self._run_generate, prompt)
        return self._response_text(response)

    def _response_text(self, response: Any) -> str:
        try:
            t = response.text
            if t:
                return t.strip()
        except Exception as e:  # pragma: no cover
            logger.warning("Gemini response.text failed: %s", e)
        if getattr(response, "candidates", None):
            parts = []
            for c in response.candidates:
                for p in getattr(c.content, "parts", []) or []:
                    if hasattr(p, "text") and p.text:
                        parts.append(p.text)
            if parts:
                return "\n".join(parts).strip()
        return ""

    def _format_detections(self, detections: list) -> str:
        lines = []
        for d in detections[:20]:
            if isinstance(d, dict):
                name = d.get("product_name") or d.get("productName") or "unknown"
                pos = d.get("shelf_position", d.get("shelfPosition", "?"))
                conf = d.get("confidence", 0)
                try:
                    conf_s = f"{float(conf):.0%}"
                except (TypeError, ValueError):
                    conf_s = str(conf)
                lines.append(f"- {name} (shelf {pos}, confidence {conf_s})")
        return "\n".join(lines) if lines else "No products detected"

    def _format_issues(self, issues: list) -> str:
        lines = []
        for issue in issues:
            if not isinstance(issue, dict):
                lines.append(f"- {issue!r}")
                continue
            sev = str(issue.get("severity", "medium")).upper()
            desc = (
                issue.get("description")
                or issue.get("type")
                or issue.get("product")
                or json.dumps(issue, ensure_ascii=False)
            )
            lines.append(f"- [{sev}] {desc}")
        return "\n".join(lines) if lines else "No issues detected"

    def _parse_json_response(self, text: str) -> dict[str, Any]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```\s*$", "", cleaned)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"raw_response": text}


_engine: GeminiInsightEngine | None = None
_engine_initialized: bool = False


def get_engine() -> GeminiInsightEngine | None:
    """Singleton when API key is set and dependencies installed."""
    global _engine, _engine_initialized
    if _engine_initialized:
        return _engine
    _engine_initialized = True
    if not is_gemini_available():
        return None
    try:
        _engine = GeminiInsightEngine()
    except Exception as e:  # pragma: no cover
        logger.warning("Gemini init failed: %s", e)
        _engine = None
    return _engine


def decode_base64_image(b64: str) -> bytes:
    s = b64.strip()
    if s.startswith("data:") and "," in s:
        s = s.split(",", 1)[1]
    return base64.b64decode(s, validate=False)
