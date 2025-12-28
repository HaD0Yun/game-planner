"""
test_orchestrator.py - Tests for Dual-Agent Game Planning Orchestrator

Tests cover:
- Basic execution flow with mock provider
- Critic approval on first iteration
- Critic rejection and revision loop
- Max iterations reached (best effort)
- JSON parsing error handling (fallback GDD)
- Timeout handling
- Network error handling (exponential backoff)
- Configuration loading
- Convenience functions
"""

import asyncio
import json
import pytest

# Import from parent directory
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator import (
    GamePlanningOrchestrator,
    OrchestratorConfig,
    create_fallback_gdd,
    create_template_gdd,
    create_mock_orchestrator,
    generate_gdd,
)
from llm_provider import (
    BaseLLMProvider,
    LLMResponse,
    MockLLMProvider,
)
from models import (
    Decision,
    TerminationReason,
    GameDesignDocument,
)


# =============================================================================
# FIXTURES
# =============================================================================


def create_valid_gdd_json() -> str:
    """Create a valid GDD JSON response for testing."""
    return json.dumps(
        {
            "schema_version": "1.0",
            "meta": {
                "title": "Test Game",
                "genres": ["action", "rpg"],
                "target_platforms": ["pc"],
                "target_audience": "Gamers who enjoy action RPGs with deep progression",
                "unique_selling_point": "Revolutionary combat system that adapts to player style in real-time",
                "estimated_dev_time_weeks": 52,
            },
            "core_loop": {
                "primary_actions": ["Fight", "Explore", "Upgrade"],
                "challenge_description": "Battle enemies with increasing difficulty while managing resources",
                "reward_description": "Gain experience, loot, and new abilities",
                "loop_description": "Explore -> Fight -> Loot -> Upgrade -> Repeat with harder areas",
                "session_length_minutes": 45,
            },
            "systems": [
                {
                    "name": "Combat System",
                    "type": "combat",
                    "description": "Real-time action combat with combo mechanics and enemy AI",
                    "mechanics": ["Light attack", "Heavy attack", "Dodge", "Block"],
                },
                {
                    "name": "Progression System",
                    "type": "leveling",
                    "description": "Experience-based leveling with skill trees",
                    "mechanics": ["Gain XP", "Level up", "Unlock skills"],
                },
                {
                    "name": "Inventory System",
                    "type": "inventory",
                    "description": "Grid-based inventory with equipment slots",
                    "mechanics": ["Store items", "Equip gear", "Craft items"],
                },
            ],
            "progression": {
                "type": "skill_tree",
                "milestones": [
                    {
                        "name": "First Blood",
                        "description": "Defeat first enemy",
                        "unlock_condition": "Kill your first enemy in combat",
                    },
                    {
                        "name": "Adventurer",
                        "description": "Complete tutorial",
                        "unlock_condition": "Complete the tutorial section",
                    },
                    {
                        "name": "Warrior",
                        "description": "Reach level 10",
                        "unlock_condition": "Reach character level 10",
                    },
                    {
                        "name": "Champion",
                        "description": "Defeat first boss",
                        "unlock_condition": "Defeat the first boss enemy",
                    },
                    {
                        "name": "Legend",
                        "description": "Complete main story",
                        "unlock_condition": "Finish the main story quest",
                    },
                ],
                "difficulty_curve_description": "Gradual increase with spike at bosses, then new area reset",
            },
            "narrative": {
                "setting": "Dark fantasy world with ancient ruins and mystical creatures",
                "story_premise": "A lone warrior seeks to uncover the truth behind a curse that plagues their homeland",
                "themes": ["Redemption", "Discovery", "Sacrifice"],
                "narrative_delivery": ["dialogue", "environmental"],
                "story_structure": "Three-act structure with multiple endings based on player choices",
            },
            "technical": {
                "recommended_engine": "unity",
                "art_style": "stylized",
                "key_technologies": ["Unity", "C#", "Shader Graph"],
                "audio": {
                    "music_style": "Orchestral with ambient elements",
                    "sound_categories": ["Combat", "Ambient", "UI"],
                },
            },
        }
    )


