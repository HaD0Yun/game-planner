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

from main import (
    app,
    gdd_to_markdown,
    gdd_to_game_generator_prompt,
    gdd_to_map_hints_prompt,
    OutputFormat,
)
from html_template import gdd_to_html
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

    def test_plan_with_game_generator_format(
        self, cli_runner: CliRunner, temp_dir: Path
    ) -> None:
        """Test plan command with game-generator output format."""
        output_file = temp_dir / "game_prompt.txt"
        result = cli_runner.invoke(
            app,
            [
                "plan",
                "space shooter arcade game",
                "--mock",
                "--format",
                "game-generator",
                "--output",
                str(output_file),
                "--no-preview",
            ],
        )

        assert result.exit_code == 0, f"CLI failed: {result.stdout}"
        assert output_file.exists(), "Output file was not created"

        content = output_file.read_text(encoding="utf-8")
        # Should contain game-generator prompt elements
        assert "Create a browser game" in content
        assert "GAMEPLAY:" in content
        assert "KEY MECHANICS:" in content
        assert "REQUIREMENTS:" in content


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

    def test_game_generator_format_value(self) -> None:
        """Test game-generator format value."""
        assert OutputFormat.GAME_GENERATOR.value == "game-generator"

    def test_map_hints_format_value(self) -> None:
        """Test map-hints format value."""
        assert OutputFormat.MAP_HINTS.value == "map-hints"

    def test_format_enum_members(self) -> None:
        """Test all format enum members exist."""
        formats = list(OutputFormat)
        assert len(formats) == 5
        assert OutputFormat.JSON in formats
        assert OutputFormat.MARKDOWN in formats
        assert OutputFormat.GAME_GENERATOR in formats
        assert OutputFormat.MAP_HINTS in formats
        assert OutputFormat.HTML in formats

    def test_html_format_value(self) -> None:
        """Test HTML format value."""
        assert OutputFormat.HTML.value == "html"


# =============================================================================
# GDD TO HTML CONVERSION TESTS
# =============================================================================


