from __future__ import annotations

import json
from openai import OpenAI


class LLMClient:
    """Thin wrapper around an OpenAI-compatible chat API with JSON mode."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: str | None = None):
        kwargs: dict = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = OpenAI(**kwargs)
        self._model = model

    def reason(self, system_prompt: str, user_message: str) -> dict:
        """Send a chat completion request and parse the JSON response."""
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)
