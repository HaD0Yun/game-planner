"""
test_llm_provider.py - Tests for LLM Provider Abstraction Layer

Tests cover:
- Provider creation via factory function
- Mock provider functionality
- JSON extraction from various formats
- Pydantic model parsing
- Retry configuration
- Temperature configuration
- Token counting
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_provider import (
    LLMResponse,
    MockLLMProvider,
    RetryConfig,
    create_provider,
    extract_json,
    get_actor_temperature,
    get_critic_temperature,
    get_max_iterations,
    load_config,
    parse_json_response,
    parse_to_model,
    retry_with_backoff,
)
from models import CriticFeedback, Decision, GameDesignDocument


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_provider():
    """Create a fresh mock provider for each test."""
    return MockLLMProvider()


@pytest.fixture
def sample_gdd_json():
    """Create a sample GDD JSON string."""
    return json.dumps(
        {
            "schema_version": "1.0",
            "meta": {
                "title": "Test Game",
                "genres": ["action", "rpg"],
                "target_platforms": ["pc"],
                "target_audience": "Gamers who enjoy action RPGs with deep combat",
                "unique_selling_point": "Revolutionary combat system with time manipulation",
                "estimated_dev_time_weeks": 52,
            },
            "core_loop": {
                "primary_actions": ["Fight", "Explore", "Upgrade"],
                "challenge_description": "Defeat enemies using time-based combat",
                "reward_description": "Gain experience and new abilities",
                "loop_description": "Fight -> Loot -> Upgrade -> Explore -> Repeat",
                "session_length_minutes": 45,
            },
            "systems": [
                {
                    "name": "Combat",
                    "type": "combat",
                    "description": "Time-based combat system with dodge mechanics",
                    "mechanics": ["Attack", "Dodge", "Time Slow"],
                },
                {
                    "name": "Movement",
                    "type": "movement",
                    "description": "Fluid movement system for exploration",
                    "mechanics": ["Walk", "Run", "Dash"],
                },
                {
                    "name": "Inventory",
                    "type": "inventory",
                    "description": "Item management system",
                    "mechanics": ["Store", "Equip", "Use"],
                },
            ],
            "progression": {
                "type": "skill_tree",
                "milestones": [
                    {
                        "name": "Tutorial Complete",
                        "description": "Finished tutorial",
                        "unlock_condition": "Complete tutorial",
                    },
                    {
                        "name": "First Boss",
                        "description": "Defeat first boss",
                        "unlock_condition": "Defeat boss",
                    },
                    {
                        "name": "Mid Game",
                        "description": "Reach mid game",
                        "unlock_condition": "Complete act 1",
                    },
                    {
                        "name": "Late Game",
                        "description": "Reach late game",
                        "unlock_condition": "Complete act 2",
                    },
                    {
                        "name": "Game Complete",
                        "description": "Finish the game",
                        "unlock_condition": "Defeat final boss",
                    },
                ],
                "difficulty_curve_description": "Gradual increase in difficulty",
            },
            "narrative": {
                "setting": "Fantasy world with time magic",
                "story_premise": "A hero discovers the power to manipulate time",
                "themes": ["Time", "Power", "Sacrifice"],
                "narrative_delivery": ["cutscenes", "dialogue"],
                "story_structure": "Three-act structure with branching paths",
            },
            "technical": {
                "recommended_engine": "unity",
                "art_style": "stylized",
                "key_technologies": ["Unity", "C#", "Physics"],
                "audio": {
                    "music_style": "Orchestral",
                    "sound_categories": ["Combat", "Ambient", "UI"],
                },
            },
        },
        indent=2,
    )


@pytest.fixture
def sample_critic_feedback_json():
    """Create a sample critic feedback JSON string."""
    return json.dumps(
        {
            "decision": "approve",
            "blocking_issues": [],
            "feasibility_score": 8,
            "coherence_score": 9,
            "fun_factor_score": 8,
            "completeness_score": 9,
            "originality_score": 7,
            "review_notes": "Solid design overall.",
        }
    )


# =============================================================================
# JSON EXTRACTION TESTS
# =============================================================================


class TestExtractJson:
    """Tests for JSON extraction from various formats."""

    def test_extract_raw_json(self):
        """Test extracting raw JSON."""
        raw = '{"key": "value"}'
        assert extract_json(raw) == '{"key": "value"}'

    def test_extract_json_with_markdown_code_block(self):
        """Test extracting JSON from ```json ... ``` block."""
        text = '```json\n{"key": "value"}\n```'
        assert extract_json(text) == '{"key": "value"}'

    def test_extract_json_with_plain_code_block(self):
        """Test extracting JSON from ``` ... ``` block."""
        text = '```\n{"key": "value"}\n```'
        assert extract_json(text) == '{"key": "value"}'

    def test_extract_json_with_surrounding_text(self):
        """Test extracting JSON with text around code block."""
        text = 'Here is the JSON:\n```json\n{"key": "value"}\n```\nEnd of response.'
        assert extract_json(text) == '{"key": "value"}'

    def test_extract_json_array(self):
        """Test extracting JSON array."""
        raw = "[1, 2, 3]"
        assert extract_json(raw) == "[1, 2, 3]"

    def test_extract_json_with_whitespace(self):
        """Test extracting JSON with extra whitespace."""
        text = '\n\n  {"key": "value"}  \n\n'
        assert extract_json(text) == '{"key": "value"}'

    def test_extract_json_fails_for_invalid(self):
        """Test that extraction fails for non-JSON."""
        with pytest.raises(ValueError, match="No valid JSON structure found"):
            extract_json("This is not JSON")


class TestParseJsonResponse:
    """Tests for JSON parsing."""

    def test_parse_valid_json(self):
        """Test parsing valid JSON."""
        text = '{"key": "value"}'
        result = parse_json_response(text)
        assert result == {"key": "value"}

    def test_parse_json_from_markdown(self):
        """Test parsing JSON from markdown code block."""
        text = '```json\n{"key": "value"}\n```'
        result = parse_json_response(text)
        assert result == {"key": "value"}

    def test_parse_invalid_json(self):
        """Test that parsing fails for invalid JSON."""
        with pytest.raises(ValueError, match="Invalid JSON"):
            parse_json_response("```json\n{invalid}\n```")


class TestParseToModel:
    """Tests for Pydantic model parsing."""

    def test_parse_to_gdd(self, sample_gdd_json):
        """Test parsing GDD JSON to model."""
        gdd = parse_to_model(sample_gdd_json, GameDesignDocument)
        assert gdd.meta.title == "Test Game"
        assert len(gdd.systems) == 3

    def test_parse_to_critic_feedback(self, sample_critic_feedback_json):
        """Test parsing critic feedback JSON to model."""
        feedback = parse_to_model(sample_critic_feedback_json, CriticFeedback)
        assert feedback.decision == Decision.APPROVE
        assert feedback.feasibility_score == 8

    def test_parse_invalid_model(self):
        """Test that parsing fails for invalid model data."""
        invalid_json = '{"invalid": "data"}'
        with pytest.raises(Exception):  # ValidationError or ValueError
            parse_to_model(invalid_json, GameDesignDocument)


# =============================================================================
# MOCK PROVIDER TESTS
# =============================================================================


class TestMockProvider:
    """Tests for MockLLMProvider."""

    def test_mock_provider_creation(self):
        """Test creating a mock provider."""
        provider = MockLLMProvider()
        assert provider.get_model_name() == "mock-model"
        assert provider.call_count == 0

    def test_mock_provider_with_custom_model(self):
        """Test mock provider with custom model name."""
        provider = MockLLMProvider(model="custom-mock")
        assert provider.get_model_name() == "custom-mock"

    @pytest.mark.asyncio
    async def test_mock_provider_generate(self, mock_provider):
        """Test mock provider generate method."""
        response = await mock_provider.generate(
            system_prompt="System",
            user_prompt="User",
            temperature=0.5,
        )
        assert isinstance(response, LLMResponse)
        assert response.model == "mock-model"
        assert mock_provider.call_count == 1

    @pytest.mark.asyncio
    async def test_mock_provider_with_custom_responses(self):
        """Test mock provider with custom responses."""
        responses = ['{"response": 1}', '{"response": 2}']
        provider = MockLLMProvider(responses=responses)

        resp1 = await provider.generate("sys", "user")
        assert resp1.content == '{"response": 1}'

        resp2 = await provider.generate("sys", "user")
        assert resp2.content == '{"response": 2}'

    @pytest.mark.asyncio
    async def test_mock_provider_records_history(self, mock_provider):
        """Test that mock provider records call history."""
        await mock_provider.generate("System prompt", "User prompt", temperature=0.6)

        assert len(mock_provider.call_history) == 1
        call = mock_provider.call_history[0]
        assert call["system"] == "System prompt"
        assert call["user"] == "User prompt"
        assert call["temperature"] == 0.6

    @pytest.mark.asyncio
    async def test_mock_provider_reset(self, mock_provider):
        """Test mock provider reset."""
        await mock_provider.generate("sys", "user")
        assert mock_provider.call_count == 1

        mock_provider.reset()
        assert mock_provider.call_count == 0
        assert len(mock_provider.call_history) == 0

    @pytest.mark.asyncio
    async def test_mock_provider_set_response(self, mock_provider):
        """Test setting specific response."""
        mock_provider.set_response(1, '{"custom": "response"}')
        response = await mock_provider.generate("sys", "user")
        assert response.content == '{"custom": "response"}'

    def test_mock_provider_token_counting(self, mock_provider):
        """Test mock provider token counting."""
        # ~4 chars per token
        text = "This is a test string with about 40 characters"
        tokens = mock_provider.count_tokens(text)
        assert tokens == len(text) // 4

    @pytest.mark.asyncio
    async def test_mock_provider_default_gdd_response(self, mock_provider):
        """Test that default mock response is valid GDD."""
        response = await mock_provider.generate("sys", "user")
        gdd = parse_to_model(response.content, GameDesignDocument)
        assert gdd.meta.title == "Mock Game"
        assert len(gdd.systems) >= 3
        assert len(gdd.progression.milestones) >= 5

    @pytest.mark.asyncio
    async def test_mock_provider_generate_structured(self, mock_provider):
        """Test generate_structured method."""
        gdd, response = await mock_provider.generate_structured(
            system_prompt="System",
            user_prompt="User",
            model_class=GameDesignDocument,
        )
        assert isinstance(gdd, GameDesignDocument)
        assert isinstance(response, LLMResponse)


# =============================================================================
# FACTORY FUNCTION TESTS
# =============================================================================


class TestCreateProvider:
    """Tests for create_provider factory function."""

    def test_create_mock_provider(self):
        """Test creating mock provider."""
        provider = create_provider("mock")
        assert isinstance(provider, MockLLMProvider)

    def test_create_mock_provider_with_responses(self):
        """Test creating mock provider with custom responses."""
        provider = create_provider("mock", responses=['{"test": 1}'])
        assert isinstance(provider, MockLLMProvider)

    def test_create_unknown_provider(self):
        """Test that unknown provider raises error."""
        with pytest.raises(ValueError, match="Unknown provider"):
            create_provider("unknown")

    def test_create_anthropic_provider_without_key(self):
        """Test that Anthropic provider requires API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises((ValueError, ImportError)):
                create_provider("anthropic")

    def test_create_openai_provider_without_key(self):
        """Test that OpenAI provider requires API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises((ValueError, ImportError)):
                create_provider("openai")


# =============================================================================
# CONFIG TESTS
# =============================================================================


class TestConfig:
    """Tests for configuration loading."""

    def test_load_config(self):
        """Test loading configuration from file."""
        config = load_config()
        assert "orchestrator" in config
        assert "llm" in config

    def test_get_actor_temperature(self):
        """Test getting actor temperature."""
        temp = get_actor_temperature()
        assert temp == 0.6

    def test_get_critic_temperature(self):
        """Test getting critic temperature."""
        temp = get_critic_temperature()
        assert temp == 0.2

    def test_get_max_iterations(self):
        """Test getting max iterations."""
        iterations = get_max_iterations()
        assert iterations == 3


# =============================================================================
# RETRY TESTS
# =============================================================================


class TestRetryConfig:
    """Tests for retry configuration."""

    def test_default_retry_config(self):
        """Test default retry configuration."""
        config = RetryConfig()
        assert config.max_attempts == 3
        assert config.backoff_base == 2.0

    def test_custom_retry_config(self):
        """Test custom retry configuration."""
        config = RetryConfig(max_attempts=5, backoff_base=1.5, max_delay=60.0)
        assert config.max_attempts == 5
        assert config.backoff_base == 1.5
        assert config.max_delay == 60.0


class TestRetryWithBackoff:
    """Tests for retry_with_backoff function."""

    @pytest.mark.asyncio
    async def test_retry_succeeds_first_try(self):
        """Test that successful call doesn't retry."""
        call_count = 0

        async def success_func():
            nonlocal call_count
            call_count += 1
            return "success"

        config = RetryConfig(max_attempts=3)
        result = await retry_with_backoff(success_func, config)
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_succeeds_after_failures(self):
        """Test that retry succeeds after initial failures."""
        call_count = 0

        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return "success"

        config = RetryConfig(max_attempts=5, backoff_base=0.1)
        result = await retry_with_backoff(flaky_func, config)
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhausts_attempts(self):
        """Test that retry raises after exhausting attempts."""

        async def always_fail():
            raise ConnectionError("Always fails")

        config = RetryConfig(max_attempts=2, backoff_base=0.1)
        with pytest.raises(ConnectionError):
            await retry_with_backoff(always_fail, config)


