"""
test_models.py - Comprehensive tests for GDD schema Pydantic models

Tests cover:
- Model validation
- Serialization/deserialization
- Edge cases (missing fields, invalid values)
- Helper methods
- Enum validation
"""

import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (
    # Enums
    Genre,
    Platform,
    AudienceRating,
    GameEngine,
    ArtStyle,
    ProgressionType,
    NarrativeDelivery,
    SystemType,
    BiomeType,
    Severity,
    Decision,
    TerminationReason,
    # Models
    GameMeta,
    FeedbackMechanism,
    CoreLoop,
    SystemParameter,
    GameSystem,
    Milestone,
    Progression,
    Character,
    Narrative,
    PerformanceTarget,
    AudioRequirements,
    TechnicalSpec,
    ObstacleHint,
    SpecialFeature,
    MapGenerationHints,
    Risk,
    GameDesignDocument,
    BlockingIssue,
    CriticFeedback,
    RefinementResult,
)


# =============================================================================
# FIXTURES - Reusable test data
# =============================================================================


@pytest.fixture
def valid_game_meta():
    """Create a valid GameMeta instance."""
    return GameMeta(
        title="Zombie Survival Roguelike",
        genres=[Genre.ROGUELIKE, Genre.SURVIVAL, Genre.ACTION],
        target_platforms=[Platform.PC, Platform.WEB],
        target_audience="Fans of challenging survival games aged 18-35",
        audience_rating=AudienceRating.MATURE,
        unique_selling_point="Procedural base building with permadeath consequences and emergent storytelling",
        estimated_dev_time_weeks=52,
        team_size_estimate=5,
    )


@pytest.fixture
def valid_core_loop():
    """Create a valid CoreLoop instance."""
    return CoreLoop(
        primary_actions=["Explore", "Fight", "Loot", "Upgrade"],
        challenge_description="Survive increasingly difficult zombie waves while managing resources and base defense",
        reward_description="Gain resources to upgrade base and unlock new weapons, abilities, and survivors",
        loop_description="Explore -> Encounter Zombies -> Fight/Flee -> Loot -> Return to Base -> Upgrade -> Repeat",
        session_length_minutes=30,
        feedback_mechanisms=[
            FeedbackMechanism(
                trigger="Enemy defeated",
                response="XP gain animation and sound",
                purpose="Provides immediate satisfaction for combat success",
            )
        ],
        hook_elements=["Daily challenges", "Leaderboards", "Unlockable content"],
    )


@pytest.fixture
def valid_game_systems():
    """Create a list of valid GameSystem instances (minimum 3)."""
    return [
        GameSystem(
            name="Combat System",
            type=SystemType.COMBAT,
            description="Real-time melee and ranged combat with dodge mechanics and stamina management",
            mechanics=[
                "Light attack",
                "Heavy attack",
                "Block",
                "Dodge roll",
                "Ranged aim",
            ],
            parameters=[
                SystemParameter(
                    name="damage_multiplier",
                    type="float",
                    default_value="1.0",
                    description="Base damage multiplier for all attacks",
                    range="0.1-10.0",
                )
            ],
            dependencies=[],
            priority=1,
        ),
        GameSystem(
            name="Inventory System",
            type=SystemType.INVENTORY,
            description="Grid-based inventory with weight limits and item stacking",
            mechanics=["Pick up", "Drop", "Use", "Combine", "Sort"],
            dependencies=[],
            priority=2,
        ),
        GameSystem(
            name="Building System",
            type=SystemType.BUILDING,
            description="Base construction and fortification with resource costs",
            mechanics=["Place", "Rotate", "Upgrade", "Repair", "Demolish"],
            dependencies=["Inventory System"],
            priority=3,
        ),
    ]


