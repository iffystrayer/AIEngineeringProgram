"""
Ollama LLM Provider

Provides integration with local Ollama instance for cost-free, privacy-first LLM inference.

Ollama: https://ollama.ai/
- Run LLMs locally (Llama, Mistral, Qwen, DeepSeek, etc.)
- Zero API costs
- Complete data privacy
- Offline capability

Usage:
    provider = OllamaProvider(
        base_url="http://localhost:11434",
        default_model="llama3.2"
    )

    response = await provider.complete(request)
"""

import logging
import time
from typing import Any, AsyncIterator, Optional
import httpx

from src.llm.base import (
    BaseLLMProvider,
    LLMRequest,
    LLMResponse,
    LLMMessage,
)

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """
    Ollama provider for local LLM inference.

    Connects to local Ollama instance (or remote via base_url) and provides
    standardized LLM interface compatible with commercial providers.

    Features:
    - Zero cost inference
    - Complete data privacy (no external API calls)
    - Supports multiple models (Llama, Mistral, Qwen, DeepSeek, etc.)
    - Streaming support
    - Compatible with LLMRouter fallback chains
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        default_model: str = "llama3.2:latest",
        timeout: int = 120,  # Ollama can be slower than cloud APIs
        max_retries: int = 3,
        api_key: Optional[str] = None,  # Not used, but keeps interface consistent
        **kwargs,
    ):
        """
        Initialize Ollama provider.

        Args:
            base_url: Ollama API base URL (default: http://localhost:11434)
            default_model: Default model to use (default: llama3.2)
            timeout: Request timeout in seconds (default: 120)
            max_retries: Maximum retry attempts (default: 3)
            api_key: Not used for Ollama (keeps interface consistent)
            **kwargs: Additional provider configuration
        """
        # Call parent with dummy api_key (Ollama doesn't need it)
        super().__init__(
            api_key=api_key or "ollama-local",
            default_model=default_model,
            timeout=timeout,
            max_retries=max_retries,
            **kwargs,
        )

        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=timeout)

        logger.info(
            f"OllamaProvider initialized: base_url={self.base_url}, "
            f"default_model={self.default_model}"
        )

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """
        Generate completion using Ollama.

        Args:
            request: Standardized LLM request

        Returns:
            Standardized LLM response

        Raises:
            Exception: If Ollama is not running or request fails
        """
        start_time = time.time()

        # Convert request to Ollama format
        ollama_request = self._convert_to_provider_format(request)

        try:
            # Call Ollama API
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=ollama_request,
            )
            response.raise_for_status()

            # Parse response
            ollama_response = response.json()

            # Convert to standardized format
            llm_response = self._convert_from_provider_format(ollama_response)

            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            llm_response.latency_ms = latency_ms

            logger.debug(
                f"Ollama completion: model={llm_response.model}, "
                f"tokens={llm_response.total_tokens}, "
                f"latency={latency_ms}ms"
            )

            return llm_response

        except httpx.ConnectError as e:
            error_msg = (
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: 'ollama serve'"
            )
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e

        except httpx.HTTPStatusError as e:
            error_msg = f"Ollama API error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg) from e

        except Exception as e:
            logger.error(f"Ollama provider error: {e}")
            raise

    async def stream_complete(
        self, request: LLMRequest
    ) -> AsyncIterator[LLMResponse]:
        """
        Generate streaming completion using Ollama.

        Args:
            request: Standardized LLM request

        Yields:
            Partial LLM responses as they arrive

        Raises:
            Exception: If Ollama is not running or request fails
        """
        # Convert request to Ollama format with streaming enabled
        ollama_request = self._convert_to_provider_format(request)
        ollama_request["stream"] = True

        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=ollama_request,
            ) as response:
                response.raise_for_status()

                accumulated_text = ""
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue

                    import json
                    chunk = json.loads(line)

                    # Accumulate response text
                    if "response" in chunk:
                        accumulated_text += chunk["response"]

                        # Yield incremental response
                        yield LLMResponse(
                            content=accumulated_text,
                            model=chunk.get("model", request.model or self.default_model),
                            provider="ollama",
                            finish_reason="stop" if chunk.get("done") else "length",
                            total_tokens=chunk.get("eval_count", 0) + chunk.get("prompt_eval_count", 0),
                            prompt_tokens=chunk.get("prompt_eval_count", 0),
                            completion_tokens=chunk.get("eval_count", 0),
                        )

        except httpx.ConnectError as e:
            error_msg = (
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: 'ollama serve'"
            )
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e

        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            raise

    async def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Estimate token count for text.

        Note: Ollama doesn't provide a direct tokenization API,
        so we use a rough estimate (1 token ~= 4 characters for English).

        Args:
            text: Text to tokenize
            model: Model to use for tokenization (unused for Ollama)

        Returns:
            Estimated number of tokens
        """
        # Rough estimate: 1 token ~= 4 characters
        # This is approximate but sufficient for most use cases
        estimated_tokens = len(text) // 4

        logger.debug(f"Estimated tokens for {len(text)} chars: {estimated_tokens}")
        return estimated_tokens

    def get_model_info(self, model: str) -> dict[str, Any]:
        """
        Get information about a specific Ollama model.

        Args:
            model: Model identifier

        Returns:
            Dictionary with model info
        """
        # Default model info for Ollama models
        # These are estimates based on typical model sizes
        model_info = {
            "context_length": 8192,  # Most Ollama models support 8K context
            "cost_per_1k_input_tokens": 0.0,  # Free!
            "cost_per_1k_output_tokens": 0.0,
            "supports_streaming": True,
            "supports_function_calling": False,
            "typical_latency_ms": 3000,
        }

        # Adjust for specific models if known
        if "qwen" in model.lower():
            model_info["context_length"] = 32768  # Qwen supports larger context
        elif "deepseek" in model.lower():
            model_info["context_length"] = 32768
        elif "phi" in model.lower():
            model_info["typical_latency_ms"] = 1500  # Phi is faster

        return model_info

    async def validate_credentials(self) -> bool:
        """
        Validate Ollama connection by checking if server is running.

        Returns:
            True if Ollama is accessible, False otherwise
        """
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()

            # Check if any models are available
            models = response.json().get("models", [])

            if not models:
                logger.warning("Ollama is running but no models are available")
                return False

            logger.info(f"Ollama validation successful: {len(models)} models available")
            return True

        except httpx.ConnectError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            return False

        except Exception as e:
            logger.error(f"Ollama validation failed: {e}")
            return False

    def _convert_to_provider_format(self, request: LLMRequest) -> dict[str, Any]:
        """
        Convert standardized request to Ollama API format.

        Ollama API format:
        {
            "model": "llama3.2",
            "prompt": "Why is the sky blue?",
            "stream": false,
            "options": {
                "temperature": 0.7,
                "num_predict": 2000
            }
        }

        Args:
            request: Standardized LLMRequest

        Returns:
            Ollama API request dictionary
        """
        # Combine messages into single prompt
        # Ollama's /api/generate endpoint expects a single prompt string
        prompt_parts = []
        for msg in request.messages:
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                prompt_parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                prompt_parts.append(f"Assistant: {msg.content}")

        prompt = "\n\n".join(prompt_parts)

        ollama_request = {
            "model": request.model or self.default_model,
            "prompt": prompt,
            "stream": request.stream,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            },
        }

        # Add optional parameters if provided
        if request.top_p != 1.0:
            ollama_request["options"]["top_p"] = request.top_p

        if request.stop_sequences:
            ollama_request["options"]["stop"] = request.stop_sequences

        return ollama_request

    def _convert_from_provider_format(self, response: dict[str, Any]) -> LLMResponse:
        """
        Convert Ollama API response to standardized format.

        Ollama response format:
        {
            "model": "llama3.2",
            "created_at": "2025-10-17T12:00:00Z",
            "response": "The sky appears blue because...",
            "done": true,
            "total_duration": 2500000000,  # nanoseconds
            "prompt_eval_count": 25,
            "eval_count": 150
        }

        Args:
            response: Ollama API response dictionary

        Returns:
            Standardized LLMResponse
        """
        return LLMResponse(
            content=response.get("response", ""),
            model=response.get("model", self.default_model),
            provider="ollama",
            finish_reason="stop" if response.get("done") else "length",
            prompt_tokens=response.get("prompt_eval_count", 0),
            completion_tokens=response.get("eval_count", 0),
            total_tokens=response.get("prompt_eval_count", 0)
            + response.get("eval_count", 0),
            raw_response=response,
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - close HTTP client."""
        await self.client.aclose()

    def __repr__(self) -> str:
        return f"OllamaProvider(base_url={self.base_url}, model={self.default_model})"
