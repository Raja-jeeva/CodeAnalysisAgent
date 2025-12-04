import json
import os
from typing import Dict, Any

import requests

from .logger import get_logger

logger = get_logger(__name__)


class MockProvider:
    def analyze(self, prompt: str) -> Dict[str, Any]:
        # Simple mock response for testing
        example = {
            "summary": "Most requirements appear implemented with minor gaps.",
            "traceability_matrix": {
                "R-1": "IMPLEMENTED",
                "R-2": "PARTIALLY_IMPLEMENTED",
                "R-3": "NOT_IMPLEMENTED"
            },
            "missing_requirements": ["R-3"],
            "suggestions": [
                "Add comprehensive error handling and unit tests for requirement R-2.",
                "Implement data validation workflow for R-3."
            ],
            "detailed_analysis": "R-1 references found in module A; R-2 partially covered in module B with missing edge cases; R-3 no references found."
        }
        logger.info("Returning mock LLM response.")
        return example


class OpenAIProvider:
    def __init__(self, api_key: str):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except Exception as e:
            logger.exception("Failed to initialize OpenAI client: %s", e)
            self.client = None

    def analyze(self, prompt: str) -> Dict[str, Any]:
        if self.client is None:
            logger.warning("OpenAI client unavailable; falling back to mock.")
            return MockProvider().analyze(prompt)
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a strict requirements verification assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            text = completion.choices[0].message.content
            return _parse_llm_json(text)
        except Exception as e:
            logger.exception("OpenAI analysis failed: %s", e)
            return MockProvider().analyze(prompt)


class AnthropicProvider:
    def __init__(self, api_key: str):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except Exception as e:
            logger.exception("Failed to initialize Anthropic client: %s", e)
            self.client = None

    def analyze(self, prompt: str) -> Dict[str, Any]:
        if self.client is None:
            logger.warning("Anthropic client unavailable; falling back to mock.")
            return MockProvider().analyze(prompt)
        try:
            msg = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.2,
                system="You are a strict requirements verification assistant.",
                messages=[{"role": "user", "content": prompt}],
            )
            # Extract text from response
            text = "".join(block.text for block in msg.content if hasattr(block, "text"))
            return _parse_llm_json(text)
        except Exception as e:
            logger.exception("Anthropic analysis failed: %s", e)
            return MockProvider().analyze(prompt)


class OllamaProvider:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url
        self.model = model

    def analyze(self, prompt: str) -> Dict[str, Any]:
        try:
            payload = {"model": self.model, "prompt": prompt, "stream": False}
            resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            text = data.get("response", "")
            return _parse_llm_json(text)
        except Exception as e:
            logger.exception("Ollama analysis failed (is Ollama running?): %s", e)
            return MockProvider().analyze(prompt)


def _parse_llm_json(text: str) -> Dict[str, Any]:
    """Attempt to parse the LLM JSON response; fall back to heuristic if not valid JSON."""
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            # Ensure required keys exist
            result.setdefault("summary", "")
            result.setdefault("traceability_matrix", {})
            result.setdefault("missing_requirements", [])
            result.setdefault("suggestions", [])
            result.setdefault("detailed_analysis", "")
            return result
    except Exception:
        pass

    logger.warning("LLM did not return valid JSON. Applying heuristic parse.")
    # Heuristic: create a minimal dict with the raw text in detailed_analysis
    return {
        "summary": "Model returned non-JSON output.",
        "traceability_matrix": {},
        "missing_requirements": [],
        "suggestions": ["Ensure the model is instructed to output strict JSON."],
        "detailed_analysis": text,
    }


def analyze_with_llm(prompt: str, model_name: str, api_key: str) -> Dict[str, Any]:
    """
    Select provider based on model_name; if no api_key, use mock or local provider.
    Returns normalized result dict.
    """
    model_name = (model_name or "").strip().lower()

    if model_name == "gpt-4o":
        # Prefer explicit API key; fallback to env
        key = api_key or os.getenv("OPENAI_API_KEY", "")
        if not key:
            logger.info("No OpenAI API key provided; using mock response.")
            return MockProvider().analyze(prompt)
        return OpenAIProvider(key).analyze(prompt)

    if model_name == "claude 3.5 sonnet":
        key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        if not key:
            logger.info("No Anthropic API key provided; using mock response.")
            return MockProvider().analyze(prompt)
        return AnthropicProvider(key).analyze(prompt)

    if model_name == "local llama 3":
        # Try local Ollama; no API key needed
        return OllamaProvider().analyze(prompt)

    logger.info("Unknown model '%s'; defaulting to mock.", model_name)
    return MockProvider().analyze(prompt)