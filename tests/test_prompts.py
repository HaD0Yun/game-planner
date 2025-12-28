"""
test_prompts.py - Tests for Game Designer and Game Reviewer agent prompts

Tests cover:
- Prompt structure and content validation
- Required components in Actor prompt
- Required components in Critic prompt
- 5-Dimension Review Framework presence
- Severity definitions presence
- GDD schema reference in prompts
- Helper function tests
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from prompts import (
    # Main prompts
    GAME_DESIGNER_SYSTEM_PROMPT,
    GAME_REVIEWER_SYSTEM_PROMPT,
    # Schema references
    GDD_SCHEMA_REFERENCE,
    CRITIC_FEEDBACK_SCHEMA_REFERENCE,
    # User message templates
    ACTOR_USER_MESSAGE_TEMPLATE,
    ACTOR_REVISION_MESSAGE_TEMPLATE,
    CRITIC_USER_MESSAGE_TEMPLATE,
    # Helper functions
    create_actor_message,
    create_revision_message,
    create_critic_message,
    # Metadata
    PROMPT_METADATA,
)


# =============================================================================
# BASIC STRUCTURE TESTS
# =============================================================================


class TestPromptBasicStructure:
    """Test that prompts are properly defined and non-empty."""

    def test_game_designer_prompt_exists(self):
        """Test GAME_DESIGNER_SYSTEM_PROMPT is a non-empty string."""
        assert isinstance(GAME_DESIGNER_SYSTEM_PROMPT, str)
        assert len(GAME_DESIGNER_SYSTEM_PROMPT) > 1000  # Should be substantial

    def test_game_reviewer_prompt_exists(self):
        """Test GAME_REVIEWER_SYSTEM_PROMPT is a non-empty string."""
        assert isinstance(GAME_REVIEWER_SYSTEM_PROMPT, str)
        assert len(GAME_REVIEWER_SYSTEM_PROMPT) > 1000  # Should be substantial

    def test_gdd_schema_reference_exists(self):
        """Test GDD_SCHEMA_REFERENCE is properly defined."""
        assert isinstance(GDD_SCHEMA_REFERENCE, str)
        assert len(GDD_SCHEMA_REFERENCE) > 500

    def test_critic_feedback_schema_reference_exists(self):
        """Test CRITIC_FEEDBACK_SCHEMA_REFERENCE is properly defined."""
        assert isinstance(CRITIC_FEEDBACK_SCHEMA_REFERENCE, str)
        assert len(CRITIC_FEEDBACK_SCHEMA_REFERENCE) > 200


# =============================================================================
# ACTOR (GAME DESIGNER) PROMPT TESTS
# =============================================================================


class TestGameDesignerPrompt:
    """Test GAME_DESIGNER_SYSTEM_PROMPT content and structure."""

    def test_contains_role_definition(self):
        """Test Actor prompt defines the agent's role."""
        prompt = GAME_DESIGNER_SYSTEM_PROMPT
        assert "role" in prompt.lower()
        assert "game designer" in prompt.lower() or "game architect" in prompt.lower()

    def test_contains_output_requirements(self):
        """Test Actor prompt specifies JSON output requirement."""
        prompt = GAME_DESIGNER_SYSTEM_PROMPT
        assert "json" in prompt.lower()
        assert "output" in prompt.lower() or "respond" in prompt.lower()

    def test_contains_creative_philosophy(self):
        """Test Actor prompt encourages creativity."""
        prompt = GAME_DESIGNER_SYSTEM_PROMPT
        assert "creative" in prompt.lower() or "creativity" in prompt.lower()

    def test_references_gdd_sections(self):
        """Test Actor prompt references all GDD sections."""
        prompt = GAME_DESIGNER_SYSTEM_PROMPT
        required_sections = [
            "meta",
            "core_loop",
            "systems",
            "progression",
            "narrative",
            "technical",
        ]
        for section in required_sections:
            assert section in prompt.lower(), f"Missing section reference: {section}"

    def test_contains_gdd_schema(self):
        """Test Actor prompt includes GDD schema reference."""
        prompt = GAME_DESIGNER_SYSTEM_PROMPT
        # Should reference the schema structure
        assert "schema" in prompt.lower()
        assert "genres" in prompt.lower()
        assert "platforms" in prompt.lower()

    def test_mentions_minimum_requirements(self):
        """Test Actor prompt mentions minimum systems and milestones."""
        prompt = GAME_DESIGNER_SYSTEM_PROMPT
        # Minimum 3 systems requirement
        assert "3" in prompt or "three" in prompt.lower()
        # Minimum 5 milestones requirement
        assert "5" in prompt or "five" in prompt.lower()

    def test_contains_revision_handling(self):
        """Test Actor prompt includes revision handling instructions."""
        prompt = GAME_DESIGNER_SYSTEM_PROMPT
        assert "revision" in prompt.lower() or "feedback" in prompt.lower()

    def test_contains_example(self):
        """Test Actor prompt includes an example."""
        prompt = GAME_DESIGNER_SYSTEM_PROMPT
        assert "example" in prompt.lower()

    def test_mentions_unique_selling_point(self):
        """Test Actor prompt emphasizes USP."""
        prompt = GAME_DESIGNER_SYSTEM_PROMPT
        assert (
            "unique_selling_point" in prompt.lower()
            or "usp" in prompt.lower()
            or "unique" in prompt.lower()
        )


