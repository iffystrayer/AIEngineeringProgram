"""
LLM Provider Abstraction Layer

Provides a provider-agnostic interface for LLM interactions, allowing seamless
switching between Claude, OpenAI, Gemini, Ollama, and other providers.

Architecture: Strategy Pattern with Provider Adapters
- BaseLLMProvider: Abstract interface all providers must implement
- Specific adapters: ClaudeProvider, OpenAIProvider, GeminiProvider, etc.
- LLMRouter: Factory for creating and managing providers

This design prevents vendor lock-in and enables:
- Easy provider switching via configuration
- Cost optimization (use cheaper models for simple tasks)
- Fallback chains (try Claude, fallback to OpenAI if rate limited)
- Local/privacy mode (Ollama for sensitive data)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Optional
from uuid import UUID, uuid4


class LLMProvider(Enum):
    """Supported LLM providers."""

    ANTHROPIC = "anthropic"  # Claude (Sonnet, Opus, Haiku)
    OPENAI = "openai"  # GPT-4, GPT-3.5
    GOOGLE = "google"  # Gemini Pro, Ultra
    OLLAMA = "ollama"  # Local models (Llama, Mistral, etc.)
    AZURE_OPENAI = "azure_openai"  # Enterprise OpenAI
    OPENROUTER = "openrouter"  # Multi-provider gateway
    DEEPSEEK = "deepseek"  # DeepSeek models
    GROQ = "groq"  # Fast inference


class ModelTier(Enum):
    """Model capability tiers for cost optimization."""

    FAST = "fast"  # Fast, cheap models (Haiku, GPT-3.5-turbo)
    BALANCED = "balanced"  # Mid-tier models (Sonnet, GPT-4)
    POWERFUL = "powerful"  # Most capable (Opus, GPT-4-turbo)
    LOCAL = "local"  # Local models via Ollama


@dataclass
class LLMMessage:
    """Standardized message format across all providers."""

    role: str  # "system", "user", "assistant"
    content: str
    name: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMRequest:
    """Standardized LLM request format."""

    messages: list[LLMMessage]
    model: Optional[str] = None  # Provider-specific model name
    temperature: float = 0.7
    max_tokens: int = 2000
    stream: bool = False
    stop_sequences: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Advanced parameters
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    user_id: Optional[str] = None  # For tracking/rate limiting


@dataclass
class LLMResponse:
    """Standardized LLM response format."""

    request_id: UUID = field(default_factory=uuid4)
    content: str = ""
    model: str = ""
    provider: str = ""
    finish_reason: str = "stop"  # "stop", "length", "content_filter"

    # Token usage
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    latency_ms: Optional[int] = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)
    raw_response: Optional[dict] = None


@dataclass
class LLMError:
    """Standardized error format for LLM failures."""

    error_type: str  # "rate_limit", "authentication", "timeout", "invalid_request"
    message: str
    provider: str
    retry_after: Optional[int] = None  # Seconds to wait before retry
    status_code: Optional[int] = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM providers.

    All provider adapters must implement these methods to ensure consistent
    interface across different LLM services.
    """

    def __init__(
        self,
        api_key: str,
        default_model: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        **kwargs,
    ):
        """
        Initialize LLM provider.

        Args:
            api_key: Provider API key
            default_model: Default model to use if not specified in request
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for transient failures
            **kwargs: Provider-specific configuration
        """
        self.api_key = api_key
        self.default_model = default_model
        self.timeout = timeout
        self.max_retries = max_retries
        self.config = kwargs

    @abstractmethod
    async def complete(self, request: LLMRequest) -> LLMResponse:
        """
        Generate completion for the given request.

        Args:
            request: Standardized LLM request

        Returns:
            Standardized LLM response

        Raises:
            LLMError: On provider-specific errors
        """
        pass

    @abstractmethod
    async def stream_complete(
        self, request: LLMRequest
    ) -> AsyncIterator[LLMResponse]:
        """
        Generate streaming completion for the given request.

        Args:
            request: Standardized LLM request

        Yields:
            Partial LLM responses as they arrive

        Raises:
            LLMError: On provider-specific errors
        """
        pass

    @abstractmethod
    async def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Count tokens for the given text.

        Args:
            text: Text to tokenize
            model: Model to use for tokenization (provider-specific)

        Returns:
            Number of tokens
        """
        pass

    @abstractmethod
    def get_model_info(self, model: str) -> dict[str, Any]:
        """
        Get information about a specific model.

        Args:
            model: Model identifier

        Returns:
            Dictionary with model info (context_length, cost_per_token, etc.)
        """
        pass

    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        Validate API credentials are working.

        Returns:
            True if credentials are valid, False otherwise
        """
        pass

    def _convert_to_provider_format(self, request: LLMRequest) -> dict[str, Any]:
        """
        Convert standardized request to provider-specific format.

        Must be implemented by each provider adapter.
        """
        raise NotImplementedError

    def _convert_from_provider_format(self, response: Any) -> LLMResponse:
        """
        Convert provider-specific response to standardized format.

        Must be implemented by each provider adapter.
        """
        raise NotImplementedError

    async def _handle_rate_limit(self, error: Any) -> None:
        """
        Handle rate limit errors with exponential backoff.

        Can be overridden by specific providers for custom rate limit handling.
        """
        import asyncio
        from random import uniform

        # Exponential backoff: 1s, 2s, 4s, 8s, etc.
        base_delay = 1
        max_delay = 60

        for attempt in range(self.max_retries):
            delay = min(base_delay * (2 ** attempt), max_delay)
            # Add jitter to prevent thundering herd
            jittered_delay = delay * uniform(0.8, 1.2)

            await asyncio.sleep(jittered_delay)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.default_model})"


