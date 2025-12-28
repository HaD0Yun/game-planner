"""
llm_provider.py - LLM Provider Abstraction Layer for Game Planner

This module provides a unified interface for LLM providers (Anthropic, OpenAI)
with support for:
- Structured output parsing (JSON/Pydantic models)
- Temperature configuration (Actor: 0.6, Critic: 0.2)
- Error handling with exponential backoff retries
- JSON extraction from markdown code blocks

Based on Dual-Agent Actor-Critic Architecture (arXiv:2512.10501)
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import yaml
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# =============================================================================
# TYPE VARIABLES
# =============================================================================

T = TypeVar("T", bound=BaseModel)


# =============================================================================
# CONFIG LOADER
# =============================================================================


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from config.yaml.

    Args:
        config_path: Path to config file (default: game-planner/config.yaml)

    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"

    if not config_path.exists():
        logger.warning(f"Config file not found at {config_path}, using defaults")
        return {
            "orchestrator": {
                "actor_temperature": 0.6,
                "critic_temperature": 0.2,
            },
            "llm": {
                "provider": "anthropic",
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 8192,
            },
            "retries": {
                "max_attempts": 3,
                "backoff_base": 2.0,
            },
            "timeouts": {
                "actor_ms": 120000,
                "critic_ms": 60000,
            },
        }

    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# =============================================================================
# RESPONSE DATA CLASS
# =============================================================================


@dataclass
class LLMResponse:
    """
    Standardized LLM response across all providers.

    Tracks token usage for cost analysis.
    """

    content: str
    input_tokens: int
    output_tokens: int
    model: str
    latency_ms: float
    finish_reason: str = "stop"
    raw_response: Optional[Any] = None

    @property
    def total_tokens(self) -> int:
        """Total tokens used (input + output)."""
        return self.input_tokens + self.output_tokens


# =============================================================================
# JSON EXTRACTION UTILITIES
# =============================================================================


def extract_json(text: str) -> str:
    """
    Extract JSON from LLM response, handling markdown code blocks.

    Handles:
    - Raw JSON
    - JSON wrapped in ```json ... ```
    - JSON wrapped in ``` ... ```

    Args:
        text: Raw LLM response text

    Returns:
        Cleaned JSON string

    Raises:
        ValueError: If no valid JSON structure found
    """
    cleaned = text.strip()

    # Try to find JSON in code blocks first
    # Pattern for ```json ... ``` or ``` ... ```
    code_block_pattern = r"```(?:json)?\s*([\s\S]*?)```"
    matches = re.findall(code_block_pattern, cleaned)

    if matches:
        # Use the first match that looks like JSON
        for match in matches:
            match = match.strip()
            if match.startswith("{") or match.startswith("["):
                return match

    # Remove markdown code block markers if present at start/end
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    cleaned = cleaned.strip()

    # Verify it looks like JSON
    if not (cleaned.startswith("{") or cleaned.startswith("[")):
        raise ValueError(f"No valid JSON structure found in response: {text[:200]}...")

    return cleaned


def parse_json_response(text: str) -> Dict[str, Any]:
    """
    Parse JSON from LLM response.

    Args:
        text: Raw LLM response text

    Returns:
        Parsed JSON as dictionary

    Raises:
        ValueError: If JSON parsing fails
    """
    try:
        cleaned = extract_json(text)
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Invalid JSON in LLM response: {e}\nResponse: {text[:500]}..."
        )


def parse_to_model(text: str, model_class: Type[T]) -> T:
    """
    Parse LLM response into a Pydantic model.

    Args:
        text: Raw LLM response text
        model_class: Pydantic model class to parse into

    Returns:
        Validated Pydantic model instance

    Raises:
        ValueError: If parsing or validation fails
    """
    data = parse_json_response(text)
    return model_class.model_validate(data)


# =============================================================================
# RETRY DECORATOR
# =============================================================================


@dataclass
class RetryConfig:
    """Configuration for retry logic."""

    max_attempts: int = 3
    backoff_base: float = 2.0
    max_delay: float = 30.0
    retryable_exceptions: tuple = field(
        default_factory=lambda: (
            ConnectionError,
            TimeoutError,
            OSError,
        )
    )


async def retry_with_backoff(
    func,
    config: RetryConfig,
    *args,
    **kwargs,
):
    """
    Execute async function with exponential backoff retry.

    Args:
        func: Async function to execute
        config: Retry configuration
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Result of func

    Raises:
        Exception: Last exception if all retries fail
    """
    last_exception = None

    for attempt in range(config.max_attempts):
        try:
            return await func(*args, **kwargs)
        except config.retryable_exceptions as e:
            last_exception = e
            if attempt < config.max_attempts - 1:
                delay = min(config.backoff_base**attempt, config.max_delay)
                logger.warning(
                    f"Retry attempt {attempt + 1}/{config.max_attempts} "
                    f"after {delay:.1f}s due to: {e}"
                )
                await asyncio.sleep(delay)
            else:
                logger.error(f"All {config.max_attempts} retry attempts failed")

    raise last_exception  # type: ignore


# =============================================================================
# ABSTRACT BASE CLASS
# =============================================================================


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    The architecture is tool-agnostic, supporting multiple backends
    including Anthropic Claude and OpenAI GPT.
    """

    def __init__(self, retry_config: Optional[RetryConfig] = None):
        """
        Initialize provider with optional retry configuration.

        Args:
            retry_config: Configuration for retry logic
        """
        self.retry_config = retry_config or RetryConfig()

    @abstractmethod
    async def _generate_impl(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Internal implementation of generate.
        Subclasses must implement this method.
        """
        pass

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        retry: bool = True,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate a completion from the LLM with optional retry.

        Args:
            system_prompt: System instructions for the model
            user_prompt: User message content
            temperature: Sampling temperature (default 0.7)
            max_tokens: Maximum tokens to generate (default 4096)
            retry: Whether to retry on transient failures (default True)
            **kwargs: Additional provider-specific options

        Returns:
            LLMResponse with content and metadata
        """
        if retry:
            return await retry_with_backoff(
                self._generate_impl,
                self.retry_config,
                system_prompt,
                user_prompt,
                temperature,
                max_tokens,
                **kwargs,
            )
        else:
            return await self._generate_impl(
                system_prompt,
                user_prompt,
                temperature,
                max_tokens,
                **kwargs,
            )

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        model_class: Type[T],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        retry: bool = True,
        **kwargs: Any,
    ) -> tuple[T, LLMResponse]:
        """
        Generate and parse response into a Pydantic model.

        Args:
            system_prompt: System instructions for the model
            user_prompt: User message content
            model_class: Pydantic model class for output
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            retry: Whether to retry on transient failures
            **kwargs: Additional provider-specific options

        Returns:
            Tuple of (parsed model, raw LLMResponse)

        Raises:
            ValueError: If response cannot be parsed into model
        """
        response = await self.generate(
            system_prompt,
            user_prompt,
            temperature,
            max_tokens,
            retry,
            **kwargs,
        )

        parsed = parse_to_model(response.content, model_class)
        return parsed, response

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Used for context management to ensure the system
        remains within the LLM's effective context window.
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model identifier."""
        pass


# =============================================================================
# ANTHROPIC PROVIDER
# =============================================================================


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude API provider.

    From arXiv:2512.10501 Section 4.1:
    "We employ the Claude 4.5 Sonnet model via API for inference"
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        default_max_tokens: int = 8192,
        retry_config: Optional[RetryConfig] = None,
    ):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (or use ANTHROPIC_API_KEY env var)
            model: Model identifier (default: Claude Sonnet 4)
            default_max_tokens: Default max tokens for generation
            retry_config: Configuration for retry logic
        """
        super().__init__(retry_config)

        try:
            from anthropic import AsyncAnthropic
        except ImportError as e:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            ) from e

        import os

        resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not resolved_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = AsyncAnthropic(api_key=resolved_key)
        self.model = model
        self.default_max_tokens = default_max_tokens
        logger.info(f"Initialized Anthropic provider with model: {model}")

    async def _generate_impl(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate completion using Claude."""
        tokens_to_use = max_tokens if max_tokens else self.default_max_tokens
        start_time = time.time()

        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=tokens_to_use,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

            latency_ms = (time.time() - start_time) * 1000

            # Extract text content from response
            content = ""
            for block in message.content:
                if hasattr(block, "text"):
                    content += block.text

            return LLMResponse(
                content=content,
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
                model=self.model,
                latency_ms=latency_ms,
                finish_reason=message.stop_reason or "stop",
                raw_response=message,
            )

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count.
        Claude uses approximately 4 characters per token for English.
        """
        return len(text) // 4

    def get_model_name(self) -> str:
        return self.model


# =============================================================================
# OPENAI PROVIDER
# =============================================================================


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI GPT API provider.

    Alternative to Claude for testing generalizability.
    Supports GPT-4, GPT-4 Turbo, GPT-4o, and other models.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        default_max_tokens: int = 8192,
        retry_config: Optional[RetryConfig] = None,
    ):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (or use OPENAI_API_KEY env var)
            model: Model identifier (default: gpt-4o)
            default_max_tokens: Default max tokens for generation
            retry_config: Configuration for retry logic
        """
        super().__init__(retry_config)

        try:
            from openai import AsyncOpenAI
        except ImportError as e:
            raise ImportError(
                "openai package not installed. Install with: pip install openai"
            ) from e

        import os

        resolved_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not resolved_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = AsyncOpenAI(api_key=resolved_key)
        self.model = model
        self.default_max_tokens = default_max_tokens
        logger.info(f"Initialized OpenAI provider with model: {model}")

    async def _generate_impl(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate completion using GPT."""
        tokens_to_use = max_tokens if max_tokens else self.default_max_tokens
        start_time = time.time()

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                max_tokens=tokens_to_use,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )

            latency_ms = (time.time() - start_time) * 1000
            choice = response.choices[0]

            return LLMResponse(
                content=choice.message.content or "",
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
                model=self.model,
                latency_ms=latency_ms,
                finish_reason=choice.finish_reason or "stop",
                raw_response=response,
            )

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def count_tokens(self, text: str) -> int:
        """Estimate token count (GPT uses ~4 chars per token for English)."""
        return len(text) // 4

    def get_model_name(self) -> str:
        return self.model