# =============================================================================
# CRITIC (GAME REVIEWER) PROMPT TESTS
# =============================================================================


class TestGameReviewerPrompt:
    """Test GAME_REVIEWER_SYSTEM_PROMPT content and structure."""

    def test_contains_role_definition(self):
        """Test Critic prompt defines the agent's role."""
        prompt = GAME_REVIEWER_SYSTEM_PROMPT
        assert "role" in prompt.lower()
        assert "reviewer" in prompt.lower() or "critic" in prompt.lower()

    def test_contains_5_dimension_framework(self):
        """Test Critic prompt includes all 5 review dimensions."""
        prompt = GAME_REVIEWER_SYSTEM_PROMPT
        dimensions = [
            "feasibility",
            "coherence",
            "fun factor",
            "completeness",
            "originality",
        ]
        for dimension in dimensions:
            assert dimension in prompt.lower(), f"Missing dimension: {dimension}"

    def test_contains_korean_dimension_terms(self):
        """Test Critic prompt includes Korean terminology for dimensions."""
        prompt = GAME_REVIEWER_SYSTEM_PROMPT
        korean_terms = [
            "실현 가능성",  # Feasibility
            "일관성",  # Coherence
            "재미 요소",  # Fun Factor
            "완성도",  # Completeness
            "독창성",  # Originality
        ]
        for term in korean_terms:
            assert term in prompt, f"Missing Korean term: {term}"

    def test_contains_severity_definitions(self):
        """Test Critic prompt includes severity definitions."""
        prompt = GAME_REVIEWER_SYSTEM_PROMPT
        # Check CRITICAL severity
        assert "critical" in prompt.lower()
        # Check MAJOR severity
        assert "major" in prompt.lower()

    def test_contains_korean_severity_definitions(self):
        """Test Critic prompt includes Korean severity explanations."""
        prompt = GAME_REVIEWER_SYSTEM_PROMPT
        # CRITICAL: 게임의 핵심 재미를 해침
        assert "게임의 핵심 재미를 해침" in prompt
        # MAJOR: 구현 또는 밸런스에 문제 발생 가능
        assert "구현 또는 밸런스에 문제 발생 가능" in prompt

    def test_contains_decision_logic(self):
        """Test Critic prompt includes decision logic."""
        prompt = GAME_REVIEWER_SYSTEM_PROMPT
        assert "approve" in prompt.lower()
        assert "revise" in prompt.lower()
        assert "decision" in prompt.lower()

    def test_contains_blocking_issues_guidance(self):
        """Test Critic prompt explains blocking issues."""
        prompt = GAME_REVIEWER_SYSTEM_PROMPT
        assert "blocking" in prompt.lower()
        assert "issue" in prompt.lower()

    def test_contains_conservative_certainty_policy(self):
        """Test Critic prompt emphasizes conservative certainty."""
        prompt = GAME_REVIEWER_SYSTEM_PROMPT
        assert "certain" in prompt.lower() or "conservative" in prompt.lower()

    def test_contains_actionable_feedback_requirement(self):
        """Test Critic prompt requires actionable feedback."""
        prompt = GAME_REVIEWER_SYSTEM_PROMPT
        assert "actionable" in prompt.lower() or "suggestion" in prompt.lower()

    def test_contains_score_guidance(self):
        """Test Critic prompt includes score guidance (1-10)."""
        prompt = GAME_REVIEWER_SYSTEM_PROMPT
        assert "1-10" in prompt or "score" in prompt.lower()

    def test_contains_weight_percentages(self):
        """Test Critic prompt includes dimension weights."""
        prompt = GAME_REVIEWER_SYSTEM_PROMPT
        # Weights should sum to 100%
        assert "25%" in prompt or "25 %" in prompt  # Feasibility and Fun Factor
        assert "20%" in prompt or "20 %" in prompt  # Coherence
        assert "15%" in prompt or "15 %" in prompt  # Completeness and Originality

    def test_references_critic_feedback_schema(self):
        """Test Critic prompt references CriticFeedback schema."""
        prompt = GAME_REVIEWER_SYSTEM_PROMPT
        assert "criticfeedback" in prompt.lower() or "feedback schema" in prompt.lower()

    def test_contains_example_review(self):
        """Test Critic prompt includes an example review."""
        prompt = GAME_REVIEWER_SYSTEM_PROMPT
        assert "example" in prompt.lower()