@pytest.fixture
def valid_progression():
    """Create a valid Progression instance."""
    return Progression(
        type=ProgressionType.ROGUELIKE_RUNS,
        milestones=[
            Milestone(
                name="First Night Survived",
                description="Complete your first night defense",
                unlock_condition="Survive until dawn on day 1",
                rewards=["Tutorial completion badge"],
                estimated_hours=0.5,
            ),
            Milestone(
                name="First Boss Defeated",
                description="Defeat the first major zombie boss",
                unlock_condition="Kill the Bloater Boss",
                rewards=["New weapon unlock", "Base expansion slot"],
            ),
            Milestone(
                name="Base Level 5",
                description="Upgrade your base to level 5",
                unlock_condition="Complete all level 5 base upgrades",
                rewards=["Advanced crafting recipes"],
            ),
            Milestone(
                name="100 Zombies Killed",
                description="Eliminate 100 zombies total",
                unlock_condition="Cumulative zombie kills reach 100",
                rewards=["Combat efficiency bonus"],
            ),
            Milestone(
                name="Week One Survivor",
                description="Survive for 7 in-game days",
                unlock_condition="Reach day 7 without dying",
                rewards=["Veteran survivor title", "New game mode unlock"],
            ),
        ],
        difficulty_curve_description="Exponential zombie count increase with linear resource availability, creating a challenging but fair curve",
        meta_progression_description="Permanent upgrades and unlocks persist between runs",
    )


@pytest.fixture
def valid_narrative():
    """Create a valid Narrative instance."""
    return Narrative(
        setting="Post-apocalyptic urban wasteland, 2045, after the Z-virus outbreak",
        story_premise="Survivors must rebuild society while fighting zombie hordes and uncovering the truth behind the outbreak",
        themes=["Survival", "Hope", "Sacrifice", "Community"],
        characters=[
            Character(
                name="Alex",
                role="Protagonist",
                description="A former first responder who must lead survivors to safety",
                motivation="Find their missing family",
                abilities=["Medical training", "Leadership"],
            )
        ],
        narrative_delivery=[
            NarrativeDelivery.ENVIRONMENTAL,
            NarrativeDelivery.DIALOGUE,
        ],
        story_structure="Three-act structure with branching paths based on player choices",
        key_story_beats=[
            "Initial outbreak",
            "Finding the safe house",
            "First major loss",
            "Discovery of cure lead",
        ],
    )


@pytest.fixture
def valid_technical_spec():
    """Create a valid TechnicalSpec instance."""
    return TechnicalSpec(
        recommended_engine=GameEngine.UNITY,
        art_style=ArtStyle.PIXEL_ART,
        key_technologies=[
            "Procedural generation",
            "Pathfinding AI",
            "Save system",
            "State machine",
        ],
        performance_targets=[
            PerformanceTarget(
                platform=Platform.PC,
                target_fps=60,
                min_resolution="1920x1080",
                max_ram_mb=4096,
            )
        ],
        audio=AudioRequirements(
            music_style="Atmospheric electronic with tense orchestral elements",
            sound_categories=["Ambient", "Combat", "UI", "Environmental"],
            voice_acting=False,
            adaptive_music=True,
        ),
        asset_requirements=[
            "Sprite sheets",
            "Tile sets",
            "UI elements",
            "Sound effects",
        ],
        networking_required=False,
    )


@pytest.fixture
def valid_map_hints():
    """Create valid MapGenerationHints instance."""
    return MapGenerationHints(
        biomes=[BiomeType.URBAN, BiomeType.RUINS],
        map_size="large",
        obstacles=[
            ObstacleHint(
                type="wall",
                density="medium",
                purpose="Create chokepoints for defensive gameplay",
            )
        ],
        special_features=[
            SpecialFeature(
                name="Safe Room",
                frequency="rare",
                requirements=["Near spawn point"],
                description="A fortified room where players can rest and save",
            )
        ],
        connectivity="high",
        generation_style="procedural_rooms",
    )