def create_approval_feedback_json() -> str:
    """Create a Critic approval feedback JSON."""
    return json.dumps(
        {
            "decision": "approve",
            "blocking_issues": [],
            "feasibility_score": 8,
            "coherence_score": 9,
            "fun_factor_score": 8,
            "completeness_score": 9,
            "originality_score": 8,
            "review_notes": "Excellent GDD with clear vision and feasible scope.",
        }
    )


def create_rejection_feedback_json() -> str:
    """Create a Critic rejection feedback JSON."""
    return json.dumps(
        {
            "decision": "revise",
            "blocking_issues": [
                {
                    "section": "meta",
                    "issue": "USP is too generic and doesn't differentiate from competitors",
                    "severity": "major",
                    "suggestion": "Define a specific unique mechanic or experience",
                },
            ],
            "feasibility_score": 7,
            "coherence_score": 6,
            "fun_factor_score": 5,
            "completeness_score": 7,
            "originality_score": 4,
            "review_notes": "Good foundation but needs more originality.",
        }
    )


# =============================================================================
# ORCHESTRATOR CONFIG TESTS
# =============================================================================


class TestOrchestratorConfig:
    """Tests for OrchestratorConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = OrchestratorConfig()

        assert config.max_iterations == 3
        assert config.actor_temperature == 0.6
        assert config.critic_temperature == 0.2
        assert config.max_tokens == 8192
        assert config.max_retries == 3
        assert config.retry_backoff_base == 2.0

    def test_custom_values(self):
        """Test custom configuration values."""
        config = OrchestratorConfig(
            max_iterations=5,
            actor_temperature=0.7,
            critic_temperature=0.1,
        )

        assert config.max_iterations == 5
        assert config.actor_temperature == 0.7
        assert config.critic_temperature == 0.1

    def test_from_config_dict(self):
        """Test loading from config dictionary."""
        config_dict = {
            "orchestrator": {
                "max_iterations": 2,
                "actor_temperature": 0.5,
                "critic_temperature": 0.3,
            },
            "llm": {
                "max_tokens": 4096,
            },
            "timeouts": {
                "actor_ms": 60000,
                "critic_ms": 30000,
            },
            "retries": {
                "max_attempts": 2,
                "backoff_base": 1.5,
            },
        }

        config = OrchestratorConfig.from_config(config_dict)

        assert config.max_iterations == 2
        assert config.actor_temperature == 0.5
        assert config.critic_temperature == 0.3
        assert config.max_tokens == 4096
        assert config.actor_timeout_ms == 60000
        assert config.critic_timeout_ms == 30000
        assert config.max_retries == 2
        assert config.retry_backoff_base == 1.5


# =============================================================================
# FALLBACK GDD TESTS
# =============================================================================


class TestFallbackGDD:
    """Tests for fallback GDD creation."""

    def test_create_fallback_gdd(self):
        """Test creating a fallback GDD."""
        user_prompt = "zombie survival roguelike with base building"

        gdd = create_fallback_gdd(user_prompt)

        assert isinstance(gdd, GameDesignDocument)
        assert "Zombie" in gdd.meta.title or "fallback" in gdd.meta.title.lower()
        assert "zombie survival roguelike" in gdd.meta.unique_selling_point.lower()
        assert len(gdd.systems) >= 3
        assert len(gdd.progression.milestones) >= 5
        assert "fallback" in (gdd.additional_notes or "").lower()

    def test_create_template_gdd(self):
        """Test creating a template GDD."""
        user_prompt = "space exploration game"

        gdd = create_template_gdd(user_prompt)

        assert isinstance(gdd, GameDesignDocument)
        assert len(gdd.systems) >= 3
        assert len(gdd.progression.milestones) >= 5

    def test_fallback_gdd_is_valid(self):
        """Test that fallback GDD passes validation."""
        user_prompt = "test game concept"

        gdd = create_fallback_gdd(user_prompt)

        # Should be valid JSON
        json_str = gdd.to_json()
        # Just verify it parses without error
        json.loads(json_str)

        # Should be parseable back to GDD
        restored = GameDesignDocument.from_json(json_str)
        assert restored.meta.title == gdd.meta.title


# =============================================================================
# BASIC ORCHESTRATOR TESTS
# =============================================================================


class TestGamePlanningOrchestrator:
    """Tests for GamePlanningOrchestrator."""

    @pytest.mark.asyncio
    async def test_successful_first_iteration(self):
        """Test successful GDD generation approved on first iteration."""
        # Setup mock responses: GDD then approval
        gdd_response = create_valid_gdd_json()
        approval_response = create_approval_feedback_json()

        provider = MockLLMProvider(responses=[gdd_response, approval_response])
        orchestrator = GamePlanningOrchestrator(provider)

        result = await orchestrator.execute("test game concept")

        assert result.success is True
        assert result.termination_reason == TerminationReason.APPROVED
        assert result.total_iterations == 1
        assert result.final_gdd.meta.title == "Test Game"
        assert len(result.iteration_history) == 1
        assert result.iteration_history[0].feedback.is_approved

    @pytest.mark.asyncio
    async def test_revision_then_approval(self):
        """Test GDD revision flow: reject -> revise -> approve."""
        # Setup: GDD -> rejection -> revised GDD -> approval
        gdd_response = create_valid_gdd_json()
        rejection_response = create_rejection_feedback_json()

        # Create a revised GDD with improved USP
        revised_gdd = json.loads(create_valid_gdd_json())
        revised_gdd["meta"]["title"] = "Revised Test Game"
        revised_gdd["meta"]["unique_selling_point"] = (
            "Time-manipulation combat where every attack can be rewound and replayed"
        )
        revised_gdd_json = json.dumps(revised_gdd)

        approval_response = create_approval_feedback_json()

        provider = MockLLMProvider(
            responses=[
                gdd_response,  # Initial GDD
                rejection_response,  # First review: reject
                revised_gdd_json,  # Revised GDD
                approval_response,  # Second review: approve
            ]
        )
        orchestrator = GamePlanningOrchestrator(provider)

        result = await orchestrator.execute("test game concept")

        assert result.success is True
        assert result.termination_reason == TerminationReason.APPROVED
        assert result.total_iterations == 2
        assert result.final_gdd.meta.title == "Revised Test Game"
        assert len(result.iteration_history) == 2
        assert not result.iteration_history[0].feedback.is_approved
        assert result.iteration_history[1].feedback.is_approved

    @pytest.mark.asyncio
    async def test_max_iterations_reached(self):
        """Test best-effort return when max iterations reached."""
        # Always reject
        gdd_response = create_valid_gdd_json()
        rejection_response = create_rejection_feedback_json()

        # 3 iterations: GDD, reject, GDD, reject, GDD, reject
        provider = MockLLMProvider(
            responses=[
                gdd_response,
                rejection_response,  # Iter 1
                gdd_response,
                rejection_response,  # Iter 2
                gdd_response,
                rejection_response,  # Iter 3
            ]
        )

        config = OrchestratorConfig(max_iterations=3)
        orchestrator = GamePlanningOrchestrator(provider, config)

        result = await orchestrator.execute("test game concept")

        assert result.success is False
        assert result.termination_reason == TerminationReason.MAX_ITERATIONS
        assert result.total_iterations == 3
        assert result.final_gdd is not None  # Should have best-effort GDD


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


class TestErrorHandling:
    """Tests for error handling scenarios."""

    @pytest.mark.asyncio
    async def test_actor_json_parse_error_uses_fallback(self):
        """Test that JSON parse error in Actor uses fallback GDD."""
        # Invalid JSON followed by valid approval
        invalid_json = "This is not valid JSON {"
        approval_response = create_approval_feedback_json()

        # Mock provider that returns invalid JSON for actor, then valid approval
        provider = MockLLMProvider(
            responses=[
                invalid_json,  # Invalid JSON
                invalid_json,  # Retry 1
                invalid_json,  # Retry 2 -> fallback
                approval_response,  # Critic approves fallback
            ]
        )

        config = OrchestratorConfig(max_retries=3)
        orchestrator = GamePlanningOrchestrator(provider, config)

        result = await orchestrator.execute("zombie roguelike")

        # Should succeed with fallback GDD
        assert result.success is True
        # Check for "FALLBACK" (case-insensitive) in notes or title
        notes = (result.final_gdd.additional_notes or "").lower()
        title = result.final_gdd.meta.title.lower()
        assert "fallback" in notes or "fallback" in title

    @pytest.mark.asyncio
    async def test_critic_failure_defaults_to_approval(self):
        """Test that Critic failure defaults to approval."""
        gdd_response = create_valid_gdd_json()
        invalid_feedback = "Not valid JSON"

        provider = MockLLMProvider(
            responses=[
                gdd_response,  # Valid GDD
                invalid_feedback,  # Invalid feedback
                invalid_feedback,  # Retry 1
                invalid_feedback,  # Retry 2 -> default approval
            ]
        )

        config = OrchestratorConfig(max_retries=3)
        orchestrator = GamePlanningOrchestrator(provider, config)

        result = await orchestrator.execute("test game")

        # Should succeed because Critic defaults to approval on failure
        assert result.success is True
        assert result.termination_reason == TerminationReason.APPROVED

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling with template fallback."""

        # Create a provider that times out
        class TimeoutProvider(BaseLLMProvider):
            async def _generate_impl(
                self,
                system_prompt,
                user_prompt,
                temperature=0.7,
                max_tokens=4096,
                **kwargs,
            ):
                await asyncio.sleep(10)  # Will timeout
                return LLMResponse(
                    content="{}",
                    input_tokens=0,
                    output_tokens=0,
                    model="timeout-test",
                    latency_ms=10000,
                )

            def count_tokens(self, text):
                return len(text) // 4

            def get_model_name(self):
                return "timeout-test"

        provider = TimeoutProvider()
        config = OrchestratorConfig(
            actor_timeout_ms=100,  # 100ms timeout
            max_retries=1,
        )
        orchestrator = GamePlanningOrchestrator(provider, config)

        result = await orchestrator.execute("test game")

        # The orchestrator uses fallback GDD on timeout, and Critic auto-approves
        # This is correct resilient behavior - we always return something usable
        assert result.final_gdd is not None
        # Should have fallback GDD (check title or notes)
        notes = (result.final_gdd.additional_notes or "").lower()
        title = result.final_gdd.meta.title.lower()
        assert "fallback" in notes or "fallback" in title

    @pytest.mark.asyncio
    async def test_exponential_backoff_on_network_error(self):
        """Test exponential backoff retry on network errors."""
        call_times = []

        class NetworkErrorProvider(BaseLLMProvider):
            def __init__(self):
                super().__init__()
                self.call_count = 0

            async def _generate_impl(
                self,
                system_prompt,
                user_prompt,
                temperature=0.7,
                max_tokens=4096,
                **kwargs,
            ):
                self.call_count += 1
                call_times.append(asyncio.get_event_loop().time())

                if self.call_count < 3:
                    raise ConnectionError("Network error")

                # Return valid response on 3rd try
                if "Designer" in system_prompt:
                    return LLMResponse(
                        content=create_valid_gdd_json(),
                        input_tokens=100,
                        output_tokens=500,
                        model="network-test",
                        latency_ms=100,
                    )
                else:
                    return LLMResponse(
                        content=create_approval_feedback_json(),
                        input_tokens=100,
                        output_tokens=100,
                        model="network-test",
                        latency_ms=50,
                    )

            def count_tokens(self, text):
                return len(text) // 4

            def get_model_name(self):
                return "network-test"

        provider = NetworkErrorProvider()
        config = OrchestratorConfig(
            max_retries=5,
            retry_backoff_base=1.1,  # Small backoff for faster tests
        )
        orchestrator = GamePlanningOrchestrator(provider, config)

        result = await orchestrator.execute("test game")

        assert result.success is True
        assert provider.call_count >= 3  # Should have retried