# =============================================================================
# GDD SCHEMA REFERENCE TESTS
# =============================================================================


class TestGDDSchemaReference:
    """Test GDD_SCHEMA_REFERENCE content."""

    def test_contains_all_required_sections(self):
        """Test schema reference includes all GDD sections."""
        schema = GDD_SCHEMA_REFERENCE
        sections = [
            "meta",
            "core_loop",
            "systems",
            "progression",
            "narrative",
            "technical",
            "map_hints",
            "risks",
        ]
        for section in sections:
            assert section in schema.lower(), f"Missing section: {section}"

    def test_contains_genre_enum_values(self):
        """Test schema reference includes genre options."""
        schema = GDD_SCHEMA_REFERENCE
        genres = ["action", "rpg", "puzzle", "roguelike", "survival"]
        for genre in genres:
            assert genre in schema.lower(), f"Missing genre: {genre}"

    def test_contains_platform_enum_values(self):
        """Test schema reference includes platform options."""
        schema = GDD_SCHEMA_REFERENCE
        platforms = ["pc", "web", "mobile_ios"]
        for platform in platforms:
            assert platform in schema.lower(), f"Missing platform: {platform}"

    def test_contains_field_constraints(self):
        """Test schema reference includes field constraints."""
        schema = GDD_SCHEMA_REFERENCE
        # Should mention minimum requirements
        assert "minimum" in schema.lower() or "min" in schema.lower() or "3" in schema
        # Should mention character limits
        assert "chars" in schema.lower() or "char" in schema.lower()


# =============================================================================
# CRITIC FEEDBACK SCHEMA REFERENCE TESTS
# =============================================================================


class TestCriticFeedbackSchemaReference:
    """Test CRITIC_FEEDBACK_SCHEMA_REFERENCE content."""

    def test_contains_decision_field(self):
        """Test schema reference includes decision field."""
        schema = CRITIC_FEEDBACK_SCHEMA_REFERENCE
        assert "decision" in schema.lower()
        assert "approve" in schema.lower()
        assert "revise" in schema.lower()

    def test_contains_blocking_issues_field(self):
        """Test schema reference includes blocking_issues field."""
        schema = CRITIC_FEEDBACK_SCHEMA_REFERENCE
        assert "blocking_issues" in schema.lower()

    def test_contains_all_score_fields(self):
        """Test schema reference includes all 5 score fields."""
        schema = CRITIC_FEEDBACK_SCHEMA_REFERENCE
        score_fields = [
            "feasibility_score",
            "coherence_score",
            "fun_factor_score",
            "completeness_score",
            "originality_score",
        ]
        for field in score_fields:
            assert field in schema.lower(), f"Missing score field: {field}"

    def test_contains_severity_field(self):
        """Test schema reference includes severity in blocking issues."""
        schema = CRITIC_FEEDBACK_SCHEMA_REFERENCE
        assert "severity" in schema.lower()
        assert "critical" in schema.lower()
        assert "major" in schema.lower()


# =============================================================================
# USER MESSAGE TEMPLATE TESTS
# =============================================================================


class TestUserMessageTemplates:
    """Test user message templates."""

    def test_actor_template_has_placeholder(self):
        """Test Actor template has user_prompt placeholder."""
        assert "{user_prompt}" in ACTOR_USER_MESSAGE_TEMPLATE

    def test_actor_revision_template_has_placeholders(self):
        """Test Actor revision template has required placeholders."""
        assert "{previous_gdd}" in ACTOR_REVISION_MESSAGE_TEMPLATE
        assert "{critic_feedback}" in ACTOR_REVISION_MESSAGE_TEMPLATE

    def test_critic_template_has_placeholders(self):
        """Test Critic template has required placeholders."""
        assert "{user_prompt}" in CRITIC_USER_MESSAGE_TEMPLATE
        assert "{gdd_json}" in CRITIC_USER_MESSAGE_TEMPLATE


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================