@pytest.fixture
def valid_gdd(
    valid_game_meta,
    valid_core_loop,
    valid_game_systems,
    valid_progression,
    valid_narrative,
    valid_technical_spec,
    valid_map_hints,
):
    """Create a complete valid GameDesignDocument."""
    return GameDesignDocument(
        meta=valid_game_meta,
        core_loop=valid_core_loop,
        systems=valid_game_systems,
        progression=valid_progression,
        narrative=valid_narrative,
        technical=valid_technical_spec,
        map_hints=valid_map_hints,
        risks=[
            Risk(
                category="Scope",
                description="The building system may be too complex for initial release timeline",
                severity=Severity.MAJOR,
                mitigation="Implement MVP version first, iterate based on feedback",
            )
        ],
    )


# =============================================================================
# ENUM TESTS
# =============================================================================


class TestEnums:
    """Test enum definitions and values."""

    def test_genre_values(self):
        """Test Genre enum has expected values."""
        assert Genre.ROGUELIKE.value == "roguelike"
        assert Genre.ACTION.value == "action"
        assert Genre.RPG.value == "rpg"

    def test_platform_values(self):
        """Test Platform enum has expected values."""
        assert Platform.PC.value == "pc"
        assert Platform.WEB.value == "web"
        assert Platform.MOBILE_IOS.value == "mobile_ios"

    def test_severity_values(self):
        """Test Severity enum for critic feedback."""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.MAJOR.value == "major"

    def test_decision_values(self):
        """Test Decision enum for critic decisions."""
        assert Decision.APPROVE.value == "approve"
        assert Decision.REVISE.value == "revise"

    def test_all_enums_are_str_enum(self):
        """Verify all enums inherit from str for JSON serialization."""
        enums = [
            Genre,
            Platform,
            AudienceRating,
            GameEngine,
            ArtStyle,
            ProgressionType,
            NarrativeDelivery,
            SystemType,
            BiomeType,
            Severity,
            Decision,
            TerminationReason,
        ]
        for enum_class in enums:
            assert issubclass(enum_class, str), (
                f"{enum_class.__name__} should inherit from str"
            )


# =============================================================================
# GAME META TESTS
# =============================================================================


class TestGameMeta:
    """Test GameMeta model."""

    def test_valid_game_meta(self, valid_game_meta):
        """Test creating a valid GameMeta instance."""
        assert valid_game_meta.title == "Zombie Survival Roguelike"
        assert Genre.ROGUELIKE in valid_game_meta.genres
        assert valid_game_meta.estimated_dev_time_weeks == 52

    def test_game_meta_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            GameMeta(
                title="Test Game",
                # Missing: genres, target_platforms, target_audience, unique_selling_point, estimated_dev_time_weeks
            )
        errors = exc_info.value.errors()
        assert len(errors) >= 4  # At least 4 missing required fields

    def test_game_meta_title_too_short(self):
        """Test title validation - too short."""
        with pytest.raises(ValidationError) as exc_info:
            GameMeta(
                title="",  # Empty title
                genres=[Genre.ACTION],
                target_platforms=[Platform.PC],
                target_audience="General gaming audience interested in action",
                unique_selling_point="A unique twist on the action genre with innovative mechanics",
                estimated_dev_time_weeks=10,
            )
        assert any("title" in str(e["loc"]) for e in exc_info.value.errors())

    def test_game_meta_usp_too_short(self):
        """Test USP validation - must be at least 20 characters."""
        with pytest.raises(ValidationError) as exc_info:
            GameMeta(
                title="Test Game",
                genres=[Genre.ACTION],
                target_platforms=[Platform.PC],
                target_audience="General gaming audience interested in action",
                unique_selling_point="Too short",  # Less than 20 chars
                estimated_dev_time_weeks=10,
            )
        assert any(
            "unique_selling_point" in str(e["loc"]) for e in exc_info.value.errors()
        )

    def test_game_meta_dev_time_bounds(self):
        """Test estimated_dev_time_weeks bounds (1-520)."""
        with pytest.raises(ValidationError):
            GameMeta(
                title="Test Game",
                genres=[Genre.ACTION],
                target_platforms=[Platform.PC],
                target_audience="General gaming audience interested in action",
                unique_selling_point="A unique twist on the action genre with innovative mechanics",
                estimated_dev_time_weeks=0,  # Below minimum
            )

        with pytest.raises(ValidationError):
            GameMeta(
                title="Test Game",
                genres=[Genre.ACTION],
                target_platforms=[Platform.PC],
                target_audience="General gaming audience interested in action",
                unique_selling_point="A unique twist on the action genre with innovative mechanics",
                estimated_dev_time_weeks=600,  # Above maximum
            )

    def test_game_meta_serialization(self, valid_game_meta):
        """Test GameMeta JSON serialization."""
        json_str = valid_game_meta.model_dump_json()
        data = json.loads(json_str)
        assert data["title"] == "Zombie Survival Roguelike"
        assert "roguelike" in data["genres"]

    def test_game_meta_deserialization(self, valid_game_meta):
        """Test GameMeta JSON deserialization."""
        json_str = valid_game_meta.model_dump_json()
        restored = GameMeta.model_validate_json(json_str)
        assert restored.title == valid_game_meta.title
        assert restored.genres == valid_game_meta.genres


