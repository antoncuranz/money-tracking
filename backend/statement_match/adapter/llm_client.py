import json
import logging
import time
from typing import Any

from openai import OpenAI

from config import config

logger = logging.getLogger(__name__)


class LlmProviderError(Exception):
    pass


class StatementMatchLlmClient:
    def __init__(self):
        self.model = config.statement_match_model

    def match_statement(self, prompt: str) -> dict[str, Any]:
        if not self.model:
            raise LlmProviderError("Statement match model is not configured.")

        client = OpenAI(
            base_url=config.statement_match_base_url,
            api_key=config.statement_match_api_key,
        )

        started_at = time.monotonic()
        try:
            response = client.chat.completions.create(
                model=self.model,
                temperature=0,
                max_tokens=config.statement_match_max_tokens,
                messages=[
                    {
                        "role": "system",
                        "content": "You match transactions to statement text and return JSON only.",
                    },
                    {"role": "user", "content": prompt},
                ],
                extra_body={
                    "providerOptions": {
                        "gateway": {
                            "only": ["vertex", "nebius"],
                        }
                    }
                },
            )
        except Exception as exc:
            raise LlmProviderError("Statement match provider request failed.") from exc

        duration_ms = round((time.monotonic() - started_at) * 1000)
        usage = response.usage
        logger.info(
            "statement_match_llm_response duration_ms=%s input_tokens=%s output_tokens=%s",
            duration_ms,
            usage.prompt_tokens if usage else None,
            usage.completion_tokens if usage else None,
        )

        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise LlmProviderError("Statement match provider returned no content.")

        try:
            return json.loads(self._strip_code_fences(content))
        except json.JSONDecodeError as exc:
            raise LlmProviderError("Statement match provider returned invalid JSON.") from exc

    def _strip_code_fences(self, content: str) -> str:
        stripped = content.strip()
        if not stripped.startswith("```"):
            return stripped

        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
