"""
LLM Configuration Loader

Loads LLM configuration from environment variables and provides
a standardized configuration dictionary for the LLM Router.
"""

import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


def load_llm_config(
    provider: str = "anthropic",
    enable_cost_optimization: Optional[bool] = None,
    enable_fallback: bool = True,
) -> dict[str, Any]:
    """
    Load LLM configuration from environment variables.

    Args:
        provider: Primary LLM provider (default: "anthropic")
        enable_cost_optimization: Enable intelligent cost optimization
                                 (default: read from LLM_COST_OPTIMIZATION env)
        enable_fallback: Enable fallback to other providers (default: True)

    Returns:
        Configuration dictionary for LLMRouter

    Example:
        >>> config = load_llm_config()
        >>> router = LLMRouter(config)
    """
    # Read cost optimization setting
    if enable_cost_optimization is None:
        enable_cost_optimization = (
            os.getenv("LLM_COST_OPTIMIZATION", "true").lower() == "true"
        )

    config = {
        "default_provider": provider,
        "cost_optimization": enable_cost_optimization,
        "rate_limit_strategy": "exponential_backoff",
    }

    # Load provider-specific configuration
    if provider == "anthropic":
        config.update(_load_anthropic_config())
    elif provider == "openai":
        config.update(_load_openai_config())
    elif provider == "ollama":
        config.update(_load_ollama_config())
    else:
        logger.warning(f"Unknown provider: {provider}, using default config")

    # Setup fallback chain
    if enable_fallback:
        config["fallback_chain"] = _build_fallback_chain(provider)
    else:
        config["fallback_chain"] = [provider]

    logger.info(
        f"LLM config loaded: provider={provider}, "
        f"cost_optimization={enable_cost_optimization}"
    )

    return config


def _load_anthropic_config() -> dict[str, Any]:
    """Load Anthropic (Claude) configuration from environment."""
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not set in environment. "
            "Please set it in your .env file."
        )

    # Model configuration
    default_model = os.getenv(
        "ANTHROPIC_DEFAULT_MODEL", "claude-sonnet-4-20250514"
    )
    fast_model = os.getenv(
        "ANTHROPIC_MODEL_FAST", "claude-haiku-4-5-20251001"
    )
    balanced_model = os.getenv(
        "ANTHROPIC_MODEL_BALANCED", "claude-sonnet-4-20250514"
    )
    powerful_model = os.getenv(
        "ANTHROPIC_MODEL_POWERFUL", "claude-sonnet-4-20250514"
    )

    return {
        "default_model": default_model,
        "providers": {
            "anthropic": {
                "api_key": api_key,
                "default_model": default_model,
                "models": {
                    "fast": fast_model,
                    "balanced": balanced_model,
                    "powerful": powerful_model,
                },
                "timeout": int(os.getenv("ANTHROPIC_TIMEOUT", "60")),
                "max_retries": int(os.getenv("ANTHROPIC_MAX_RETRIES", "3")),
            }
        },
    }