# =============================================================================
# CORE LOOP TESTS
# =============================================================================


class TestCoreLoop:
    """Test CoreLoop model."""

    def test_valid_core_loop(self, valid_core_loop):
        """Test creating a valid CoreLoop instance."""
        assert len(valid_core_loop.primary_actions) == 4
        assert valid_core_loop.session_length_minutes == 30

    def test_core_loop_minimum_actions(self):
        """Test that at least 2 primary actions are required."""
        with pytest.raises(ValidationError):
            CoreLoop(
                primary_actions=["OnlyOne"],  # Need at least 2
                challenge_description="Some challenge description that is long enough",
                reward_description="Some reward description that is long enough",
                loop_description="Some loop description that is long enough",
                session_length_minutes=30,
            )

    def test_core_loop_session_length_bounds(self):
        """Test session_length_minutes bounds (1-480)."""
        # Valid minimum
        loop = CoreLoop(
            primary_actions=["Action1", "Action2"],
            challenge_description="Some challenge description that is long enough",
            reward_description="Some reward description that is long enough",
            loop_description="Some loop description that is long enough",
            session_length_minutes=1,
        )
        assert loop.session_length_minutes == 1

        # Invalid - too long
        with pytest.raises(ValidationError):
            CoreLoop(
                primary_actions=["Action1", "Action2"],
                challenge_description="Some challenge description that is long enough",
                reward_description="Some reward description that is long enough",
                loop_description="Some loop description that is long enough",
                session_length_minutes=500,  # Above maximum
            )


# =============================================================================
# GAME SYSTEM TESTS
# =============================================================================


class TestGameSystem:
    """Test GameSystem model."""

    def test_valid_game_system(self, valid_game_systems):
        """Test creating valid GameSystem instances."""
        combat = valid_game_systems[0]
        assert combat.name == "Combat System"
        assert combat.type == SystemType.COMBAT
        assert len(combat.mechanics) >= 1

    def test_game_system_with_parameters(self, valid_game_systems):
        """Test GameSystem with parameters."""
        combat = valid_game_systems[0]
        assert len(combat.parameters) == 1
        assert combat.parameters[0].name == "damage_multiplier"

    def test_game_system_priority_bounds(self):
        """Test priority bounds (1-10)."""
        with pytest.raises(ValidationError):
            GameSystem(
                name="Test System",
                type=SystemType.CUSTOM,
                description="A test system for validation testing purposes",
                mechanics=["Test mechanic"],
                priority=0,  # Below minimum
            )

        with pytest.raises(ValidationError):
            GameSystem(
                name="Test System",
                type=SystemType.CUSTOM,
                description="A test system for validation testing purposes",
                mechanics=["Test mechanic"],
                priority=11,  # Above maximum
            )


