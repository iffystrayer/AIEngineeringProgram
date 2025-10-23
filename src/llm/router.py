"""
LLM Router - Provider Factory and Intelligent Routing

Manages LLM provider selection, fallback chains, and cost optimization.

Features:
- Dynamic provider instantiation from configuration
- Intelligent routing based on task requirements
- Automatic fallback on provider failures
- Cost optimization (use cheaper models for simple tasks)
- Rate limit handling across providers
"""

import logging
from typing import Any, Optional, Union, List, Dict

from src.llm.base import (
    BaseLLMProvider,
    LLMError,
    LLMProvider,
    LLMRequest,
    LLMResponse,
    ModelTier,
    ProviderCapabilities,
    PROVIDER_CAPABILITIES,
)

logger = logging.getLogger(__name__)


class LLMRouter:
    """
    Factory and router for LLM providers.

    Handles provider instantiation, intelligent routing, and fallback chains.
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize LLM Router.

        Args:
            config: Configuration dictionary with provider settings
                {
                    "default_provider": "anthropic",
                    "default_model": "claude-3-sonnet",
                    "providers": {
                        "anthropic": {
                            "api_key": "sk-...",
                            "models": {"fast": "claude-3-haiku", "balanced": "claude-3-sonnet"}
                        },
                        "openai": {
                            "api_key": "sk-...",
                            "models": {"fast": "gpt-3.5-turbo", "balanced": "gpt-4"}
                        },
                        "ollama": {
                            "base_url": "http://localhost:11434",
                            "models": {"balanced": "llama3"}
                        }
                    },
                    "fallback_chain": ["anthropic", "openai", "ollama"],
                    "cost_optimization": true,
                    "rate_limit_strategy": "exponential_backoff"
                }
        """
        self.config = config
        self.providers: dict[str, BaseLLMProvider] = {}
        self.default_provider_name = config.get("default_provider", "anthropic")
        self.default_model = config.get("default_model")
        self.fallback_chain = config.get("fallback_chain", [self.default_provider_name])
        self.cost_optimization_enabled = config.get("cost_optimization", False)

        # Initialize providers
        self._initialize_providers()

        logger.info(
            f"LLMRouter initialized with default provider: {self.default_provider_name}"
        )

    def _initialize_providers(self) -> None:
        """Initialize all configured LLM providers."""
        provider_configs = self.config.get("providers", {})

        for provider_name, provider_config in provider_configs.items():
            try:
                provider = self._create_provider(provider_name, provider_config)
                self.providers[provider_name] = provider
                logger.info(f"Initialized provider: {provider_name}")
            except Exception as e:
                logger.error(f"Failed to initialize provider {provider_name}: {e}")

    def _create_provider(
        self, provider_name: str, provider_config: dict[str, Any]
    ) -> BaseLLMProvider:
        """
        Create a provider instance based on configuration.

        Args:
            provider_name: Name of the provider (anthropic, openai, etc.)
            provider_config: Provider-specific configuration

        Returns:
            Instantiated provider

        Raises:
            ValueError: If provider is not supported
        """
        # Import provider implementations dynamically
        if provider_name == "anthropic":
            from src.llm.providers.anthropic_provider import AnthropicProvider

            return AnthropicProvider(
                api_key=provider_config.get("api_key"),
                default_model=provider_config.get("default_model", "claude-3-sonnet"),
                **provider_config,
            )

        elif provider_name == "openai":
            from src.llm.providers.openai_provider import OpenAIProvider

            return OpenAIProvider(
                api_key=provider_config.get("api_key"),
                default_model=provider_config.get("default_model", "gpt-4"),
                **provider_config,
            )

        elif provider_name == "ollama":
            from src.llm.providers.ollama_provider import OllamaProvider

            # Extract explicit params to avoid duplicate keyword arguments
            base_url = provider_config.get("base_url", "http://localhost:11434")
            default_model = provider_config.get("default_model", "llama3.2:latest")

            # Remove explicit params from config dict
            extra_config = {k: v for k, v in provider_config.items()
                           if k not in ["base_url", "default_model"]}

            return OllamaProvider(
                base_url=base_url,
                default_model=default_model,
                **extra_config,
            )

        elif provider_name == "google":
            from src.llm.providers.google_provider import GoogleProvider

            return GoogleProvider(
                api_key=provider_config.get("api_key"),
                default_model=provider_config.get("default_model", "gemini-pro"),
                **provider_config,
            )

        else:
            raise ValueError(f"Unsupported provider: {provider_name}")

    async def route(
        self,
        prompt: Union[str, List[Dict[str, str]]],
        context: Optional[Any] = None,
        model_tier: ModelTier = ModelTier.BALANCED,
        provider: Optional[str] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Route request to appropriate LLM provider with intelligent fallback.

        Args:
            prompt: User prompt (string or message list)
            context: Optional context object for metadata
            model_tier: Desired model capability tier (fast, balanced, powerful)
            provider: Specific provider to use (bypasses intelligent routing)
            **kwargs: Additional parameters for LLM request

        Returns:
            LLMResponse from the selected provider

        Raises:
            LLMError: If all providers in fallback chain fail
        """
        # Convert prompt to standardized request
        request = self._build_request(prompt, model_tier, **kwargs)

        # Determine provider order (specific provider or fallback chain)
        if provider:
            provider_order = [provider]
        elif self.cost_optimization_enabled:
            provider_order = self._optimize_provider_selection(request, model_tier)
        else:
            provider_order = self.fallback_chain

        # Try providers in order
        last_error = None
        for provider_name in provider_order:
            if provider_name not in self.providers:
                logger.warning(f"Provider {provider_name} not configured, skipping")
                continue

            try:
                provider_instance = self.providers[provider_name]
                logger.debug(
                    f"Routing request to {provider_name} with model {request.model}"
                )

                response = await provider_instance.complete(request)
                response.provider = provider_name

                logger.info(
                    f"Request completed by {provider_name}: "
                    f"{response.total_tokens} tokens, {response.latency_ms}ms"
                )

                return response

            except Exception as e:
                logger.warning(
                    f"Provider {provider_name} failed: {e}. Trying next provider..."
                )
                last_error = e
                continue

        # All providers failed
        error_msg = (
            f"All providers in fallback chain failed. Last error: {last_error}"
        )
        logger.error(error_msg)
        raise LLMError(
            error_type="all_providers_failed",
            message=error_msg,
            provider="router",
        )

    def _build_request(
        self,
        prompt: Union[str, List[Dict[str, str]]],
        model_tier: ModelTier,
        **kwargs,
    ) -> LLMRequest:
        """
        Build standardized LLM request from prompt.

        Args:
            prompt: User prompt or message list
            model_tier: Model tier to use
            **kwargs: Additional request parameters

        Returns:
            Standardized LLMRequest
        """
        from src.llm.base import LLMMessage

        # Convert prompt to messages
        if isinstance(prompt, str):
            messages = [LLMMessage(role="user", content=prompt)]
        elif isinstance(prompt, list):
            messages = [
                LLMMessage(role=msg.get("role", "user"), content=msg.get("content", ""))
                for msg in prompt
            ]
        else:
            raise ValueError(f"Invalid prompt type: {type(prompt)}")

        # Select model based on tier and provider
        model = self._select_model_for_tier(model_tier)

        # Extract known LLMRequest parameters
        temperature = kwargs.pop("temperature", 0.7)
        max_tokens = kwargs.pop("max_tokens", 2000)
        stream = kwargs.pop("stream", False)
        stop_sequences = kwargs.pop("stop_sequences", [])
        top_p = kwargs.pop("top_p", 1.0)
        frequency_penalty = kwargs.pop("frequency_penalty", 0.0)
        presence_penalty = kwargs.pop("presence_penalty", 0.0)
        user_id = kwargs.pop("user_id", None)

        # Any remaining kwargs go into metadata (e.g., response_format, etc.)
        metadata = kwargs.pop("metadata", {})
        # Add any remaining kwargs to metadata
        metadata.update(kwargs)

        return LLMRequest(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            stop_sequences=stop_sequences,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            user_id=user_id,
            metadata=metadata,
        )

    def _select_model_for_tier(self, model_tier: ModelTier) -> str:
        """
        Select appropriate model for the given tier.

        Args:
            model_tier: Desired capability tier

        Returns:
            Model identifier
        """
        provider_config = self.config.get("providers", {}).get(
            self.default_provider_name, {}
        )
        models = provider_config.get("models", {})

        # Map tiers to model keys
        tier_map = {
            ModelTier.FAST: "fast",
            ModelTier.BALANCED: "balanced",
            ModelTier.POWERFUL: "powerful",
            ModelTier.LOCAL: "local",
        }

        model_key = tier_map.get(model_tier, "balanced")
        return models.get(model_key, self.default_model)

    def _optimize_provider_selection(
        self, request: LLMRequest, model_tier: ModelTier
    ) -> list[str]:
        """
        Optimize provider selection based on cost, capabilities, and requirements.

        Args:
            request: LLM request
            model_tier: Desired model tier

        Returns:
            Ordered list of providers to try
        """
        # For now, use default fallback chain
        # TODO: Implement intelligent cost optimization:
        # - Use cheaper providers for simple tasks
        # - Consider latency requirements
        # - Check provider capabilities match request needs
        # - Factor in current rate limit status

        return self.fallback_chain

    async def validate_all_providers(self) -> dict[str, bool]:
        """
        Validate credentials for all configured providers.

        Returns:
            Dictionary mapping provider names to validation status
        """
        results = {}

        for provider_name, provider in self.providers.items():
            try:
                is_valid = await provider.validate_credentials()
                results[provider_name] = is_valid
                logger.info(f"Provider {provider_name} validation: {is_valid}")
            except Exception as e:
                logger.error(f"Provider {provider_name} validation failed: {e}")
                results[provider_name] = False

        return results

    def get_provider_info(self) -> dict[str, Any]:
        """
        Get information about all configured providers.

        Returns:
            Dictionary with provider information
        """
        return {
            "default_provider": self.default_provider_name,
            "default_model": self.default_model,
            "active_providers": list(self.providers.keys()),
            "fallback_chain": self.fallback_chain,
            "cost_optimization": self.cost_optimization_enabled,
        }

    def __repr__(self) -> str:
        return (
            f"LLMRouter(default={self.default_provider_name}, "
            f"providers={list(self.providers.keys())})"
        )


# ============================================================================
# DEFAULT LLM ROUTER INSTANCE
# ============================================================================

def _create_default_router() -> LLMRouter:
    """
    Create a default LLM router instance from environment variables.

    Uses ANTHROPIC_API_KEY from environment for Anthropic provider.
    Falls back to Ollama (local) if no API key provided.

    Returns:
        Configured LLMRouter instance
    """
    import os

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    config = {
        "default_provider": "anthropic" if anthropic_key else "ollama",
        "default_model": "claude-sonnet-4-20250514" if anthropic_key else "llama3.2:latest",
        "providers": {},
        "fallback_chain": [],
        "cost_optimization": True,
    }

    # Add Anthropic if API key available
    if anthropic_key:
        config["providers"]["anthropic"] = {
            "api_key": anthropic_key,
            "default_model": "claude-sonnet-4-20250514",
            "models": {
                "fast": "claude-haiku-4-5-20250514",
                "balanced": "claude-sonnet-4-20250514",
                "powerful": "claude-sonnet-4-20250514",
            }
        }
        config["fallback_chain"].append("anthropic")

    # Add Ollama (local LLM - always available for cost-free development)
    config["providers"]["ollama"] = {
        "base_url": ollama_url,
        "default_model": "llama3.2:latest",
        "models": {
            "balanced": "llama3.2:latest",
            "fast": "llama3.2:latest",
        }
    }
    config["fallback_chain"].append("ollama")

    return LLMRouter(config)


# Global default router instance
llm_router = _create_default_router()