class TestGddToHtml:
    """Tests for GDD to HTML conversion."""

    def test_html_contains_doctype(self, sample_gdd: GameDesignDocument) -> None:
        """Test HTML output contains DOCTYPE declaration."""
        html = gdd_to_html(sample_gdd)
        assert "<!DOCTYPE html>" in html

    def test_html_contains_title(self, sample_gdd: GameDesignDocument) -> None:
        """Test HTML output contains game title."""
        html = gdd_to_html(sample_gdd)
        assert sample_gdd.meta.title in html
        assert f"<title>{sample_gdd.meta.title}" in html

    def test_html_contains_meta_viewport(self, sample_gdd: GameDesignDocument) -> None:
        """Test HTML output contains responsive viewport meta tag."""
        html = gdd_to_html(sample_gdd)
        assert 'name="viewport"' in html

    def test_html_contains_embedded_css(self, sample_gdd: GameDesignDocument) -> None:
        """Test HTML output contains embedded CSS."""
        html = gdd_to_html(sample_gdd)
        assert "<style>" in html
        assert "</style>" in html
        # Check for key CSS variables
        assert "--bg-primary" in html
        assert "--accent" in html
        assert "--neon-blue" in html

    def test_html_contains_hero_section(self, sample_gdd: GameDesignDocument) -> None:
        """Test HTML output contains hero section."""
        html = gdd_to_html(sample_gdd)
        assert 'class="hero"' in html
        assert "<h1>" in html

    def test_html_contains_navigation(self, sample_gdd: GameDesignDocument) -> None:
        """Test HTML output contains navigation bar."""
        html = gdd_to_html(sample_gdd)
        assert 'class="nav"' in html
        assert 'href="#meta"' in html
        assert 'href="#core-loop"' in html

    def test_html_contains_core_loop_section(
        self, sample_gdd: GameDesignDocument
    ) -> None:
        """Test HTML output contains core loop section."""
        html = gdd_to_html(sample_gdd)
        assert 'id="core-loop"' in html
        assert "Core Loop" in html
        # Check that primary actions are present
        for action in sample_gdd.core_loop.primary_actions:
            assert action in html

    def test_html_contains_systems_section(
        self, sample_gdd: GameDesignDocument
    ) -> None:
        """Test HTML output contains systems section."""
        html = gdd_to_html(sample_gdd)
        assert 'id="systems"' in html
        for system in sample_gdd.systems:
            assert system.name in html

    def test_html_contains_progression_section(
        self, sample_gdd: GameDesignDocument
    ) -> None:
        """Test HTML output contains progression section."""
        html = gdd_to_html(sample_gdd)
        assert 'id="progression"' in html
        assert "Milestones" in html

    def test_html_contains_narrative_section(
        self, sample_gdd: GameDesignDocument
    ) -> None:
        """Test HTML output contains narrative section."""
        html = gdd_to_html(sample_gdd)
        assert 'id="narrative"' in html
        assert "Story" in html
        # Setting should be present
        assert sample_gdd.narrative.setting[:30] in html

    def test_html_contains_characters_section(
        self, sample_gdd: GameDesignDocument
    ) -> None:
        """Test HTML output contains characters section when characters exist."""
        html = gdd_to_html(sample_gdd)
        if sample_gdd.narrative.characters:
            assert 'id="characters"' in html
            for char in sample_gdd.narrative.characters:
                assert char.name in html

    def test_html_contains_technical_section(
        self, sample_gdd: GameDesignDocument
    ) -> None:
        """Test HTML output contains technical specs section."""
        html = gdd_to_html(sample_gdd)
        assert 'id="tech"' in html
        assert sample_gdd.technical.recommended_engine.value in html.lower()
        assert sample_gdd.technical.art_style.value.replace("_", " ") in html.lower()

    def test_html_contains_footer(self, sample_gdd: GameDesignDocument) -> None:
        """Test HTML output contains footer with metadata."""
        html = gdd_to_html(sample_gdd)
        assert "<footer>" in html
        assert sample_gdd.schema_version in html

    def test_html_escapes_special_characters(
        self, sample_gdd: GameDesignDocument
    ) -> None:
        """Test HTML properly escapes special characters."""
        # Create a GDD with special characters
        gdd_with_special = sample_gdd.model_copy(deep=True)
        gdd_dict = gdd_with_special.model_dump()
        gdd_dict["meta"]["title"] = "Test <Game> & 'Stuff'"
        gdd_special = GameDesignDocument.model_validate(gdd_dict)

        html = gdd_to_html(gdd_special)
        # Should be escaped
        assert "&lt;Game&gt;" in html
        assert "&amp;" in html

    def test_html_is_non_empty_string(self, sample_gdd: GameDesignDocument) -> None:
        """Test HTML output is a substantial non-empty string."""
        html = gdd_to_html(sample_gdd)
        assert isinstance(html, str)
        assert len(html) > 1000  # HTML should be substantial


# =============================================================================
# CLI HTML FORMAT TESTS
# =============================================================================