# =============================================================================
# PROGRESSION TESTS
# =============================================================================


class TestProgression:
    """Test Progression model."""

    def test_valid_progression(self, valid_progression):
        """Test creating a valid Progression instance."""
        assert valid_progression.type == ProgressionType.ROGUELIKE_RUNS
        assert len(valid_progression.milestones) >= 5

    def test_progression_minimum_milestones(self):
        """Test that at least 5 milestones are required."""
        with pytest.raises(ValidationError) as exc_info:
            Progression(
                type=ProgressionType.LINEAR,
                milestones=[
                    Milestone(
                        name=f"Milestone {i}",
                        description=f"Description for milestone {i}",
                        unlock_condition=f"Condition for milestone {i}",
                    )
                    for i in range(4)  # Only 4, need 5
                ],
                difficulty_curve_description="Linear difficulty increase throughout the game",
            )
        # Pydantic uses "at least 5 items" for min_length validation
        assert "at least 5" in str(exc_info.value) or "milestones" in str(
            exc_info.value
        )


# =============================================================================
# NARRATIVE TESTS
# =============================================================================


class TestNarrative:
    """Test Narrative model."""

    def test_valid_narrative(self, valid_narrative):
        """Test creating a valid Narrative instance."""
        assert "2045" in valid_narrative.setting
        assert len(valid_narrative.themes) >= 1
        assert len(valid_narrative.narrative_delivery) >= 1

    def test_narrative_with_characters(self, valid_narrative):
        """Test Narrative with character definitions."""
        assert len(valid_narrative.characters) >= 1
        assert valid_narrative.characters[0].name == "Alex"


# =============================================================================
# TECHNICAL SPEC TESTS
# =============================================================================


class TestTechnicalSpec:
    """Test TechnicalSpec model."""

    def test_valid_technical_spec(self, valid_technical_spec):
        """Test creating a valid TechnicalSpec instance."""
        assert valid_technical_spec.recommended_engine == GameEngine.UNITY
        assert valid_technical_spec.art_style == ArtStyle.PIXEL_ART

    def test_technical_spec_audio_requirements(self, valid_technical_spec):
        """Test AudioRequirements nested model."""
        assert valid_technical_spec.audio.adaptive_music is True
        assert len(valid_technical_spec.audio.sound_categories) >= 1


# =============================================================================
# MAP GENERATION HINTS TESTS
# =============================================================================


class TestMapGenerationHints:
    """Test MapGenerationHints model."""

    def test_valid_map_hints(self, valid_map_hints):
        """Test creating valid MapGenerationHints."""
        assert BiomeType.URBAN in valid_map_hints.biomes
        assert valid_map_hints.map_size == "large"

    def test_map_hints_to_command_args(self, valid_map_hints):
        """Test conversion to /Map command arguments."""
        args = valid_map_hints.to_map_command_args()
        assert "biomes:" in args
        assert "urban" in args
        assert "size: large" in args


# =============================================================================
# GAME DESIGN DOCUMENT TESTS
# =============================================================================