# =============================================================================
# CONVENIENCE FUNCTION TESTS
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_mock_orchestrator(self):
        """Test create_mock_orchestrator function."""
        orchestrator = create_mock_orchestrator()

        assert isinstance(orchestrator, GamePlanningOrchestrator)
        assert isinstance(orchestrator.llm_provider, MockLLMProvider)

    def test_create_mock_orchestrator_with_responses(self):
        """Test create_mock_orchestrator with custom responses."""
        responses = [create_valid_gdd_json(), create_approval_feedback_json()]
        orchestrator = create_mock_orchestrator(responses=responses)

        assert isinstance(orchestrator, GamePlanningOrchestrator)

    def test_create_mock_orchestrator_with_config(self):
        """Test create_mock_orchestrator with custom config."""
        config = OrchestratorConfig(max_iterations=5)
        orchestrator = create_mock_orchestrator(config=config)

        assert orchestrator.config.max_iterations == 5

    @pytest.mark.asyncio
    async def test_generate_gdd_convenience(self):
        """Test generate_gdd convenience function."""
        result = await generate_gdd("test game", provider_type="mock")

        assert result.final_gdd is not None
        assert isinstance(result.final_gdd, GameDesignDocument)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests for the full orchestration flow."""

    @pytest.mark.asyncio
    async def test_full_flow_with_mock(self):
        """Test complete flow from concept to approved GDD."""
        orchestrator = create_mock_orchestrator()

        result = await orchestrator.execute(
            "zombie survival roguelike with base building"
        )

        # Should complete successfully (mock returns valid data)
        assert result.final_gdd is not None
        assert result.total_iterations >= 1
        assert result.total_duration_ms > 0
        assert result.user_prompt == "zombie survival roguelike with base building"

    @pytest.mark.asyncio
    async def test_iteration_history_tracking(self):
        """Test that iteration history is properly tracked."""
        gdd_response = create_valid_gdd_json()
        rejection_response = create_rejection_feedback_json()
        approval_response = create_approval_feedback_json()

        provider = MockLLMProvider(
            responses=[
                gdd_response,
                rejection_response,
                gdd_response,
                approval_response,
            ]
        )
        orchestrator = GamePlanningOrchestrator(provider)

        result = await orchestrator.execute("test game")

        assert len(result.iteration_history) == 2

        # First iteration should have rejection
        iter1 = result.iteration_history[0]
        assert iter1.iteration_number == 0
        assert iter1.gdd is not None
        assert iter1.feedback is not None
        assert iter1.feedback.decision == Decision.REVISE

        # Second iteration should have approval
        iter2 = result.iteration_history[1]
        assert iter2.iteration_number == 1
        assert iter2.feedback.decision == Decision.APPROVE

    @pytest.mark.asyncio
    async def test_result_summary(self):
        """Test RefinementResult summary generation."""
        gdd_response = create_valid_gdd_json()
        approval_response = create_approval_feedback_json()

        provider = MockLLMProvider(responses=[gdd_response, approval_response])
        orchestrator = GamePlanningOrchestrator(provider)

        result = await orchestrator.execute("test game")

        summary = result.to_summary()

        assert "[OK] SUCCESS" in summary
        assert "Test Game" in summary
        assert "approved" in summary.lower()
        assert "1" in summary  # iterations


# =============================================================================
# PROVIDER CALL VERIFICATION TESTS
# =============================================================================


class TestProviderCalls:
    """Tests that verify correct provider calls."""

    @pytest.mark.asyncio
    async def test_actor_uses_correct_temperature(self):
        """Test that Actor uses configured temperature."""
        gdd_response = create_valid_gdd_json()
        approval_response = create_approval_feedback_json()

        provider = MockLLMProvider(responses=[gdd_response, approval_response])
        config = OrchestratorConfig(actor_temperature=0.8)
        orchestrator = GamePlanningOrchestrator(provider, config)

        await orchestrator.execute("test game")

        # Check actor call used correct temperature
        actor_call = provider.call_history[0]
        assert actor_call["temperature"] == 0.8

    @pytest.mark.asyncio
    async def test_critic_uses_correct_temperature(self):
        """Test that Critic uses configured temperature."""
        gdd_response = create_valid_gdd_json()
        approval_response = create_approval_feedback_json()

        provider = MockLLMProvider(responses=[gdd_response, approval_response])
        config = OrchestratorConfig(critic_temperature=0.15)
        orchestrator = GamePlanningOrchestrator(provider, config)

        await orchestrator.execute("test game")

        # Check critic call used correct temperature
        critic_call = provider.call_history[1]
        assert critic_call["temperature"] == 0.15

    @pytest.mark.asyncio
    async def test_actor_system_prompt_used(self):
        """Test that Actor uses Game Designer system prompt."""
        gdd_response = create_valid_gdd_json()
        approval_response = create_approval_feedback_json()

        provider = MockLLMProvider(responses=[gdd_response, approval_response])
        orchestrator = GamePlanningOrchestrator(provider)

        await orchestrator.execute("test game")

        actor_call = provider.call_history[0]
        assert (
            "Game Designer" in actor_call["system"]
            or "Expert Game Designer" in actor_call["system"]
        )

    @pytest.mark.asyncio
    async def test_critic_system_prompt_used(self):
        """Test that Critic uses Game Reviewer system prompt."""
        gdd_response = create_valid_gdd_json()
        approval_response = create_approval_feedback_json()

        provider = MockLLMProvider(responses=[gdd_response, approval_response])
        orchestrator = GamePlanningOrchestrator(provider)

        await orchestrator.execute("test game")

        critic_call = provider.call_history[1]
        assert (
            "Reviewer" in critic_call["system"]
            or "reviewer" in critic_call["system"].lower()
        )


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_empty_user_prompt(self):
        """Test handling of minimal user prompt."""
        provider = MockLLMProvider()
        orchestrator = GamePlanningOrchestrator(provider)

        result = await orchestrator.execute("game")

        assert result.final_gdd is not None
        assert result.user_prompt == "game"

    @pytest.mark.asyncio
    async def test_very_long_user_prompt(self):
        """Test handling of very long user prompt."""
        long_prompt = "A game about " + "adventure " * 500

        provider = MockLLMProvider()
        orchestrator = GamePlanningOrchestrator(provider)

        result = await orchestrator.execute(long_prompt)

        assert result.final_gdd is not None

    @pytest.mark.asyncio
    async def test_single_iteration_config(self):
        """Test with max_iterations=1."""
        gdd_response = create_valid_gdd_json()
        rejection_response = create_rejection_feedback_json()

        provider = MockLLMProvider(responses=[gdd_response, rejection_response])
        config = OrchestratorConfig(max_iterations=1)
        orchestrator = GamePlanningOrchestrator(provider, config)

        result = await orchestrator.execute("test game")

        assert result.total_iterations == 1
        assert result.termination_reason == TerminationReason.MAX_ITERATIONS

    @pytest.mark.asyncio
    async def test_unicode_in_prompt(self):
        """Test handling of Unicode in user prompt."""
        unicode_prompt = "Create a game with 한글 and 日本語 characters"

        provider = MockLLMProvider()
        orchestrator = GamePlanningOrchestrator(provider)

        result = await orchestrator.execute(unicode_prompt)

        assert result.final_gdd is not None
        assert result.user_prompt == unicode_prompt
