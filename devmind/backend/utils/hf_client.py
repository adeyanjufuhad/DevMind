"""Shared HuggingFace Inference API asynchronous client.

Enforces a strict 15-second timeout, token validation, and resilient error
handling to support graceful degradation in Stages 1 and 2.
"""

import logging
import os
from typing import Any, Dict, Optional
import httpx

logger = logging.getLogger("devmind.hf_client")

HF_INFERENCE_BASE_URL = "https://api-inference.huggingface.co/models"
DEFAULT_TIMEOUT_SECONDS = 15.0


class HuggingFaceClient:
    """Asynchronous client for querying the HuggingFace Inference API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("HUGGINGFACE_API_KEY")

    def is_configured(self) -> bool:
        """Returns True if a non-empty HuggingFace API key is present."""
        return bool(self.api_key and self.api_key.strip())

    async def query_model(
        self,
        model_id: str,
        inputs: Any,
        parameters: Optional[Dict[str, Any]] = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> Optional[Any]:
        """Queries a HuggingFace model with strict timeout and error capture.

        Args:
            model_id: HuggingFace model identifier (e.g. microsoft/codebert-base)
            inputs: String prompt or dictionary input for the model.
            parameters: Optional inference parameters (temperature, max_new_tokens).
            timeout: Timeout in seconds (defaults to 15.0s).

        Returns:
            The parsed JSON response from the API, or None if the call fails.
        """
        if not self.is_configured():
            logger.warning("HUGGINGFACE_API_KEY is not configured. Skipping HF call.")
            return None

        url = f"{HF_INFERENCE_BASE_URL}/{model_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {"inputs": inputs}
        if parameters:
            payload["parameters"] = parameters

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 503:
                    logger.warning(
                        "HuggingFace model %s is currently loading (503): %s",
                        model_id,
                        response.text[:200],
                    )
                    return None
                elif response.status_code == 429:
                    logger.warning(
                        "HuggingFace rate limit reached (429) for model %s",
                        model_id,
                    )
                    return None
                else:
                    logger.warning(
                        "HuggingFace query failed with status %d: %s",
                        response.status_code,
                        response.text[:200],
                    )
                    return None
        except httpx.TimeoutException:
            logger.warning(
                "HuggingFace request timed out after %.1fs for model %s",
                timeout,
                model_id,
            )
            return None
        except Exception as exc:
            logger.warning("HuggingFace request error for model %s: %s", model_id, exc)
            return None


# Global singleton instance for easy import across pipeline stages
hf_client = HuggingFaceClient()