class TestGameDesignDocument:
    """Test the root GameDesignDocument model."""

    def test_valid_gdd(self, valid_gdd):
        """Test creating a complete valid GDD."""
        assert valid_gdd.schema_version == "1.0"
        assert valid_gdd.meta.title == "Zombie Survival Roguelike"
        assert len(valid_gdd.systems) >= 3

    def test_gdd_minimum_systems(
        self,
        valid_game_meta,
        valid_core_loop,
        valid_progression,
        valid_narrative,
        valid_technical_spec,
    ):
        """Test that at least 3 systems are required."""
        with pytest.raises(ValidationError) as exc_info:
            GameDesignDocument(
                meta=valid_game_meta,
                core_loop=valid_core_loop,
                systems=[
                    GameSystem(
                        name="Only One System",
                        type=SystemType.COMBAT,
                        description="A single combat system for the game",
                        mechanics=["Attack", "Defend"],
                    )
                ],  # Only 1, need 3
                progression=valid_progression,
                narrative=valid_narrative,
                technical=valid_technical_spec,
            )
        # Pydantic uses "at least 3 items" for min_length validation
        assert "at least 3" in str(exc_info.value) or "systems" in str(exc_info.value)

    def test_gdd_json_serialization(self, valid_gdd):
        """Test GDD JSON serialization."""
        json_str = valid_gdd.to_json()
        data = json.loads(json_str)
        assert data["schema_version"] == "1.0"
        assert data["meta"]["title"] == "Zombie Survival Roguelike"

    def test_gdd_json_deserialization(self, valid_gdd):
        """Test GDD JSON deserialization."""
        json_str = valid_gdd.to_json()
        restored = GameDesignDocument.from_json(json_str)
        assert restored.meta.title == valid_gdd.meta.title
        assert len(restored.systems) == len(valid_gdd.systems)

    def test_gdd_from_llm_response_raw_json(self, valid_gdd):
        """Test parsing raw JSON from LLM."""
        json_str = valid_gdd.to_json()
        restored = GameDesignDocument.from_llm_response(json_str)
        assert restored.meta.title == valid_gdd.meta.title

    def test_gdd_from_llm_response_wrapped_json(self, valid_gdd):
        """Test parsing JSON wrapped in markdown code block."""
        json_str = valid_gdd.to_json()
        wrapped = f"```json\n{json_str}\n```"
        restored = GameDesignDocument.from_llm_response(wrapped)
        assert restored.meta.title == valid_gdd.meta.title

    def test_gdd_from_llm_response_invalid_json(self):
        """Test error handling for invalid JSON."""
        with pytest.raises(ValueError) as exc_info:
            GameDesignDocument.from_llm_response("not valid json {{{")
        assert "Invalid JSON" in str(exc_info.value)

    def test_gdd_summary(self, valid_gdd):
        """Test GDD summary generation."""
        summary = valid_gdd.get_summary()
        assert "Zombie Survival Roguelike" in summary
        assert "roguelike" in summary.lower()
        assert "CORE LOOP" in summary

    def test_gdd_to_dict(self, valid_gdd):
        """Test GDD to dictionary conversion."""
        data = valid_gdd.to_dict()
        assert isinstance(data, dict)
        assert data["meta"]["title"] == "Zombie Survival Roguelike"


# =============================================================================
# CRITIC FEEDBACK TESTS
# =============================================================================