class TestHelperFunctions:
    """Test helper functions for message creation."""

    def test_create_actor_message(self):
        """Test create_actor_message function."""
        result = create_actor_message("zombie survival roguelike")
        assert "zombie survival roguelike" in result
        assert "GDD" in result or "Game Design Document" in result

    def test_create_revision_message(self):
        """Test create_revision_message function."""
        result = create_revision_message(
            previous_gdd='{"meta": {"title": "Test"}}',
            critic_feedback="## CRITIC DECISION: REVISE",
        )
        assert "Test" in result
        assert "REVISE" in result
        assert "fix" in result.lower() or "address" in result.lower()

    def test_create_critic_message(self):
        """Test create_critic_message function."""
        result = create_critic_message(
            user_prompt="space exploration game",
            gdd_json='{"meta": {"title": "Space Explorer"}}',
        )
        assert "space exploration game" in result
        assert "Space Explorer" in result
        assert "5-dimension" in result.lower() or "evaluate" in result.lower()


# =============================================================================
# PROMPT METADATA TESTS
# =============================================================================


class TestPromptMetadata:
    """Test PROMPT_METADATA structure."""

    def test_metadata_has_actor_entry(self):
        """Test metadata includes actor configuration."""
        assert "actor" in PROMPT_METADATA
        actor = PROMPT_METADATA["actor"]
        assert "name" in actor
        assert "temperature" in actor[
            "recommended_temperature"
        ].__class__.__name__.lower() or isinstance(
            actor["recommended_temperature"], (int, float)
        )
        assert actor["recommended_temperature"] == 0.6

    def test_metadata_has_critic_entry(self):
        """Test metadata includes critic configuration."""
        assert "critic" in PROMPT_METADATA
        critic = PROMPT_METADATA["critic"]
        assert "name" in critic
        assert isinstance(critic["recommended_temperature"], (int, float))
        assert critic["recommended_temperature"] == 0.2

    def test_critic_metadata_has_review_dimensions(self):
        """Test critic metadata includes review dimensions."""
        critic = PROMPT_METADATA["critic"]
        assert "review_dimensions" in critic
        assert len(critic["review_dimensions"]) == 5

    def test_critic_metadata_has_severity_levels(self):
        """Test critic metadata includes severity levels."""
        critic = PROMPT_METADATA["critic"]
        assert "severity_levels" in critic
        assert "critical" in critic["severity_levels"]
        assert "major" in critic["severity_levels"]

    def test_actor_has_correct_output_schema(self):
        """Test actor metadata references GameDesignDocument schema."""
        actor = PROMPT_METADATA["actor"]
        assert actor["output_schema"] == "GameDesignDocument"

    def test_critic_has_correct_output_schema(self):
        """Test critic metadata references CriticFeedback schema."""
        critic = PROMPT_METADATA["critic"]
        assert critic["output_schema"] == "CriticFeedback"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestPromptIntegration:
    """Test prompt integration and consistency."""

    def test_actor_prompt_includes_gdd_schema(self):
        """Test that GAME_DESIGNER_SYSTEM_PROMPT includes GDD schema reference."""
        # The schema should be embedded in the actor prompt
        assert GDD_SCHEMA_REFERENCE in GAME_DESIGNER_SYSTEM_PROMPT

    def test_critic_prompt_includes_feedback_schema(self):
        """Test that GAME_REVIEWER_SYSTEM_PROMPT includes feedback schema reference."""
        # The schema should be embedded in the critic prompt
        assert CRITIC_FEEDBACK_SCHEMA_REFERENCE in GAME_REVIEWER_SYSTEM_PROMPT

    def test_prompts_are_not_identical(self):
        """Test that Actor and Critic prompts are different."""
        assert GAME_DESIGNER_SYSTEM_PROMPT != GAME_REVIEWER_SYSTEM_PROMPT

    def test_both_prompts_request_json_only(self):
        """Test both prompts request JSON-only responses."""
        assert "only with valid json" in GAME_DESIGNER_SYSTEM_PROMPT.lower()
        assert "only with valid json" in GAME_REVIEWER_SYSTEM_PROMPT.lower()

    def test_prompts_have_substantial_length(self):
        """Test prompts are comprehensive (not too short)."""
        # Actor prompt should be substantial for game design guidance
        assert len(GAME_DESIGNER_SYSTEM_PROMPT) > 5000
        # Critic prompt should be substantial for review framework
        assert len(GAME_REVIEWER_SYSTEM_PROMPT) > 5000

    def test_dimension_weights_in_critic_sum_to_100(self):
        """Test that review dimension weights mentioned sum to 100%."""
        # Weights: Feasibility 25%, Coherence 20%, Fun Factor 25%, Completeness 15%, Originality 15%
        # = 100%
        prompt = GAME_REVIEWER_SYSTEM_PROMPT
        # Check that all expected weights are mentioned
        assert "25%" in prompt  # Feasibility and Fun Factor
        assert "20%" in prompt  # Coherence
        assert "15%" in prompt  # Completeness and Originality