# =============================================================================
# MOCK PROVIDER (for Testing)
# =============================================================================


class MockLLMProvider(BaseLLMProvider):
    """
    Mock provider for testing without API calls.

    Useful for:
    - Unit testing
    - Development without API costs
    - Reproducible test scenarios
    """

    def __init__(
        self,
        responses: Optional[Union[Dict[int, str], List[str]]] = None,
        default_response: Optional[str] = None,
        model: str = "mock-model",
        retry_config: Optional[RetryConfig] = None,
    ):
        """
        Initialize mock provider.

        Args:
            responses: Dict mapping call number (1-indexed) to response content,
                      or list of responses to return in order
            default_response: Default response when no specific response configured
            model: Mock model name
            retry_config: Configuration for retry logic
        """
        super().__init__(retry_config)

        # Convert list to dict if provided
        if isinstance(responses, list):
            self._responses = {i + 1: r for i, r in enumerate(responses)}
        else:
            self._responses: Dict[int, str] = responses if responses is not None else {}

        self._default_response = default_response or self._create_default_gdd_response()
        self.model = model
        self.call_count = 0
        self.call_history: List[Dict[str, Any]] = []
        logger.info("Initialized Mock LLM provider")

    def _create_default_gdd_response(self) -> str:
        """Create a minimal valid GDD JSON response for testing."""
        return json.dumps(
            {
                "schema_version": "1.0",
                "meta": {
                    "title": "Mock Game",
                    "genres": ["action"],
                    "target_platforms": ["pc"],
                    "target_audience": "Test audience for mock game development",
                    "unique_selling_point": "This is a mock game for testing purposes only",
                    "estimated_dev_time_weeks": 10,
                },
                "core_loop": {
                    "primary_actions": ["Action1", "Action2"],
                    "challenge_description": "Mock challenge description for testing",
                    "reward_description": "Mock reward description for testing",
                    "loop_description": "Mock loop description for testing",
                    "session_length_minutes": 30,
                },
                "systems": [
                    {
                        "name": "Combat System",
                        "type": "combat",
                        "description": "Mock combat system for testing",
                        "mechanics": ["Attack", "Defend"],
                    },
                    {
                        "name": "Movement System",
                        "type": "movement",
                        "description": "Mock movement system for testing",
                        "mechanics": ["Walk", "Run"],
                    },
                    {
                        "name": "Inventory System",
                        "type": "inventory",
                        "description": "Mock inventory system for testing",
                        "mechanics": ["Store", "Retrieve"],
                    },
                ],
                "progression": {
                    "type": "linear",
                    "milestones": [
                        {
                            "name": "Milestone 1",
                            "description": "First milestone",
                            "unlock_condition": "Complete tutorial",
                        },
                        {
                            "name": "Milestone 2",
                            "description": "Second milestone",
                            "unlock_condition": "Complete level 1",
                        },
                        {
                            "name": "Milestone 3",
                            "description": "Third milestone",
                            "unlock_condition": "Complete level 2",
                        },
                        {
                            "name": "Milestone 4",
                            "description": "Fourth milestone",
                            "unlock_condition": "Complete level 3",
                        },
                        {
                            "name": "Milestone 5",
                            "description": "Fifth milestone",
                            "unlock_condition": "Complete game",
                        },
                    ],
                    "difficulty_curve_description": "Mock difficulty curve for testing",
                },
                "narrative": {
                    "setting": "Mock fantasy world for testing",
                    "story_premise": "Mock story premise for testing the game planner",
                    "themes": ["Adventure", "Testing"],
                    "narrative_delivery": ["dialogue"],
                    "story_structure": "Linear progression with mock story beats",
                },
                "technical": {
                    "recommended_engine": "unity",
                    "art_style": "pixel_art",
                    "key_technologies": ["Unity", "C#"],
                    "audio": {
                        "music_style": "Retro chiptune",
                        "sound_categories": ["Combat", "UI"],
                    },
                },
            },
            indent=2,
        )

    async def _generate_impl(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> LLMResponse:
        """Return mock response."""
        self.call_count += 1
        self.call_history.append(
            {
                "call_number": self.call_count,
                "system": system_prompt,
                "user": user_prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "kwargs": kwargs,
            }
        )

        # Return configured response or default
        content = self._responses.get(self.call_count, self._default_response)

        # Simulate some latency
        await asyncio.sleep(0.01)

        return LLMResponse(
            content=content,
            input_tokens=len(system_prompt + user_prompt) // 4,
            output_tokens=len(content) // 4,
            model=self.model,
            latency_ms=10.0,
        )

    def count_tokens(self, text: str) -> int:
        return len(text) // 4

    def get_model_name(self) -> str:
        return self.model

    def reset(self) -> None:
        """Reset call history for new test."""
        self.call_count = 0
        self.call_history = []

    def set_response(self, call_number: int, response: str) -> None:
        """Set response for a specific call number (1-indexed)."""
        self._responses[call_number] = response

    def set_responses(self, responses: List[str]) -> None:
        """Set responses in order."""
        self._responses = {i + 1: r for i, r in enumerate(responses)}

    def get_last_call(self) -> Optional[Dict[str, Any]]:
        """Get the last call details."""
        return self.call_history[-1] if self.call_history else None


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def create_provider(
    provider_type: str,
    config: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> BaseLLMProvider:
    """
    Factory function to create LLM providers.

    Args:
        provider_type: One of "anthropic", "openai", "mock"
        config: Optional configuration dictionary (loaded from config.yaml if not provided)
        **kwargs: Provider-specific configuration overrides

    Returns:
        Configured LLM provider instance

    Example:
        # Using Anthropic with default config
        provider = create_provider("anthropic")

        # Using OpenAI with custom model
        provider = create_provider("openai", model="gpt-4-turbo")

        # Using mock for testing
        provider = create_provider("mock")
    """
    providers: Dict[str, type] = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "mock": MockLLMProvider,
    }

    if provider_type not in providers:
        raise ValueError(
            f"Unknown provider: {provider_type}. Available: {list(providers.keys())}"
        )

    # Load config if not provided
    if config is None:
        config = load_config()

    # Get LLM config
    llm_config = config.get("llm", {})
    retry_config_dict = config.get("retries", {})

    # Create retry config
    retry_config = RetryConfig(
        max_attempts=retry_config_dict.get("max_attempts", 3),
        backoff_base=retry_config_dict.get("backoff_base", 2.0),
    )

    # Build provider kwargs
    provider_kwargs: Dict[str, Any] = {"retry_config": retry_config}

    if provider_type == "anthropic":
        provider_kwargs["model"] = kwargs.get(
            "model", llm_config.get("model", "claude-sonnet-4-20250514")
        )
        provider_kwargs["default_max_tokens"] = kwargs.get(
            "max_tokens", llm_config.get("max_tokens", 8192)
        )
        if "api_key" in kwargs:
            provider_kwargs["api_key"] = kwargs["api_key"]

    elif provider_type == "openai":
        provider_kwargs["model"] = kwargs.get("model", "gpt-4o")
        provider_kwargs["default_max_tokens"] = kwargs.get(
            "max_tokens", llm_config.get("max_tokens", 8192)
        )
        if "api_key" in kwargs:
            provider_kwargs["api_key"] = kwargs["api_key"]

    elif provider_type == "mock":
        if "responses" in kwargs:
            provider_kwargs["responses"] = kwargs["responses"]
        if "default_response" in kwargs:
            provider_kwargs["default_response"] = kwargs["default_response"]
        if "model" in kwargs:
            provider_kwargs["model"] = kwargs["model"]

    return providers[provider_type](**provider_kwargs)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def get_actor_temperature(config: Optional[Dict[str, Any]] = None) -> float:
    """Get the configured temperature for the Actor (Game Designer) agent."""
    if config is None:
        config = load_config()
    return config.get("orchestrator", {}).get("actor_temperature", 0.6)


def get_critic_temperature(config: Optional[Dict[str, Any]] = None) -> float:
    """Get the configured temperature for the Critic (Game Reviewer) agent."""
    if config is None:
        config = load_config()
    return config.get("orchestrator", {}).get("critic_temperature", 0.2)


def get_max_iterations(config: Optional[Dict[str, Any]] = None) -> int:
    """Get the configured maximum iterations for the refinement loop."""
    if config is None:
        config = load_config()
    return config.get("orchestrator", {}).get("max_iterations", 3)