class TestCriticFeedback:
    """Test CriticFeedback model for Dual-Agent system."""

    def test_valid_approve_feedback(self):
        """Test creating valid approval feedback."""
        feedback = CriticFeedback(
            decision=Decision.APPROVE,
            blocking_issues=[],
            feasibility_score=8,
            coherence_score=9,
            fun_factor_score=8,
            completeness_score=9,
            originality_score=7,
        )
        assert feedback.is_approved
        assert feedback.overall_score > 7

    def test_valid_revise_feedback(self):
        """Test creating valid revision feedback."""
        feedback = CriticFeedback(
            decision=Decision.REVISE,
            blocking_issues=[
                BlockingIssue(
                    section="core_loop",
                    issue="The core loop lacks clear feedback mechanisms",
                    severity=Severity.MAJOR,
                    suggestion="Add at least 3 feedback mechanisms for player actions",
                )
            ],
            feasibility_score=6,
            coherence_score=5,
            fun_factor_score=4,
            completeness_score=5,
            originality_score=6,
        )
        assert not feedback.is_approved
        assert len(feedback.blocking_issues) == 1

    def test_feedback_decision_consistency_approve_with_critical(self):
        """Test that approve cannot have critical issues."""
        with pytest.raises(ValidationError) as exc_info:
            CriticFeedback(
                decision=Decision.APPROVE,  # Trying to approve
                blocking_issues=[
                    BlockingIssue(
                        section="meta",
                        issue="Missing unique selling point",
                        severity=Severity.CRITICAL,  # But has critical issue
                        suggestion="Add a clear USP",
                    )
                ],
                feasibility_score=8,
                coherence_score=8,
                fun_factor_score=8,
                completeness_score=8,
                originality_score=8,
            )
        assert "approve" in str(exc_info.value).lower()

    def test_feedback_decision_consistency_revise_without_issues(self):
        """Test that revise requires issues."""
        with pytest.raises(ValidationError) as exc_info:
            CriticFeedback(
                decision=Decision.REVISE,  # Trying to revise
                blocking_issues=[],  # But no issues
                feasibility_score=8,
                coherence_score=8,
                fun_factor_score=8,
                completeness_score=8,
                originality_score=8,
            )
        assert "revise" in str(exc_info.value).lower()

    def test_feedback_score_bounds(self):
        """Test that scores must be 1-10."""
        with pytest.raises(ValidationError):
            CriticFeedback(
                decision=Decision.APPROVE,
                blocking_issues=[],
                feasibility_score=0,  # Below minimum
                coherence_score=8,
                fun_factor_score=8,
                completeness_score=8,
                originality_score=8,
            )

        with pytest.raises(ValidationError):
            CriticFeedback(
                decision=Decision.APPROVE,
                blocking_issues=[],
                feasibility_score=11,  # Above maximum
                coherence_score=8,
                fun_factor_score=8,
                completeness_score=8,
                originality_score=8,
            )

    def test_feedback_to_actor_feedback(self):
        """Test formatting feedback for actor revision."""
        feedback = CriticFeedback(
            decision=Decision.REVISE,
            blocking_issues=[
                BlockingIssue(
                    section="systems",
                    issue="Combat system lacks depth",
                    severity=Severity.MAJOR,
                    suggestion="Add combo system and enemy variety",
                )
            ],
            feasibility_score=7,
            coherence_score=6,
            fun_factor_score=5,
            completeness_score=7,
            originality_score=6,
            review_notes="Overall promising but needs more gameplay depth",
        )
        text = feedback.to_actor_feedback()
        assert "REVISE" in text
        assert "Combat system" in text
        assert "BLOCKING ISSUES" in text

    def test_feedback_from_llm_response(self):
        """Test parsing CriticFeedback from LLM response."""
        json_data = {
            "decision": "approve",
            "blocking_issues": [],
            "feasibility_score": 8,
            "coherence_score": 8,
            "fun_factor_score": 9,
            "completeness_score": 8,
            "originality_score": 7,
        }
        wrapped = f"```json\n{json.dumps(json_data)}\n```"
        feedback = CriticFeedback.from_llm_response(wrapped)
        assert feedback.is_approved


# =============================================================================
# REFINEMENT RESULT TESTS
# =============================================================================


class TestRefinementResult:
    """Test RefinementResult model."""

    def test_valid_refinement_result(self, valid_gdd):
        """Test creating a valid RefinementResult."""
        result = RefinementResult(
            final_gdd=valid_gdd,
            termination_reason=TerminationReason.APPROVED,
            total_iterations=2,
            total_duration_ms=5000.0,
            user_prompt="Create a zombie survival roguelike game",
            success=True,
        )
        assert result.success
        assert result.termination_reason == TerminationReason.APPROVED

    def test_refinement_result_summary(self, valid_gdd):
        """Test RefinementResult summary generation."""
        result = RefinementResult(
            final_gdd=valid_gdd,
            termination_reason=TerminationReason.APPROVED,
            total_iterations=2,
            total_duration_ms=5000.0,
            user_prompt="Create a zombie survival roguelike game",
            success=True,
        )
        summary = result.to_summary()
        assert "SUCCESS" in summary
        assert "Zombie Survival Roguelike" in summary


