"""
LLM Manager — Multi-provider LLM client with retry and backoff.
Supports: Ollama (local), OpenAI API, Anthropic API.
"""

import asyncio
import httpx
import json
import os
from typing import Optional, Literal, Any


class LLMManager:
    """Manages connections to different LLM providers."""

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 2, 4]  # seconds

    def __init__(self):
        self.llm_type: Optional[str] = None
        self.model: Optional[str] = None
        self.api_key: Optional[str] = None
        self.ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")

    def configure(
        self,
        llm_type: Literal["ollama", "openai", "anthropic"],
        model: str,
        api_key: Optional[str] = None
    ):
        """Configure the LLM provider."""
        self.llm_type = llm_type
        self.model = model
        self.api_key = api_key or os.environ.get(
            f"{llm_type.upper()}_API_KEY", ""
        )

        if llm_type == "ollama":
            self._check_ollama()
        elif llm_type in ["openai", "anthropic"] and not self.api_key:
            raise ValueError(
                f"API key required for {llm_type}. "
                f"Set {llm_type.upper()}_API_KEY environment variable or pass api_key parameter."
            )

    async def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text using the configured LLM."""
        if not self.llm_type:
            raise ValueError("LLM not configured. Call configure() first.")

        if self.llm_type == "ollama":
            return await self._generate_ollama(prompt, max_tokens)
        elif self.llm_type == "openai":
            return await self._generate_openai(prompt, max_tokens)
        elif self.llm_type == "anthropic":
            return await self._generate_anthropic(prompt, max_tokens)
        else:
            raise ValueError(f"Unsupported LLM type: {self.llm_type}")

    async def _call_with_retry(
        self,
        method: str,
        url: str,
        *,
        json_data: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: float = 60.0,
    ) -> httpx.Response:
        """Make an HTTP request with retry and exponential backoff.

        Retries on: 429 (rate limit), 5xx (server errors), and connection errors.
        Does NOT retry on: 401 (auth), 400 (bad request), 404 (not found).
        """
        last_error = None

        for attempt in range(self.MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    if method == "POST":
                        response = await client.post(url, json=json_data, headers=headers)
                    else:
                        response = await client.get(url, headers=headers)

                    # Success or non-retryable error → return immediately
                    if response.status_code < 500 and response.status_code != 429:
                        return response

                    # Rate limit or server error on last attempt → return as-is
                    if attempt == self.MAX_RETRIES:
                        return response

                    delay = self.RETRY_DELAYS[min(attempt, len(self.RETRY_DELAYS) - 1)]
                    if response.status_code == 429:
                        # Use Retry-After header if available, otherwise our delay
                        retry_after = response.headers.get("Retry-After")
                        if retry_after and retry_after.isdigit():
                            delay = int(retry_after)
                        await asyncio.sleep(delay)
                    else:
                        await asyncio.sleep(delay)

            except (httpx.ConnectError, httpx.ReadError, httpx.RemoteProtocolError) as e:
                last_error = e
                if attempt < self.MAX_RETRIES:
                    delay = self.RETRY_DELAYS[min(attempt, len(self.RETRY_DELAYS) - 1)]
                    await asyncio.sleep(delay)
                    continue
                raise ConnectionError(f"Failed after {self.MAX_RETRIES + 1} attempts: {e}") from e

        return response  # type: ignore[reportPossiblyUnboundVariable] — loop always returns or raises

    async def _generate_ollama(self, prompt: str, max_tokens: int) -> str:
        """Generate using local Ollama."""
        try:
            response = await self._call_with_retry(
                "POST",
                f"{self.ollama_url}/api/generate",
                json_data={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.8,
                    },
                },
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["response"]
        except httpx.ConnectError:
            raise ConnectionError(
                "Could not connect to Ollama. "
                "Make sure Ollama is running: ollama serve"
            )
        except Exception as e:
            raise Exception(f"Error generating with Ollama: {str(e)}")

    async def _generate_openai(self, prompt: str, max_tokens: int) -> str:
        """Generate using OpenAI API."""
        try:
            response = await self._call_with_retry(
                "POST",
                "https://api.openai.com/v1/chat/completions",
                json_data={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.8,
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
            if response.status_code == 401:
                raise ValueError("Invalid OpenAI API key")
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError("Invalid OpenAI API key")
            raise Exception(f"OpenAI API error: {e.response.text}")
        except Exception as e:
            raise Exception(f"Error generating with OpenAI: {str(e)}")

    async def _generate_anthropic(self, prompt: str, max_tokens: int) -> str:
        """Generate using Anthropic API."""
        try:
            response = await self._call_with_retry(
                "POST",
                "https://api.anthropic.com/v1/messages",
                json_data={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.8,
                },
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
            if response.status_code == 401:
                raise ValueError("Invalid Anthropic API key")
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError("Invalid Anthropic API key")
            raise Exception(f"Anthropic API error: {e.response.text}")
        except Exception as e:
            raise Exception(f"Error generating with Anthropic: {str(e)}")

    def _check_ollama(self):
        """Check if Ollama is available."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.ollama_url}/api/tags")
                response.raise_for_status()
        except Exception:
            raise ConnectionError(
                "Ollama is not running. Start it with: ollama serve"
            )

    def list_ollama_models(self) -> list:
        """List available Ollama models."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.ollama_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception:
            return []