class TestPlanCommandHtml:
    """Tests for the plan command with HTML format."""

    def test_plan_with_html_format(self, cli_runner: CliRunner, temp_dir: Path) -> None:
        """Test plan command with HTML output format."""
        output_file = temp_dir / "test_output.html"
        result = cli_runner.invoke(
            app,
            [
                "plan",
                "puzzle adventure game",
                "--mock",
                "--format",
                "html",
                "--output",
                str(output_file),
                "--no-preview",
            ],
        )

        assert result.exit_code == 0, f"CLI failed: {result.stdout}"
        assert output_file.exists(), "Output file was not created"

        content = output_file.read_text(encoding="utf-8")
        # Should be valid HTML
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "</html>" in content

    def test_plan_html_contains_required_sections(
        self, cli_runner: CliRunner, temp_dir: Path
    ) -> None:
        """Test HTML output contains all required sections."""
        output_file = temp_dir / "test_sections.html"
        result = cli_runner.invoke(
            app,
            [
                "plan",
                "roguelike shooter",
                "--mock",
                "--format",
                "html",
                "--output",
                str(output_file),
                "--no-preview",
            ],
        )

        assert result.exit_code == 0
        content = output_file.read_text(encoding="utf-8")

        # Check for required sections
        assert 'class="hero"' in content
        assert 'class="nav"' in content
        assert 'id="meta"' in content
        assert 'id="core-loop"' in content
        assert 'id="systems"' in content
        assert 'id="progression"' in content
        assert 'id="narrative"' in content
        assert 'id="tech"' in content

    def test_plan_html_contains_dark_theme_css(
        self, cli_runner: CliRunner, temp_dir: Path
    ) -> None:
        """Test HTML output contains dark theme CSS variables."""
        output_file = temp_dir / "test_theme.html"
        result = cli_runner.invoke(
            app,
            [
                "plan",
                "space exploration",
                "--mock",
                "--format",
                "html",
                "--output",
                str(output_file),
                "--no-preview",
            ],
        )

        assert result.exit_code == 0
        content = output_file.read_text(encoding="utf-8")

        # Check for dark theme CSS
        assert "--bg-primary" in content
        assert "--bg-secondary" in content
        assert "--accent" in content
        assert "--neon-blue" in content
        assert "--neon-green" in content


# =============================================================================
# GDD TO GAME-GENERATOR PROMPT CONVERSION TESTS
# =============================================================================


class TestGddToGameGeneratorPrompt:
    """Tests for GDD to game-generator prompt conversion."""

    def test_prompt_contains_title(self, sample_gdd: GameDesignDocument) -> None:
        """Test game-generator prompt contains game title."""
        prompt = gdd_to_game_generator_prompt(sample_gdd)
        assert sample_gdd.meta.title in prompt

    def test_prompt_contains_genres(self, sample_gdd: GameDesignDocument) -> None:
        """Test game-generator prompt contains genres."""
        prompt = gdd_to_game_generator_prompt(sample_gdd)
        for genre in sample_gdd.meta.genres:
            assert genre.value in prompt

    def test_prompt_contains_gameplay_section(
        self, sample_gdd: GameDesignDocument
    ) -> None:
        """Test game-generator prompt contains gameplay section."""
        prompt = gdd_to_game_generator_prompt(sample_gdd)
        assert "GAMEPLAY:" in prompt
        assert "Primary actions:" in prompt
        assert "Challenge:" in prompt
        assert "Rewards:" in prompt

    def test_prompt_contains_mechanics(self, sample_gdd: GameDesignDocument) -> None:
        """Test game-generator prompt contains key mechanics."""
        prompt = gdd_to_game_generator_prompt(sample_gdd)
        assert "KEY MECHANICS:" in prompt
        # Should contain at least one system name
        assert any(system.name in prompt for system in sample_gdd.systems)

    def test_prompt_contains_visual_style(self, sample_gdd: GameDesignDocument) -> None:
        """Test game-generator prompt contains visual style."""
        prompt = gdd_to_game_generator_prompt(sample_gdd)
        assert "VISUAL STYLE:" in prompt
        assert sample_gdd.technical.art_style.value in prompt

    def test_prompt_contains_unique_features(
        self, sample_gdd: GameDesignDocument
    ) -> None:
        """Test game-generator prompt contains unique features."""
        prompt = gdd_to_game_generator_prompt(sample_gdd)
        assert "UNIQUE FEATURES:" in prompt
        assert sample_gdd.meta.unique_selling_point in prompt

    def test_prompt_contains_requirements(self, sample_gdd: GameDesignDocument) -> None:
        """Test game-generator prompt contains browser game requirements."""
        prompt = gdd_to_game_generator_prompt(sample_gdd)
        assert "REQUIREMENTS:" in prompt
        assert "HTML" in prompt
        assert "score" in prompt.lower()
        assert "restart" in prompt.lower()

    def test_prompt_contains_elevator_pitch_when_present(
        self, sample_gdd: GameDesignDocument
    ) -> None:
        """Test game-generator prompt contains elevator pitch when present."""
        prompt = gdd_to_game_generator_prompt(sample_gdd)
        if sample_gdd.meta.elevator_pitch:
            assert sample_gdd.meta.elevator_pitch in prompt

    def test_prompt_is_non_empty_string(self, sample_gdd: GameDesignDocument) -> None:
        """Test game-generator prompt is a non-empty string."""
        prompt = gdd_to_game_generator_prompt(sample_gdd)
        assert isinstance(prompt, str)
        assert len(prompt) > 100  # Should be a substantial prompt