def _load_openai_config() -> dict[str, Any]:
    """Load OpenAI configuration from environment."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        logger.warning("OPENAI_API_KEY not set, OpenAI provider will not be available")
        return {"providers": {}}

    default_model = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4")
    fast_model = os.getenv("OPENAI_MODEL_FAST", "gpt-3.5-turbo")
    balanced_model = os.getenv("OPENAI_MODEL_BALANCED", "gpt-4")
    powerful_model = os.getenv("OPENAI_MODEL_POWERFUL", "gpt-4-turbo")

    return {
        "default_model": default_model,
        "providers": {
            "openai": {
                "api_key": api_key,
                "default_model": default_model,
                "models": {
                    "fast": fast_model,
                    "balanced": balanced_model,
                    "powerful": powerful_model,
                },
                "timeout": int(os.getenv("OPENAI_TIMEOUT", "60")),
                "max_retries": int(os.getenv("OPENAI_MAX_RETRIES", "3")),
            }
        },
    }


def _load_ollama_config() -> dict[str, Any]:
    """Load Ollama (local) configuration from environment."""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    default_model = os.getenv("OLLAMA_DEFAULT_MODEL", "llama3")
    fast_model = os.getenv("OLLAMA_MODEL_FAST", "llama3")
    balanced_model = os.getenv("OLLAMA_MODEL_BALANCED", "llama3")
    powerful_model = os.getenv("OLLAMA_MODEL_POWERFUL", "llama3")

    return {
        "default_model": default_model,
        "providers": {
            "ollama": {
                "base_url": base_url,
                "default_model": default_model,
                "models": {
                    "fast": fast_model,
                    "balanced": balanced_model,
                    "powerful": powerful_model,
                },
                "timeout": int(os.getenv("OLLAMA_TIMEOUT", "120")),
                "max_retries": int(os.getenv("OLLAMA_MAX_RETRIES", "2")),
            }
        },
    }


def _build_fallback_chain(primary_provider: str) -> list[str]:
    """
    Build intelligent fallback chain based on available providers.

    Args:
        primary_provider: Primary provider to use first

    Returns:
        Ordered list of providers for fallback
    """
    fallback_chain = [primary_provider]

    # Check which additional providers are configured
    if primary_provider != "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
        fallback_chain.append("anthropic")

    if primary_provider != "openai" and os.getenv("OPENAI_API_KEY"):
        fallback_chain.append("openai")

    if primary_provider != "ollama" and os.getenv("OLLAMA_BASE_URL"):
        # Ollama (local) as last resort
        fallback_chain.append("ollama")

    return fallback_chain


def get_model_tier_from_task_type(task_type: str) -> str:
    """
    Recommend model tier based on task type.

    Args:
        task_type: Type of task (e.g., "summary", "code_generation", "planning")

    Returns:
        Recommended tier: "fast", "balanced", or "powerful"

    Example:
        >>> tier = get_model_tier_from_task_type("summary")
        >>> # Returns "fast" for simple summarization
    """
    from src.llm.base import ModelTier

    # Fast tier tasks
    fast_tasks = {
        "summary",
        "translation",
        "simple_query",
        "keyword_extraction",
        "classification",
        "sentiment_analysis",
        "data_validation",
    }

    # Powerful tier tasks
    powerful_tasks = {
        "architecture_design",
        "complex_planning",
        "strategic_decision",
        "multi_step_reasoning",
        "critical_analysis",
    }

    if task_type.lower() in fast_tasks:
        return ModelTier.FAST
    elif task_type.lower() in powerful_tasks:
        return ModelTier.POWERFUL
    else:
        return ModelTier.BALANCED


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = "claude-sonnet-4-20250514",
) -> float:
    """
    Estimate cost for a given token usage.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model identifier

    Returns:
        Estimated cost in USD

    Example:
        >>> cost = estimate_cost(1000, 500, "claude-haiku-4-5-20251001")
        >>> print(f"Estimated cost: ${cost:.4f}")
    """
    # Pricing per 1K tokens (as of 2025)
    pricing = {
        # Claude 4 models
        "claude-sonnet-4-20250514": (0.003, 0.015),
        "claude-haiku-4-5-20251001": (0.0004, 0.002),
        # Claude 3 models
        "claude-3-opus-20240229": (0.015, 0.075),
        "claude-3-sonnet-20240229": (0.003, 0.015),
        "claude-3-haiku-20240307": (0.00025, 0.00125),
    }

    input_cost_per_1k, output_cost_per_1k = pricing.get(
        model, (0.003, 0.015)  # Default to Sonnet pricing
    )

    total_cost = (
        (input_tokens / 1000) * input_cost_per_1k
        + (output_tokens / 1000) * output_cost_per_1k
    )

    return total_cost


def validate_environment() -> dict[str, bool]:
    """
    Validate LLM configuration in environment.

    Returns:
        Dictionary of validation results

    Example:
        >>> results = validate_environment()
        >>> if not results["anthropic_api_key"]:
        ...     print("Please set ANTHROPIC_API_KEY")
    """
    results = {
        "anthropic_api_key": bool(os.getenv("ANTHROPIC_API_KEY")),
        "anthropic_model_configured": bool(
            os.getenv("ANTHROPIC_DEFAULT_MODEL")
            or os.getenv("ANTHROPIC_MODEL_BALANCED")
        ),
        "cost_optimization_enabled": (
            os.getenv("LLM_COST_OPTIMIZATION", "true").lower() == "true"
        ),
        "has_env_file": os.path.exists(".env"),
    }

    # Log warnings for missing configuration
    if not results["anthropic_api_key"]:
        logger.warning(
            "ANTHROPIC_API_KEY not set. Please configure in .env file."
        )

    if not results["has_env_file"]:
        logger.warning(
            ".env file not found. Copy .env.example to .env and configure."
        )

    return results
