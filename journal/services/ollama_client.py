import json
import logging
import re
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

TAGGING_PROMPT = """You are a journal entry tagger. Read the following journal entry \
and return ONLY a JSON array of 1-5 short, lowercase tags that categorize the themes \
and emotions in the entry. Examples of good tags: work, gratitude, anxiety, family, \
health, creativity, goals, reflection, frustration, travel. \
Return ONLY the JSON array, nothing else.

Journal entry:
{content}

Tags:"""


class OllamaClient:
    """Client for interacting with the Ollama REST API."""

    def __init__(self, base_url=None, model=None, timeout=None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout or settings.OLLAMA_TIMEOUT

    def is_available(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            urllib.request.urlopen(req, timeout=5)
            return True
        except (urllib.error.URLError, OSError):
            return False

    def generate_tags(self, entry_content: str) -> list[str]:
        """Send journal entry text to Ollama, return a list of tag strings."""
        prompt = TAGGING_PROMPT.format(content=entry_content)

        payload = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3},
            }
        ).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                response_text = result.get("response", "").strip()
                # Models often wrap the array in extra text; extract it with regex
                match = re.search(r"\[.*?\]", response_text, re.DOTALL)
                if not match:
                    logger.warning("Ollama response contained no JSON array: %r", response_text[:200])
                    return []
                tags = json.loads(match.group())
                if isinstance(tags, list):
                    return [
                        str(t).lower().strip()[:50] for t in tags[:5] if str(t).strip()
                    ]
        except (json.JSONDecodeError, urllib.error.URLError, OSError, KeyError) as e:
            logger.warning("Ollama tagging failed: %s", e)

        return []