# =============================================================================
# GDD TO MAP HINTS PROMPT CONVERSION TESTS
# =============================================================================


class TestGddToMapHintsPrompt:
    """Tests for GDD to map hints prompt conversion."""

    def test_prompt_contains_title(self, sample_gdd: GameDesignDocument) -> None:
        """Test map hints prompt contains game title."""
        prompt = gdd_to_map_hints_prompt(sample_gdd)
        assert sample_gdd.meta.title in prompt

    def test_prompt_without_map_hints(self, sample_gdd: GameDesignDocument) -> None:
        """Test map hints prompt when GDD has no map_hints."""
        # Create a GDD without map_hints
        gdd_without_hints = sample_gdd.model_copy(deep=True)
        gdd_without_hints_dict = gdd_without_hints.model_dump()
        gdd_without_hints_dict["map_hints"] = None
        gdd_no_hints = GameDesignDocument.model_validate(gdd_without_hints_dict)

        prompt = gdd_to_map_hints_prompt(gdd_no_hints)

        assert "No Map Hints Available" in prompt
        assert "Derived from Game Design" in prompt
        assert "Setting:" in prompt
        assert "Suggested /Map Command" in prompt

    def test_prompt_with_map_hints_contains_biomes(
        self, sample_gdd: GameDesignDocument
    ) -> None:
        """Test map hints prompt contains biomes when map_hints present."""

        # Add map_hints to sample_gdd
        gdd_with_hints = sample_gdd.model_copy(deep=True)
        gdd_dict = gdd_with_hints.model_dump()
        gdd_dict["map_hints"] = {
            "biomes": ["urban", "ruins"],
            "map_size": "large",
            "obstacles": [
                {
                    "type": "wall",
                    "density": "medium",
                    "purpose": "Create chokepoints for defensive gameplay",
                }
            ],
            "special_features": [
                {
                    "name": "Safe Room",
                    "frequency": "rare",
                    "requirements": ["Near spawn point"],
                    "description": "A fortified room where players can rest and save",
                }
            ],
            "connectivity": "high",
            "generation_style": "procedural_rooms",
        }
        gdd_hints = GameDesignDocument.model_validate(gdd_dict)

        prompt = gdd_to_map_hints_prompt(gdd_hints)

        assert "## Biomes" in prompt
        assert "urban" in prompt
        assert "ruins" in prompt

    def test_prompt_with_map_hints_contains_configuration(
        self, sample_gdd: GameDesignDocument
    ) -> None:
        """Test map hints prompt contains map configuration."""

        gdd_with_hints = sample_gdd.model_copy(deep=True)
        gdd_dict = gdd_with_hints.model_dump()
        gdd_dict["map_hints"] = {
            "biomes": ["forest"],
            "map_size": "medium",
            "connectivity": "high",
            "verticality": "low",
            "generation_style": "cellular_automata",
        }
        gdd_hints = GameDesignDocument.model_validate(gdd_dict)

        prompt = gdd_to_map_hints_prompt(gdd_hints)

        assert "## Map Configuration" in prompt
        assert "Size:" in prompt
        assert "medium" in prompt
        assert "Connectivity:" in prompt
        assert "high" in prompt

    def test_prompt_contains_map_command_reference(
        self, sample_gdd: GameDesignDocument
    ) -> None:
        """Test map hints prompt contains /Map command reference."""

        gdd_with_hints = sample_gdd.model_copy(deep=True)
        gdd_dict = gdd_with_hints.model_dump()
        gdd_dict["map_hints"] = {
            "biomes": ["dungeon"],
            "map_size": "small",
            "connectivity": "medium",
            "generation_style": "bsp_dungeon",
        }
        gdd_hints = GameDesignDocument.model_validate(gdd_dict)

        prompt = gdd_to_map_hints_prompt(gdd_hints)

        assert "## /Map Command Reference" in prompt
        assert "/Map" in prompt
        assert "biomes:" in prompt

    def test_prompt_contains_twc4_hints(self, sample_gdd: GameDesignDocument) -> None:
        """Test map hints prompt contains TWC4 configuration hints."""

        gdd_with_hints = sample_gdd.model_copy(deep=True)
        gdd_dict = gdd_with_hints.model_dump()
        gdd_dict["map_hints"] = {
            "biomes": ["cave"],
            "map_size": "large",
            "generation_style": "cellular_automata",
        }
        gdd_hints = GameDesignDocument.model_validate(gdd_dict)

        prompt = gdd_to_map_hints_prompt(gdd_hints)

        assert "## TileWorldCreator4 Configuration Hints" in prompt
        assert "Suggested Generator:" in prompt
        assert "Suggested Grid Size:" in prompt

    def test_prompt_contains_json_export(self, sample_gdd: GameDesignDocument) -> None:
        """Test map hints prompt contains JSON export section."""

        gdd_with_hints = sample_gdd.model_copy(deep=True)
        gdd_dict = gdd_with_hints.model_dump()
        gdd_dict["map_hints"] = {
            "biomes": ["plains"],
            "map_size": "medium",
        }
        gdd_hints = GameDesignDocument.model_validate(gdd_dict)

        prompt = gdd_to_map_hints_prompt(gdd_hints)

        assert "## JSON Export" in prompt
        assert "```json" in prompt

    def test_prompt_is_non_empty_string(self, sample_gdd: GameDesignDocument) -> None:
        """Test map hints prompt is a non-empty string."""
        prompt = gdd_to_map_hints_prompt(sample_gdd)
        assert isinstance(prompt, str)
        assert len(prompt) > 50  # Should be a substantial output


