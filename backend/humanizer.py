import os
import re
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("stealthdoc.humanizer")

SYSTEM_PROMPT = """You are an expert human academic writer specializing in stealth document editing and rewriting.
Your primary mission is to humanize AI-generated text so that it reads like an authentic, articulate human student and consistently achieves a 6-8% or lower AI detection score on AI detectors (Turnitin, GPTZero, ZeroGPT, CopyLeaks).

CRITICAL REWRITING RULES:
1. MAXIMIZE BURSTINESS & PERPLEXITY:
   - Mix short, punchy sentences with longer, naturally complex sentences.
   - Vary your sentence structures (start with prepositional phrases, dependent clauses, or casual transitions).
   - Avoid predictable rhythmic cadence or monotonous parallel sentence structures.

2. ABSOLUTELY BANNED AI BUZZWORDS & CLICHES:
   Never use any of these words or their variations:
   - delve, delving
   - harness, harnessing
   - leverage, leveraging
   - testament
   - intricate, intricately
   - robust, robustness
   - paradigm
   - dynamic
   - tapestry
   - multifaceted
   - crucial, vital, paramount
   - furthermore, moreover, in conclusion, to summarize, underscores

3. TONE & VOICE:
   - Adopt a natural, thoughtful, slightly imperfect authentic student/researcher tone.
   - Use straightforward, genuine vocabulary rather than decorative synonyms.
   - Add organic transition thoughts and realistic phrasing.

4. PRESERVE DOCUMENT STRUCTURE & MEANING:
   - Retain all core facts, data, arguments, and main ideas without distortion.
   - Maintain formatting elements: keep Headings as headings, list items as list items, and preserve the original paragraph order.
   - Return ONLY the humanized text with no introductory chatter, meta-commentary, or markdown code-fence wrapper.
"""

class TextHumanizer:
    """Handles text humanization using Google Gemini API to bypass AI detectors."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    def set_api_key(self, api_key: str):
        self.api_key = api_key

    def humanize_paragraph(self, text: str, api_key: Optional[str] = None) -> str:
        """Humanizes a single text paragraph or segment."""
        key = api_key or self.api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY is not configured. Please supply your Gemini API key in settings or header.")

        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Here is the text to humanize:\n"
            f"---\n{text}\n---\n\n"
            f"Rewrite it now following all rules above. Output ONLY the rewritten text:"
        )

        # Attempt with google-genai SDK
        try:
            from google import genai
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            if response and response.text:
                return self._clean_output(response.text)
        except Exception as e1:
            logger.warning(f"google-genai Client attempt failed ({e1}). Trying google.generativeai fallback...")

        # Fallback with google.generativeai
        try:
            import google.generativeai as gai
            gai.configure(api_key=key)
            model = gai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)
            response = model.generate_content(f"Rewrite this text to be human:\n\n{text}")
            if response and response.text:
                return self._clean_output(response.text)
        except Exception as e2:
            logger.error(f"Generative AI fallback failed: {e2}")
            raise RuntimeError(f"Gemini API request failed: {e2}")

        raise RuntimeError("No text returned from Gemini API.")

    def humanize_document(self, paragraphs: List[Dict[str, Any]], api_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Humanizes document paragraphs while preserving headings and structure."""
        humanized_paragraphs = []

        # Batch normal paragraphs to minimize API calls and maintain context flow
        for p in paragraphs:
            original_text = p.get("text", "").strip()
            if not original_text:
                humanized_paragraphs.append(dict(p))
                continue

            # Keep short headings or titles verbatim or lightly polished to preserve document outline
            if p.get("is_heading") and len(original_text.split()) < 8:
                humanized_paragraphs.append(dict(p))
                continue

            try:
                rewritten_text = self.humanize_paragraph(original_text, api_key=api_key)
                new_p = dict(p)
                new_p["text"] = rewritten_text
                new_p["original_text"] = original_text
                humanized_paragraphs.append(new_p)
            except Exception as e:
                logger.error(f"Error humanizing paragraph {p.get('id')}: {e}")
                # Keep original if individual call fails
                new_p = dict(p)
                new_p["error"] = str(e)
                humanized_paragraphs.append(new_p)

        return humanized_paragraphs

    @staticmethod
    def _clean_output(text: str) -> str:
        """Removes code fences and AI meta commentary."""
        cleaned = text.strip()
        cleaned = re.sub(r'^```[a-zA-Z]*\n', '', cleaned)
        cleaned = re.sub(r'\n```$', '', cleaned)
        cleaned = re.sub(r'^(Here is the rewritten text:|Rewritten text:)\s*', '', cleaned, flags=re.IGNORECASE)
        return cleaned.strip()