# =============================================================================
# EDGE CASES AND INTEGRATION TESTS
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_optional_fields(self, valid_gdd):
        """Test that optional fields can be None or empty."""
        gdd = valid_gdd.model_copy(deep=True)
        gdd_dict = gdd.to_dict()
        gdd_dict["map_hints"] = None
        gdd_dict["additional_notes"] = None
        restored = GameDesignDocument.model_validate(gdd_dict)
        assert restored.map_hints is None

    def test_maximum_length_strings(self):
        """Test fields at their maximum lengths."""
        meta = GameMeta(
            title="A" * 100,  # Max 100
            genres=[Genre.ACTION],
            target_platforms=[Platform.PC],
            target_audience="A" * 500,  # Max 500
            unique_selling_point="A" * 500,  # Max 500
            estimated_dev_time_weeks=520,  # Max 520
        )
        assert len(meta.title) == 100

    def test_unicode_content(self):
        """Test Unicode content in fields."""
        meta = GameMeta(
            title="Zombie Survival Roguelike",
            genres=[Genre.ROGUELIKE],
            target_platforms=[Platform.PC],
            target_audience="Gaming audience interested in Korean horror games",
            unique_selling_point="Korean aesthetic combined with roguelike mechanics",
            estimated_dev_time_weeks=52,
        )
        assert "Zombie" in meta.title

    def test_special_characters_in_strings(self):
        """Test special characters are handled properly."""
        meta = GameMeta(
            title='Game: "Survival" Edition (v2.0)',
            genres=[Genre.SURVIVAL],
            target_platforms=[Platform.PC],
            target_audience="Players who enjoy challenging survival games with depth",
            unique_selling_point="Unique crafting system with 1000+ recipes & combinations",
            estimated_dev_time_weeks=26,
        )
        json_str = meta.model_dump_json()
        restored = GameMeta.model_validate_json(json_str)
        assert '"Survival"' in restored.title

    def test_deeply_nested_model_validation(self, valid_gdd):
        """Test validation propagates through nested models."""
        json_str = valid_gdd.to_json()
        data = json.loads(json_str)
        # Corrupt a deeply nested field
        data["systems"][0]["parameters"][0]["name"] = ""  # Empty name should fail
        with pytest.raises(ValidationError):
            GameDesignDocument.model_validate(data)


# =============================================================================
# SERIALIZATION ROUND-TRIP TESTS
# =============================================================================


class TestSerializationRoundTrip:
    """Test that models survive JSON round-trips."""

    def test_full_gdd_round_trip(self, valid_gdd):
        """Test complete GDD survives JSON round-trip."""
        json_str = valid_gdd.to_json()
        restored = GameDesignDocument.from_json(json_str)

        # Verify key fields survived
        assert restored.meta.title == valid_gdd.meta.title
        assert restored.meta.genres == valid_gdd.meta.genres
        assert len(restored.systems) == len(valid_gdd.systems)
        assert restored.progression.type == valid_gdd.progression.type
        assert restored.narrative.themes == valid_gdd.narrative.themes

    def test_critic_feedback_round_trip(self):
        """Test CriticFeedback survives JSON round-trip."""
        feedback = CriticFeedback(
            decision=Decision.REVISE,
            blocking_issues=[
                BlockingIssue(
                    section="meta",
                    issue="USP is not unique enough",
                    severity=Severity.MAJOR,
                    suggestion="Differentiate from existing games in the market",
                )
            ],
            feasibility_score=7,
            coherence_score=8,
            fun_factor_score=6,
            completeness_score=8,
            originality_score=5,
        )
        json_str = feedback.model_dump_json()
        restored = CriticFeedback.model_validate_json(json_str)
        assert restored.decision == feedback.decision
        assert len(restored.blocking_issues) == 1