class ProviderCapabilities:
    """
    Defines capabilities for each provider.

    Used for intelligent routing and fallback decisions.
    """

    def __init__(
        self,
        supports_streaming: bool = True,
        supports_function_calling: bool = False,
        supports_vision: bool = False,
        supports_json_mode: bool = False,
        max_context_length: int = 4096,
        cost_per_1k_input_tokens: float = 0.0,
        cost_per_1k_output_tokens: float = 0.0,
        typical_latency_ms: int = 1000,
    ):
        self.supports_streaming = supports_streaming
        self.supports_function_calling = supports_function_calling
        self.supports_vision = supports_vision
        self.supports_json_mode = supports_json_mode
        self.max_context_length = max_context_length
        self.cost_per_1k_input_tokens = cost_per_1k_input_tokens
        self.cost_per_1k_output_tokens = cost_per_1k_output_tokens
        self.typical_latency_ms = typical_latency_ms


# Provider capability definitions
PROVIDER_CAPABILITIES = {
    LLMProvider.ANTHROPIC: {
        # Claude 3 models
        "claude-3-opus": ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=True,
            supports_json_mode=False,
            max_context_length=200000,
            cost_per_1k_input_tokens=0.015,
            cost_per_1k_output_tokens=0.075,
            typical_latency_ms=2000,
        ),
        "claude-3-sonnet": ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=True,
            supports_json_mode=False,
            max_context_length=200000,
            cost_per_1k_input_tokens=0.003,
            cost_per_1k_output_tokens=0.015,
            typical_latency_ms=1500,
        ),
        "claude-3-haiku": ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=False,
            supports_vision=True,
            supports_json_mode=False,
            max_context_length=200000,
            cost_per_1k_input_tokens=0.00025,
            cost_per_1k_output_tokens=0.00125,
            typical_latency_ms=800,
        ),
        # Claude 4 models
        "claude-sonnet-4": ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=True,
            supports_json_mode=True,
            max_context_length=200000,
            cost_per_1k_input_tokens=0.003,
            cost_per_1k_output_tokens=0.015,
            typical_latency_ms=1500,
        ),
        "claude-haiku-4": ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=True,
            supports_json_mode=True,
            max_context_length=200000,
            cost_per_1k_input_tokens=0.0004,
            cost_per_1k_output_tokens=0.002,
            typical_latency_ms=600,
        ),
        "claude-haiku-4-5": ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=True,
            supports_json_mode=True,
            max_context_length=200000,
            cost_per_1k_input_tokens=0.0004,
            cost_per_1k_output_tokens=0.002,
            typical_latency_ms=600,
        ),
    },
    LLMProvider.OPENAI: {
        "gpt-4-turbo": ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=True,
            supports_json_mode=True,
            max_context_length=128000,
            cost_per_1k_input_tokens=0.01,
            cost_per_1k_output_tokens=0.03,
            typical_latency_ms=2000,
        ),
        "gpt-4": ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=False,
            supports_json_mode=True,
            max_context_length=8192,
            cost_per_1k_input_tokens=0.03,
            cost_per_1k_output_tokens=0.06,
            typical_latency_ms=3000,
        ),
        "gpt-3.5-turbo": ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=False,
            supports_json_mode=True,
            max_context_length=16385,
            cost_per_1k_input_tokens=0.0005,
            cost_per_1k_output_tokens=0.0015,
            typical_latency_ms=800,
        ),
    },
    LLMProvider.OLLAMA: {
        "llama3": ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=False,
            supports_vision=False,
            supports_json_mode=True,
            max_context_length=8192,
            cost_per_1k_input_tokens=0.0,  # Local, no cost
            cost_per_1k_output_tokens=0.0,
            typical_latency_ms=3000,
        ),
        "mistral": ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=False,
            supports_vision=False,
            supports_json_mode=True,
            max_context_length=8192,
            cost_per_1k_input_tokens=0.0,
            cost_per_1k_output_tokens=0.0,
            typical_latency_ms=2500,
        ),
    },
}