# =============================================================================
# LLM RESPONSE TESTS
# =============================================================================


class TestLLMResponse:
    """Tests for LLMResponse dataclass."""

    def test_total_tokens(self):
        """Test total tokens calculation."""
        response = LLMResponse(
            content="test",
            input_tokens=100,
            output_tokens=50,
            model="test-model",
            latency_ms=100.0,
        )
        assert response.total_tokens == 150

    def test_response_fields(self):
        """Test response fields."""
        response = LLMResponse(
            content="test content",
            input_tokens=100,
            output_tokens=50,
            model="gpt-4",
            latency_ms=150.5,
            finish_reason="stop",
        )
        assert response.content == "test content"
        assert response.model == "gpt-4"
        assert response.finish_reason == "stop"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests for the LLM provider module."""

    @pytest.mark.asyncio
    async def test_full_flow_with_mock(self, sample_gdd_json):
        """Test full flow: create provider -> generate -> parse."""
        provider = create_provider("mock", default_response=sample_gdd_json)

        response = await provider.generate(
            system_prompt="You are a game designer.",
            user_prompt="Create a game design document.",
            temperature=0.6,
        )

        gdd = parse_to_model(response.content, GameDesignDocument)
        assert gdd.meta.title == "Test Game"
        assert len(gdd.systems) == 3

    @pytest.mark.asyncio
    async def test_structured_generation_flow(self, sample_gdd_json):
        """Test structured generation flow."""
        provider = create_provider("mock", default_response=sample_gdd_json)

        gdd, response = await provider.generate_structured(
            system_prompt="You are a game designer.",
            user_prompt="Create a game design document.",
            model_class=GameDesignDocument,
            temperature=0.6,
        )

        assert isinstance(gdd, GameDesignDocument)
        assert gdd.meta.title == "Test Game"
        assert response.model == "mock-model"

    @pytest.mark.asyncio
    async def test_actor_critic_temperatures(self):
        """Test that actor and critic temperatures are correctly configured."""
        actor_temp = get_actor_temperature()
        critic_temp = get_critic_temperature()

        # Actor should be higher for creativity
        assert actor_temp == 0.6
        # Critic should be lower for consistency
        assert critic_temp == 0.2
        # Actor temp should be higher than critic
        assert actor_temp > critic_temp

    @pytest.mark.asyncio
    async def test_mock_provider_multiple_calls(self):
        """Test mock provider handles multiple calls correctly."""
        provider = create_provider(
            "mock",
            responses=[
                '{"call": 1}',
                '{"call": 2}',
                '{"call": 3}',
            ],
        )

        resp1 = await provider.generate("sys", "user")
        resp2 = await provider.generate("sys", "user")
        resp3 = await provider.generate("sys", "user")

        assert json.loads(resp1.content)["call"] == 1
        assert json.loads(resp2.content)["call"] == 2
        assert json.loads(resp3.content)["call"] == 3