# =============================================================================
# CLI MAP HINTS FORMAT TESTS
# =============================================================================


class TestPlanCommandMapHints:
    """Tests for the plan command with map-hints format."""

    def test_plan_with_map_hints_format(
        self, cli_runner: CliRunner, temp_dir: Path
    ) -> None:
        """Test plan command with map-hints output format."""
        output_file = temp_dir / "map_hints.txt"
        result = cli_runner.invoke(
            app,
            [
                "plan",
                "dungeon crawler roguelike",
                "--mock",
                "--format",
                "map-hints",
                "--output",
                str(output_file),
                "--no-preview",
            ],
        )

        assert result.exit_code == 0, f"CLI failed: {result.stdout}"
        assert output_file.exists(), "Output file was not created"

        content = output_file.read_text(encoding="utf-8")
        # Should contain map hints header
        assert "Map Generation Hints" in content

    def test_plan_map_hints_contains_map_command(
        self, cli_runner: CliRunner, temp_dir: Path
    ) -> None:
        """Test map-hints output contains /Map command suggestion."""
        output_file = temp_dir / "map_hints.txt"
        result = cli_runner.invoke(
            app,
            [
                "plan",
                "exploration adventure game",
                "--mock",
                "--format",
                "map-hints",
                "--output",
                str(output_file),
                "--no-preview",
            ],
        )

        assert result.exit_code == 0
        content = output_file.read_text(encoding="utf-8")
        # Should contain /Map command reference
        assert "/Map" in content


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
