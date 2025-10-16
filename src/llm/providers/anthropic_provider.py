"""
Anthropic (Claude) Provider Implementation

Adapter for Anthropic's Claude API following the BaseLLMProvider interface.
"""

import asyncio
import logging
from typing import Any, AsyncIterator, Optional

from src.llm.base import (
    BaseLLMProvider,
    LLMError,
    LLMRequest,
    LLMResponse,
)

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude provider implementation.

    Supports: Claude 3 Opus, Sonnet, and Haiku models.
    """

    def __init__(
        self,
        api_key: str,
        default_model: str = "claude-3-sonnet-20240229",
        timeout: int = 30,
        max_retries: int = 3,
        **kwargs,
    ):
        super().__init__(api_key, default_model, timeout, max_retries, **kwargs)

        # Model mappings (short name -> full API name)
        self.model_mappings = {
            # Claude 3 models
            "claude-3-opus": "claude-3-opus-20240229",
            "claude-3-sonnet": "claude-3-sonnet-20240229",
            "claude-3-haiku": "claude-3-haiku-20240307",
            # Claude 4 models
            "claude-sonnet-4": "claude-sonnet-4-20250514",
            "claude-haiku-4": "claude-haiku-4-5-20251001",
            "claude-haiku-4-5": "claude-haiku-4-5-20251001",
        }

        # Initialize Anthropic client (lazy loading)
        self._client = None

    def _get_client(self):
        """Lazy load Anthropic client."""
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic

                self._client = AsyncAnthropic(
                    api_key=self.api_key,
                    timeout=self.timeout,
                )
            except ImportError:
                raise ImportError(
                    "anthropic package not installed. "
                    "Install with: pip install anthropic"
                )

        return self._client

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Generate completion using Claude API."""
        import time
        from datetime import datetime

        client = self._get_client()

        # Resolve model name
        model = self._resolve_model_name(request.model or self.default_model)

        # Convert to Anthropic format
        anthropic_request = self._convert_to_provider_format(request)

        try:
            start_time = time.time()

            # Make API call
            response = await client.messages.create(
                model=model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                messages=anthropic_request["messages"],
                **anthropic_request.get("extra_params", {}),
            )

            latency_ms = int((time.time() - start_time) * 1000)

            # Convert to standardized format
            llm_response = LLMResponse(
                content=response.content[0].text if response.content else "",
                model=response.model,
                provider="anthropic",
                finish_reason=response.stop_reason or "stop",
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens
                + response.usage.output_tokens,
                created_at=datetime.now(),
                latency_ms=latency_ms,
                raw_response=response.model_dump() if hasattr(response, "model_dump") else None,
            )

            logger.debug(
                f"Claude completion: {llm_response.total_tokens} tokens, "
                f"{latency_ms}ms"
            )

            return llm_response

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise self._convert_error(e)

    async def stream_complete(
        self, request: LLMRequest
    ) -> AsyncIterator[LLMResponse]:
        """Generate streaming completion using Claude API."""
        import time
        from datetime import datetime

        client = self._get_client()
        model = self._resolve_model_name(request.model or self.default_model)
        anthropic_request = self._convert_to_provider_format(request)

        try:
            start_time = time.time()

            async with client.messages.stream(
                model=model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                messages=anthropic_request["messages"],
            ) as stream:
                async for text in stream.text_stream:
                    latency_ms = int((time.time() - start_time) * 1000)

                    yield LLMResponse(
                        content=text,
                        model=model,
                        provider="anthropic",
                        finish_reason="streaming",
                        created_at=datetime.now(),
                        latency_ms=latency_ms,
                    )

        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise self._convert_error(e)

    async def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Count tokens using Anthropic's tokenization.

        Note: Anthropic doesn't provide a direct token counting API,
        so this is an approximation.
        """
        # Rough approximation: ~4 characters per token
        # For accurate counting, would need to use actual tokenizer
        return len(text) // 4

    def get_model_info(self, model: str) -> dict[str, Any]:
        """Get Claude model information."""
        model_info = {
            # Claude 3 models
            "claude-3-opus-20240229": {
                "context_length": 200000,
                "cost_per_1k_input": 0.015,
                "cost_per_1k_output": 0.075,
                "capabilities": ["text", "vision", "function_calling"],
            },
            "claude-3-sonnet-20240229": {
                "context_length": 200000,
                "cost_per_1k_input": 0.003,
                "cost_per_1k_output": 0.015,
                "capabilities": ["text", "vision", "function_calling"],
            },
            "claude-3-haiku-20240307": {
                "context_length": 200000,
                "cost_per_1k_input": 0.00025,
                "cost_per_1k_output": 0.00125,
                "capabilities": ["text", "vision"],
            },
            # Claude 4 models
            "claude-sonnet-4-20250514": {
                "context_length": 200000,
                "cost_per_1k_input": 0.003,
                "cost_per_1k_output": 0.015,
                "capabilities": ["text", "vision", "function_calling", "artifacts"],
            },
            "claude-haiku-4-5-20251001": {
                "context_length": 200000,
                "cost_per_1k_input": 0.0004,
                "cost_per_1k_output": 0.002,
                "capabilities": ["text", "vision", "function_calling"],
            },
        }

        resolved_model = self._resolve_model_name(model)
        return model_info.get(resolved_model, {})

    async def validate_credentials(self) -> bool:
        """Validate Anthropic API credentials."""
        try:
            client = self._get_client()

            # Try a minimal API call
            await client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}],
            )

            return True

        except Exception as e:
            logger.error(f"Credential validation failed: {e}")
            return False

    def _convert_to_provider_format(self, request: LLMRequest) -> dict[str, Any]:
        """Convert standardized request to Anthropic format."""
        messages = []

        for msg in request.messages:
            messages.append({"role": msg.role, "content": msg.content})

        return {
            "messages": messages,
            "extra_params": {
                "top_p": request.top_p,
                "stop_sequences": request.stop_sequences if request.stop_sequences else None,
            },
        }

    def _resolve_model_name(self, model: str) -> str:
        """Resolve short model names to full API names."""
        return self.model_mappings.get(model, model)

    def _convert_error(self, error: Exception) -> LLMError:
        """Convert Anthropic errors to standardized LLMError."""
        error_str = str(error).lower()

        if "rate" in error_str or "429" in error_str:
            error_type = "rate_limit"
            retry_after = 60  # Default retry after 60s
        elif "auth" in error_str or "401" in error_str:
            error_type = "authentication"
            retry_after = None
        elif "timeout" in error_str:
            error_type = "timeout"
            retry_after = 10
        else:
            error_type = "unknown"
            retry_after = None

        return LLMError(
            error_type=error_type,
            message=str(error),
            provider="anthropic",
            retry_after=retry_after,
        )
