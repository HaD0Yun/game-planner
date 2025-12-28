"""
test_cli.py - Tests for the CLI Entry Point

Tests cover:
- CLI command invocation
- JSON and Markdown output formats
- Mock mode functionality
- Validation command
- Error handling
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from typer.testing import CliRunner

from main import app, gdd_to_markdown, OutputFormat
from models import (
    GameDesignDocument,
    GameMeta,
    CoreLoop,
    GameSystem,
    Progression,
    Narrative,
    TechnicalSpec,
    Genre,
    Platform,
    AudienceRating,
    GameEngine,
    ArtStyle,
    SystemType,
    ProgressionType,
    Milestone,
    Character,
    PerformanceTarget,
    AudioRequirements,
    NarrativeDelivery,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_gdd() -> GameDesignDocument:
    """Create a sample GDD for testing."""
    return GameDesignDocument(
        meta=GameMeta(
            title="Test Game",
            genres=[Genre.ACTION, Genre.ROGUELIKE],
            target_platforms=[Platform.PC, Platform.WEB],
            target_audience="Players who enjoy challenging roguelike experiences",
            audience_rating=AudienceRating.TEEN,
            unique_selling_point="This is a unique selling point that is long enough to pass validation",
            estimated_dev_time_weeks=12,
            team_size_estimate=3,
            elevator_pitch="A test game for testing purposes",
        ),
        core_loop=CoreLoop(
            primary_actions=["explore", "fight", "loot"],
            challenge_description="Survive increasingly difficult enemy waves",
            reward_description="Upgrade weapons and abilities",
            loop_description="Players explore procedural dungeons, fight enemies, collect loot, and upgrade their character between runs.",
            session_length_minutes=30,
            hook_elements=["Permanent upgrades", "Unlockable characters"],
        ),
        systems=[
            GameSystem(
                name="Combat System",
                type=SystemType.COMBAT,
                description="Real-time action combat with dodge mechanics and combo attacks.",
                mechanics=["Light attack", "Heavy attack", "Dodge"],
                priority=1,
            ),
            GameSystem(
                name="Loot System",
                type=SystemType.INVENTORY,
                description="Randomized loot drops with rarity tiers and stat bonuses.",
                mechanics=["Item pickup", "Inventory management", "Equipment"],
                priority=2,
            ),
            GameSystem(
                name="Upgrade System",
                type=SystemType.LEVELING,
                description="Meta-progression with permanent upgrades between runs.",
                mechanics=["XP gain", "Level up", "Skill unlock"],
                priority=3,
            ),
        ],
        progression=Progression(
            type=ProgressionType.ROGUELIKE_RUNS,
            milestones=[
                Milestone(
                    name="First Boss",
                    description="Defeat the first boss",
                    unlock_condition="Complete level 5",
                ),
                Milestone(
                    name="New Character",
                    description="Unlock a new character",
                    unlock_condition="Complete 10 runs",
                ),
                Milestone(
                    name="Hard Mode",
                    description="Unlock hard mode",
                    unlock_condition="Beat the game",
                ),
                Milestone(
                    name="True Ending",
                    description="See the true ending",
                    unlock_condition="Beat hard mode",
                ),
                Milestone(
                    name="Completionist",
                    description="Unlock everything",
                    unlock_condition="100% completion",
                ),
            ],
            difficulty_curve_description="Difficulty increases with each dungeon level. Enemy health and damage scale, new enemy types appear.",
        ),
        narrative=Narrative(
            setting="A dark fantasy world overrun by monsters after a magical cataclysm.",
            story_premise="You are the last survivor of a fallen kingdom, seeking to reclaim your homeland.",
            themes=["redemption", "survival", "hope"],
            characters=[
                Character(
                    name="The Hero",
                    role="Protagonist",
                    description="A fallen knight seeking redemption.",
                ),
            ],
            narrative_delivery=[
                NarrativeDelivery.ENVIRONMENTAL,
                NarrativeDelivery.DIALOGUE,
            ],
            story_structure="Episodic, with lore revealed through item descriptions and NPC encounters.",
        ),
        technical=TechnicalSpec(
            recommended_engine=GameEngine.UNITY,
            art_style=ArtStyle.PIXEL_ART,
            key_technologies=["Unity 2D", "Procedural generation", "Save system"],
            performance_targets=[
                PerformanceTarget(
                    platform=Platform.PC,
                    target_fps=60,
                    min_resolution="1920x1080",
                    max_ram_mb=512,
                ),
            ],
            audio=AudioRequirements(
                music_style="Dark fantasy orchestral",
                sound_categories=["Ambient", "Combat", "UI"],
            ),
        ),
    )


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# =============================================================================
# BASIC CLI TESTS
# =============================================================================


class TestCLIBasic:
    """Basic CLI functionality tests."""

    def test_help_command(self, cli_runner: CliRunner) -> None:
        """Test --help shows usage information."""
        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert (
            "Game Design Document" in result.stdout or "game-planner" in result.stdout
        )

    def test_plan_help(self, cli_runner: CliRunner) -> None:
        """Test plan --help shows command usage."""
        result = cli_runner.invoke(app, ["plan", "--help"])
        assert result.exit_code == 0
        assert "prompt" in result.stdout.lower()
        assert "--output" in result.stdout or "-o" in result.stdout

    def test_version_command(self, cli_runner: CliRunner) -> None:
        """Test version command shows version info."""
        result = cli_runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Game Planner" in result.stdout
        assert "Version" in result.stdout or "0.1.0" in result.stdout

    def test_missing_concept_shows_error(self, cli_runner: CliRunner) -> None:
        """Test that missing concept argument shows error."""
        result = cli_runner.invoke(app, ["plan"])
        assert result.exit_code != 0


# =============================================================================
# PLAN COMMAND TESTS
# =============================================================================


class TestPlanCommand:
    """Tests for the plan command."""

    def test_plan_with_mock_json(self, cli_runner: CliRunner, temp_dir: Path) -> None:
        """Test plan command with mock mode produces JSON output."""
        output_file = temp_dir / "test_output.json"
        result = cli_runner.invoke(
            app,
            [
                "plan",
                "test roguelike game",
                "--mock",
                "--output",
                str(output_file),
                "--no-preview",
            ],
        )

        # Should succeed
        assert result.exit_code == 0, f"CLI failed: {result.stdout}"

        # Output file should exist
        assert output_file.exists(), "Output file was not created"

        # Should be valid JSON
        content = output_file.read_text(encoding="utf-8")
        data = json.loads(content)
        assert "meta" in data
        assert "core_loop" in data

    def test_plan_with_mock_markdown(
        self, cli_runner: CliRunner, temp_dir: Path
    ) -> None:
        """Test plan command with markdown output format."""
        output_file = temp_dir / "test_output.md"
        result = cli_runner.invoke(
            app,
            [
                "plan",
                "puzzle platformer",
                "--mock",
                "--format",
                "markdown",
                "--output",
                str(output_file),
                "--no-preview",
            ],
        )

        assert result.exit_code == 0, f"CLI failed: {result.stdout}"
        assert output_file.exists()

        content = output_file.read_text(encoding="utf-8")
        # Markdown should have headers
        assert "#" in content
        # Should contain game info
        assert "Core Loop" in content or "Systems" in content

    def test_plan_custom_iterations(
        self, cli_runner: CliRunner, temp_dir: Path
    ) -> None:
        """Test plan with custom max iterations."""
        output_file = temp_dir / "output.json"
        result = cli_runner.invoke(
            app,
            [
                "plan",
                "simple game",
                "--mock",
                "--max-iterations",
                "1",
                "--output",
                str(output_file),
                "--no-preview",
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()

    def test_plan_shows_progress(self, cli_runner: CliRunner, temp_dir: Path) -> None:
        """Test that plan command shows progress information."""
        output_file = temp_dir / "output.json"
        result = cli_runner.invoke(
            app,
            [
                "plan",
                "RPG game",
                "--mock",
                "--output",
                str(output_file),
                "--no-preview",
            ],
        )

        assert result.exit_code == 0
        # Should show some progress/status information
        output = result.stdout.lower()
        assert (
            "generation" in output
            or "approved" in output
            or "best effort" in output
            or "iteration" in output
        )

    def test_plan_quiet_mode(self, cli_runner: CliRunner, temp_dir: Path) -> None:
        """Test quiet mode suppresses progress output."""
        output_file = temp_dir / "output.json"
        result = cli_runner.invoke(
            app,
            [
                "plan",
                "quiet test game",
                "--mock",
                "--quiet",
                "--output",
                str(output_file),
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()


# =============================================================================
# VALIDATE COMMAND TESTS
# =============================================================================


class TestValidateCommand:
    """Tests for the validate command."""

    def test_validate_valid_gdd(
        self, cli_runner: CliRunner, sample_gdd: GameDesignDocument, temp_dir: Path
    ) -> None:
        """Test validate command with valid GDD file."""
        gdd_file = temp_dir / "valid_gdd.json"
        gdd_file.write_text(sample_gdd.model_dump_json(indent=2), encoding="utf-8")

        result = cli_runner.invoke(app, ["validate", str(gdd_file)])

        assert result.exit_code == 0
        assert "Valid" in result.stdout or "valid" in result.stdout.lower()
        assert sample_gdd.meta.title in result.stdout

    def test_validate_missing_file(self, cli_runner: CliRunner) -> None:
        """Test validate command with missing file."""
        result = cli_runner.invoke(app, ["validate", "nonexistent.json"])

        assert result.exit_code == 1
        assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()

    def test_validate_invalid_json(self, cli_runner: CliRunner, temp_dir: Path) -> None:
        """Test validate command with invalid JSON."""
        invalid_file = temp_dir / "invalid.json"
        invalid_file.write_text("{ invalid json }", encoding="utf-8")

        result = cli_runner.invoke(app, ["validate", str(invalid_file)])

        assert result.exit_code == 1
        assert "json" in result.stdout.lower() or "error" in result.stdout.lower()

    def test_validate_invalid_schema(
        self, cli_runner: CliRunner, temp_dir: Path
    ) -> None:
        """Test validate command with valid JSON but invalid GDD schema."""
        invalid_gdd = temp_dir / "bad_schema.json"
        invalid_gdd.write_text('{"title": "missing required fields"}', encoding="utf-8")

        result = cli_runner.invoke(app, ["validate", str(invalid_gdd)])

        assert result.exit_code == 1
        assert "failed" in result.stdout.lower() or "error" in result.stdout.lower()


# =============================================================================
# GDD TO MARKDOWN CONVERSION TESTS
# =============================================================================


class TestGddToMarkdown:
    """Tests for GDD to Markdown conversion."""

    def test_markdown_contains_title(self, sample_gdd: GameDesignDocument) -> None:
        """Test markdown output contains game title."""
        md = gdd_to_markdown(sample_gdd)
        assert f"# {sample_gdd.meta.title}" in md

    def test_markdown_contains_genres(self, sample_gdd: GameDesignDocument) -> None:
        """Test markdown output contains genres."""
        md = gdd_to_markdown(sample_gdd)
        for genre in sample_gdd.meta.genres:
            assert genre.value in md

    def test_markdown_contains_core_loop(self, sample_gdd: GameDesignDocument) -> None:
        """Test markdown output contains core loop info."""
        md = gdd_to_markdown(sample_gdd)
        assert "Core Loop" in md
        assert str(sample_gdd.core_loop.session_length_minutes) in md

    def test_markdown_contains_systems(self, sample_gdd: GameDesignDocument) -> None:
        """Test markdown output contains game systems."""
        md = gdd_to_markdown(sample_gdd)
        assert "Game Systems" in md
        for system in sample_gdd.systems:
            assert system.name in md

    def test_markdown_contains_progression(
        self, sample_gdd: GameDesignDocument
    ) -> None:
        """Test markdown output contains progression info."""
        md = gdd_to_markdown(sample_gdd)
        assert "Progression" in md
        assert "Milestones" in md

    def test_markdown_contains_narrative(self, sample_gdd: GameDesignDocument) -> None:
        """Test markdown output contains narrative info."""
        md = gdd_to_markdown(sample_gdd)
        assert "Narrative" in md
        assert sample_gdd.narrative.setting[:30] in md

    def test_markdown_contains_technical(self, sample_gdd: GameDesignDocument) -> None:
        """Test markdown output contains technical specs."""
        md = gdd_to_markdown(sample_gdd)
        assert "Technical" in md
        assert sample_gdd.technical.recommended_engine.value in md

    def test_markdown_contains_metadata(self, sample_gdd: GameDesignDocument) -> None:
        """Test markdown output contains generation metadata."""
        md = gdd_to_markdown(sample_gdd)
        assert "Schema Version" in md
        assert sample_gdd.schema_version in md

    def test_markdown_contains_elevator_pitch(
        self, sample_gdd: GameDesignDocument
    ) -> None:
        """Test markdown output contains elevator pitch when present."""
        md = gdd_to_markdown(sample_gdd)
        if sample_gdd.meta.elevator_pitch:
            assert sample_gdd.meta.elevator_pitch in md


# =============================================================================
# OUTPUT FORMAT ENUM TESTS
# =============================================================================


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    def test_json_format_value(self) -> None:
        """Test JSON format value."""
        assert OutputFormat.JSON.value == "json"

    def test_markdown_format_value(self) -> None:
        """Test Markdown format value."""
        assert OutputFormat.MARKDOWN.value == "markdown"

    def test_format_enum_members(self) -> None:
        """Test all format enum members exist."""
        formats = list(OutputFormat)
        assert len(formats) == 2
        assert OutputFormat.JSON in formats
        assert OutputFormat.MARKDOWN in formats


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


class TestErrorHandling:
    """Tests for CLI error handling."""

    def test_missing_prompt_argument(self, cli_runner: CliRunner) -> None:
        """Test error when prompt argument is missing."""
        result = cli_runner.invoke(app, ["plan"])
        assert result.exit_code != 0

    def test_invalid_format_option(self, cli_runner: CliRunner, temp_dir: Path) -> None:
        """Test error with invalid format option."""
        output_file = temp_dir / "output.json"
        result = cli_runner.invoke(
            app,
            [
                "plan",
                "test game",
                "--mock",
                "--format",
                "invalid_format",
                "--output",
                str(output_file),
            ],
        )
        assert result.exit_code != 0

    def test_invalid_max_iterations(
        self, cli_runner: CliRunner, temp_dir: Path
    ) -> None:
        """Test error with invalid max iterations (too high)."""
        output_file = temp_dir / "output.json"
        result = cli_runner.invoke(
            app,
            [
                "plan",
                "test game",
                "--mock",
                "--max-iterations",
                "100",  # Max is 10
                "--output",
                str(output_file),
            ],
        )
        assert result.exit_code != 0


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests for the complete CLI workflow."""

    def test_full_workflow_json(self, cli_runner: CliRunner, temp_dir: Path) -> None:
        """Test complete workflow: generate -> validate."""
        output_file = temp_dir / "full_test.json"

        # Generate
        gen_result = cli_runner.invoke(
            app,
            [
                "plan",
                "adventure puzzle game with mystery elements",
                "--mock",
                "--output",
                str(output_file),
                "--no-preview",
            ],
        )
        assert gen_result.exit_code == 0
        assert output_file.exists()

        # Validate
        val_result = cli_runner.invoke(app, ["validate", str(output_file)])
        assert val_result.exit_code == 0

    def test_stdout_output_when_no_file(self, cli_runner: CliRunner) -> None:
        """Test that output goes to stdout when no file specified."""
        result = cli_runner.invoke(
            app,
            [
                "plan",
                "simple test game",
                "--mock",
                "--quiet",
            ],
        )

        assert result.exit_code == 0
        # Output should contain JSON (since default is JSON format)
        assert "{" in result.stdout
        assert "meta" in result.stdout
