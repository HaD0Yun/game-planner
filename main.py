"""
main.py - CLI Entry Point for Game Planner

This module provides the command-line interface for generating
Game Design Documents using the Dual-Agent Actor-Critic architecture.

Usage:
    python -m game_planner.main plan "zombie survival roguelike" --mock
    python -m game_planner.main plan "space exploration RPG" --output game.json
    python -m game_planner.main plan "puzzle platformer" --format markdown
    python -m game_planner.main version
    python -m game_planner.main validate gdd.json
"""

from __future__ import annotations

import asyncio
import io
import json
import sys
from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from models import GameDesignDocument, RefinementResult
from orchestrator import GamePlanningOrchestrator, OrchestratorConfig
from llm_provider import create_provider
from html_template import gdd_to_html

# Fix encoding issues on Windows (CP949 can't handle Rich's Unicode spinners)
if sys.platform == "win32":
    try:
        if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace"
            )
    except Exception:
        pass  # Silently ignore encoding setup failures

# =============================================================================
# CLI APPLICATION
# =============================================================================

app = typer.Typer(
    name="game-planner",
    help="AI-Powered Game Design Document Generator using Dual-Agent Architecture",
    add_completion=False,
)
console = Console()


class OutputFormat(str, Enum):
    """Supported output formats."""

    JSON = "json"
    MARKDOWN = "markdown"
    GAME_GENERATOR = "game-generator"
    MAP_HINTS = "map-hints"
    HTML = "html"


class Provider(str, Enum):
    """Supported LLM providers."""

    MOCK = "mock"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def gdd_to_markdown(gdd: GameDesignDocument) -> str:
    """Convert a GDD to formatted Markdown."""
    lines = [
        f"# {gdd.meta.title}",
        "",
    ]

    # Add elevator pitch if available
    if gdd.meta.elevator_pitch:
        lines.append(f"> {gdd.meta.elevator_pitch}")
        lines.append("")

    lines.append("## Overview")
    lines.append("")
    lines.append(f"**Genres:** {', '.join(g.value for g in gdd.meta.genres)}")
    lines.append(
        f"**Platforms:** {', '.join(p.value for p in gdd.meta.target_platforms)}"
    )
    lines.append(f"**Target Audience:** {gdd.meta.target_audience}")
    lines.append(f"**Estimated Dev Time:** {gdd.meta.estimated_dev_time_weeks} weeks")
    lines.append("")
    lines.append("### Unique Selling Point")
    lines.append("")
    lines.append(gdd.meta.unique_selling_point)
    lines.append("")
    lines.append("## Core Loop")
    lines.append("")
    lines.append(f"**Primary Actions:** {', '.join(gdd.core_loop.primary_actions)}")
    lines.append(f"**Session Length:** {gdd.core_loop.session_length_minutes} minutes")
    lines.append("")
    lines.append("### Challenge")
    lines.append("")
    lines.append(gdd.core_loop.challenge_description)
    lines.append("")
    lines.append("### Rewards")
    lines.append("")
    lines.append(gdd.core_loop.reward_description)
    lines.append("")
    lines.append("### Loop Description")
    lines.append("")
    lines.append(gdd.core_loop.loop_description)
    lines.append("")
    lines.append("## Game Systems")
    lines.append("")

    for i, system in enumerate(gdd.systems, 1):
        lines.append(f"### {i}. {system.name} ({system.type.value})")
        lines.append("")
        lines.append(system.description)
        lines.append("")
        if system.mechanics:
            lines.append("**Mechanics:**")
            for mech in system.mechanics:
                lines.append(f"- {mech}")
            lines.append("")
        if system.parameters:
            lines.append("**Parameters:**")
            for param in system.parameters:
                lines.append(f"- `{param.name}`: {param.description}")
            lines.append("")

    lines.append("## Progression")
    lines.append("")
    lines.append(f"**Type:** {gdd.progression.type.value}")
    lines.append("")
    lines.append(gdd.progression.difficulty_curve_description)
    lines.append("")
    lines.append("### Milestones")
    lines.append("")

    for milestone in gdd.progression.milestones:
        lines.append(f"- **{milestone.name}**: {milestone.description}")

    lines.append("")
    lines.append("## Narrative")
    lines.append("")
    lines.append(f"**Setting:** {gdd.narrative.setting}")
    lines.append("")
    lines.append("### Story Premise")
    lines.append("")
    lines.append(gdd.narrative.story_premise)
    lines.append("")
    lines.append(f"**Themes:** {', '.join(gdd.narrative.themes)}")
    lines.append("")

    if gdd.narrative.characters:
        lines.append("### Characters")
        lines.append("")
        for char in gdd.narrative.characters:
            lines.append(f"- **{char.name}** ({char.role}): {char.description}")
        lines.append("")

    lines.append("## Technical Specifications")
    lines.append("")
    lines.append(f"**Recommended Engine:** {gdd.technical.recommended_engine.value}")
    lines.append(f"**Art Style:** {gdd.technical.art_style.value}")
    lines.append("")
    lines.append("### Key Technologies")
    lines.append("")

    for tech in gdd.technical.key_technologies:
        lines.append(f"- {tech}")

    if gdd.technical.performance_targets:
        lines.append("")
        lines.append("### Performance Targets")
        lines.append("")
        for target in gdd.technical.performance_targets:
            lines.append(
                f"- **{target.platform.value}:** {target.target_fps} FPS, "
                f"{target.min_resolution}, {target.max_ram_mb}MB RAM"
            )
        lines.append("")
    else:
        lines.append("")

    if gdd.risks:
        lines.append("## Risks")
        lines.append("")
        for risk in gdd.risks:
            lines.append(
                f"- **[{risk.severity.value.upper()}] {risk.category}**: "
                f"{risk.description}"
            )
            lines.append(f"  - *Mitigation*: {risk.mitigation}")
        lines.append("")

    if gdd.map_hints:
        lines.append("## Map Generation Hints")
        lines.append("")
        lines.append(f"**Size:** {gdd.map_hints.map_size}")
        lines.append(f"**Style:** {gdd.map_hints.generation_style}")
        lines.append(f"**Connectivity:** {gdd.map_hints.connectivity}")
        lines.append("")
        lines.append("```")
        lines.append(f"/Map {gdd.map_hints.to_map_command_args()}")
        lines.append("```")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*Generated: {gdd.generated_at}*")
    lines.append(f"*Schema Version: {gdd.schema_version}*")

    return "\n".join(lines)


def gdd_to_game_generator_prompt(gdd: GameDesignDocument) -> str:
    """
    Convert a GDD to a game-generator compatible prompt.

    This format is designed to work with the game-generator project
    which expects a text prompt describing the game to create.
    The prompt is optimized for generating playable HTML5 browser games.
    """
    lines = []

    # Title and core concept
    lines.append(f"Create a browser game called '{gdd.meta.title}'.")
    lines.append("")

    # Genre description
    genres = ", ".join(g.value for g in gdd.meta.genres)
    lines.append(f"Genre: {genres}")
    lines.append("")

    # Elevator pitch if available
    if gdd.meta.elevator_pitch:
        lines.append(f"Concept: {gdd.meta.elevator_pitch}")
        lines.append("")

    # Core gameplay loop
    lines.append("GAMEPLAY:")
    lines.append(f"- Primary actions: {', '.join(gdd.core_loop.primary_actions)}")
    lines.append(f"- Challenge: {gdd.core_loop.challenge_description}")
    lines.append(f"- Rewards: {gdd.core_loop.reward_description}")
    lines.append(f"- Session length: ~{gdd.core_loop.session_length_minutes} minutes")
    lines.append("")

    # Key game mechanics from systems
    lines.append("KEY MECHANICS:")
    for system in gdd.systems[:5]:  # Top 5 systems by priority
        mechanics_str = ", ".join(system.mechanics[:5])  # Top 5 mechanics per system
        lines.append(f"- {system.name}: {mechanics_str}")
    lines.append("")

    # Win/lose conditions from progression
    lines.append("PROGRESSION:")
    lines.append(f"- Type: {gdd.progression.type.value}")
    lines.append(
        f"- Difficulty curve: {gdd.progression.difficulty_curve_description[:200]}"
    )
    if gdd.progression.milestones:
        milestone_names = [m.name for m in gdd.progression.milestones[:3]]
        lines.append(f"- Key milestones: {', '.join(milestone_names)}")
    lines.append("")

    # Visual style
    lines.append("VISUAL STYLE:")
    lines.append(f"- Art style: {gdd.technical.art_style.value}")
    if gdd.narrative.setting:
        lines.append(f"- Setting: {gdd.narrative.setting[:150]}")
    lines.append("")

    # Unique selling point
    lines.append("UNIQUE FEATURES:")
    lines.append(f"- {gdd.meta.unique_selling_point}")
    lines.append("")

    # Technical requirements for browser game
    lines.append("REQUIREMENTS:")
    lines.append("- Must be a single HTML file with embedded CSS and JavaScript")
    lines.append("- Include score tracking and game over state")
    lines.append("- Add restart functionality")
    lines.append("- Show clear controls/instructions to the player")

    return "\n".join(lines)


def gdd_to_map_hints_prompt(gdd: GameDesignDocument) -> str:
    """
    Extract and format map generation hints from a GDD for /Map command usage.

    This format is designed to work with the /Map command (TileWorldCreator4)
    which generates procedural maps based on the game design specifications.

    The output can be directly passed to /Map command or used as reference
    for level design.

    Args:
        gdd: GameDesignDocument to extract map hints from

    Returns:
        Formatted string with map generation hints for /Map command
    """
    lines = []

    # Header
    lines.append(f"# Map Generation Hints for: {gdd.meta.title}")
    lines.append("")

    # Check if map_hints exists
    if gdd.map_hints is None:
        lines.append("## No Map Hints Available")
        lines.append("")
        lines.append("This GDD does not include explicit map generation hints.")
        lines.append("Generate hints based on game context:")
        lines.append("")

        # Derive hints from narrative setting
        lines.append("### Derived from Game Design")
        lines.append("")
        lines.append(f"**Setting:** {gdd.narrative.setting}")
        lines.append(f"**Themes:** {', '.join(gdd.narrative.themes)}")
        lines.append(f"**Art Style:** {gdd.technical.art_style.value}")
        lines.append("")

        # Suggest /Map command based on setting
        lines.append("### Suggested /Map Command")
        lines.append("")
        lines.append("```")
        lines.append(
            f"/Map Create a map for a {gdd.meta.genres[0].value} game set in {gdd.narrative.setting[:100]}"
        )
        lines.append("```")

        return "\n".join(lines)

    # Full map hints available
    hints = gdd.map_hints

    # Quick reference for /Map command
    lines.append("## /Map Command Reference")
    lines.append("")
    lines.append("```")
    lines.append(f"/Map {hints.to_map_command_args()}")
    lines.append("```")
    lines.append("")

    # Biomes section
    lines.append("## Biomes")
    lines.append("")
    for biome in hints.biomes:
        lines.append(f"- {biome.value}")
    lines.append("")

    # Map configuration
    lines.append("## Map Configuration")
    lines.append("")
    lines.append(f"- **Size:** {hints.map_size}")
    lines.append(f"- **Connectivity:** {hints.connectivity}")
    lines.append(f"- **Verticality:** {hints.verticality}")
    lines.append(f"- **Generation Style:** {hints.generation_style}")
    lines.append("")

    # Obstacles
    if hints.obstacles:
        lines.append("## Obstacles")
        lines.append("")
        for obstacle in hints.obstacles:
            lines.append(f"### {obstacle.type.capitalize()}")
            lines.append(f"- **Density:** {obstacle.density}")
            lines.append(f"- **Purpose:** {obstacle.purpose}")
            lines.append("")

    # Special features
    if hints.special_features:
        lines.append("## Special Features")
        lines.append("")
        for feature in hints.special_features:
            lines.append(f"### {feature.name}")
            lines.append(f"- **Frequency:** {feature.frequency}")
            lines.append(f"- **Description:** {feature.description}")
            if feature.requirements:
                lines.append(f"- **Requirements:** {', '.join(feature.requirements)}")
            lines.append("")

    # Enemy spawn zones
    if hints.enemy_spawn_zones:
        lines.append("## Enemy Spawn Zones")
        lines.append("")
        for zone in hints.enemy_spawn_zones:
            lines.append(f"- {zone}")
        lines.append("")

    # Visual themes
    if hints.visual_themes:
        lines.append("## Visual Themes")
        lines.append("")
        for theme in hints.visual_themes:
            lines.append(f"- {theme}")
        lines.append("")

    # TWC4 Configuration Hints
    lines.append("## TileWorldCreator4 Configuration Hints")
    lines.append("")
    lines.append("Based on the map hints, suggested TWC4 settings:")
    lines.append("")

    # Suggest generator based on generation_style
    generator_map = {
        "procedural_rooms": "BSPDungeon",
        "cellular_automata": "CellularAutomata",
        "bsp_dungeon": "BSPDungeon",
        "wave_function_collapse": "RandomNoise",
        "perlin_noise": "RandomNoise",
    }
    suggested_generator = generator_map.get(hints.generation_style, "CellularAutomata")
    lines.append(f"- **Suggested Generator:** {suggested_generator}")

    # Size mapping
    size_map = {
        "tiny": "32x32",
        "small": "48x48",
        "medium": "64x64",
        "large": "96x96",
        "huge": "128x128",
    }
    suggested_size = size_map.get(hints.map_size, "64x64")
    lines.append(f"- **Suggested Grid Size:** {suggested_size}")
    lines.append("")

    # JSON export for programmatic use
    lines.append("## JSON Export")
    lines.append("")
    lines.append("```json")
    lines.append(hints.model_dump_json(indent=2))
    lines.append("```")

    return "\n".join(lines)


def display_result_summary(result: RefinementResult) -> None:
    """Display a rich summary of the generation result."""
    # Create status panel
    status_color = "green" if result.success else "yellow"
    status_text = "APPROVED" if result.success else "BEST EFFORT"

    console.print()
    console.print(
        Panel(
            f"[bold {status_color}]{status_text}[/bold {status_color}]\n\n"
            f"[bold]Game:[/bold] {result.final_gdd.meta.title}\n"
            f"[bold]Termination:[/bold] {result.termination_reason.value}\n"
            f"[bold]Iterations:[/bold] {result.total_iterations}\n"
            f"[bold]Duration:[/bold] {result.total_duration_ms / 1000:.2f}s",
            title="Generation Result",
            border_style=status_color,
        )
    )

    # Create scores table if we have feedback
    if result.final_feedback:
        feedback = result.final_feedback
        table = Table(
            title="Quality Scores", show_header=True, header_style="bold cyan"
        )
        table.add_column("Dimension", style="dim")
        table.add_column("Score", justify="center")
        table.add_column("Weight", justify="center")

        scores = [
            ("Feasibility", feedback.feasibility_score, "25%"),
            ("Coherence", feedback.coherence_score, "20%"),
            ("Fun Factor", feedback.fun_factor_score, "25%"),
            ("Completeness", feedback.completeness_score, "15%"),
            ("Originality", feedback.originality_score, "15%"),
        ]

        for name, score, weight in scores:
            score_color = "green" if score >= 7 else "yellow" if score >= 5 else "red"
            table.add_row(name, f"[{score_color}]{score}/10[/{score_color}]", weight)

        table.add_row(
            "[bold]Overall[/bold]",
            f"[bold]{feedback.overall_score:.1f}/10[/bold]",
            "100%",
        )
        console.print(table)


def display_gdd_preview(gdd: GameDesignDocument) -> None:
    """Display a preview of the generated GDD."""
    # Build elevator pitch line if available
    elevator_line = ""
    if gdd.meta.elevator_pitch:
        elevator_line = f"[italic]{gdd.meta.elevator_pitch}[/italic]\n\n"

    console.print()
    console.print(
        Panel(
            f"[bold]{gdd.meta.title}[/bold]\n\n"
            f"{elevator_line}"
            f"[bold]Genres:[/bold] {', '.join(g.value for g in gdd.meta.genres)}\n"
            f"[bold]USP:[/bold] {gdd.meta.unique_selling_point[:100]}...\n\n"
            f"[bold]Core Loop:[/bold]\n"
            f"  Actions: {', '.join(gdd.core_loop.primary_actions)}\n"
            f"  Challenge: {gdd.core_loop.challenge_description[:50]}...\n"
            f"  Reward: {gdd.core_loop.reward_description[:50]}...\n\n"
            f"[bold]Systems:[/bold] {len(gdd.systems)} defined\n"
            f"[bold]Milestones:[/bold] {len(gdd.progression.milestones)} defined\n"
            f"[bold]Characters:[/bold] {len(gdd.narrative.characters)} defined",
            title="GDD Preview",
            border_style="blue",
        )
    )


# =============================================================================
# CLI COMMANDS
# =============================================================================


@app.command()
def plan(
    prompt: str = typer.Argument(
        ...,
        help="Game concept to design (e.g., 'zombie survival roguelike')",
    ),
    provider: Provider = typer.Option(
        Provider.MOCK,
        "--provider",
        "-p",
        help="LLM provider: mock, anthropic, openai",
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (stdout if not specified)",
    ),
    format: OutputFormat = typer.Option(
        OutputFormat.JSON,
        "--format",
        "-f",
        help="Output format: json or markdown",
    ),
    mock: bool = typer.Option(
        False,
        "--mock",
        "-m",
        help="Use mock LLM for testing (shortcut for --provider mock)",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress progress output (only show final result)",
    ),
    max_iterations: int = typer.Option(
        3,
        "--max-iterations",
        "-i",
        help="Maximum refinement iterations",
        min=1,
        max=10,
    ),
    preview: bool = typer.Option(
        True,
        "--preview/--no-preview",
        help="Show GDD preview after generation",
    ),
) -> None:
    """
    Generate a Game Design Document from a game concept.

    Uses the Dual-Agent Actor-Critic architecture to generate and refine
    comprehensive game design documents.

    Examples:
        python -m game_planner.main plan "zombie roguelike" --mock
        python -m game_planner.main plan "cozy farming sim" --provider anthropic
        python -m game_planner.main plan "space explorer" -o gdd.md -f markdown
    """
    # Handle mock shortcut
    provider_type = provider.value
    if mock:
        provider_type = "mock"

    if not quiet:
        console.print()
        console.print(
            Panel(
                f"[bold]Concept:[/bold] {prompt}\n"
                f"[bold]Provider:[/bold] {provider_type}\n"
                f"[bold]Format:[/bold] {format.value}\n"
                f"[bold]Output:[/bold] {output or 'stdout'}",
                title="Game Planner - Dual-Agent GDD Generator",
                border_style="cyan",
            )
        )

    try:
        # Run async generation
        result = asyncio.run(
            _generate_with_progress(
                prompt=prompt,
                provider_type=provider_type,
                max_iterations=max_iterations,
                quiet=quiet,
            )
        )

        # Display result summary
        if not quiet:
            display_result_summary(result)

        # Show preview if enabled
        if preview and not quiet:
            display_gdd_preview(result.final_gdd)

        # Format output
        if format == OutputFormat.MARKDOWN:
            content = gdd_to_markdown(result.final_gdd)
        elif format == OutputFormat.GAME_GENERATOR:
            content = gdd_to_game_generator_prompt(result.final_gdd)
        elif format == OutputFormat.MAP_HINTS:
            content = gdd_to_map_hints_prompt(result.final_gdd)
        elif format == OutputFormat.HTML:
            content = gdd_to_html(result.final_gdd)
        else:
            content = result.final_gdd.to_json(indent=2)

        # Output handling
        if output:
            output_path = Path(output)
            output_path.write_text(content, encoding="utf-8")
            if not quiet:
                console.print()
                console.print(
                    f"[green]OK[/green] GDD saved to [bold]{output_path}[/bold]"
                )
        elif format == OutputFormat.HTML:
            # For HTML format without explicit output, save to auto-named file and open in browser
            import re
            import webbrowser

            # Create slug from title
            title_slug = re.sub(r"[^\w\s-]", "", result.final_gdd.meta.title.lower())
            title_slug = re.sub(r"[\s_]+", "-", title_slug).strip("-")
            output_path = Path(f"gdd-{title_slug}.html")
            output_path.write_text(content, encoding="utf-8")

            if not quiet:
                console.print()
                console.print(
                    f"[green]OK[/green] GDD saved to [bold]{output_path}[/bold]"
                )
                console.print("[cyan]Opening in browser...[/cyan]")

            # Open in default browser
            webbrowser.open(output_path.absolute().as_uri())
        else:
            # Output to stdout
            if not quiet:
                console.print()
                console.print(
                    Panel(
                        content[:3000] + ("..." if len(content) > 3000 else ""),
                        title=f"GDD Output ({format.value.upper()})",
                        border_style="green",
                    )
                )
            else:
                # In quiet mode, just print raw output
                print(content)

        # Show map integration hints if available
        if not quiet and result.final_gdd.map_hints:
            console.print()
            console.print(
                Panel(
                    f"[dim]Use with /Map command:[/dim]\n"
                    f"/Map {result.final_gdd.map_hints.to_map_command_args()}",
                    title="Map Generation Integration",
                    border_style="magenta",
                )
            )

    except KeyboardInterrupt:
        console.print("\n[yellow]Generation cancelled by user[/yellow]")
        raise typer.Exit(code=130)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


async def _generate_with_progress(
    prompt: str,
    provider_type: str,
    max_iterations: int,
    quiet: bool,
) -> RefinementResult:
    """Run GDD generation with rich progress display."""
    if quiet:
        # No progress display in quiet mode
        llm_provider = create_provider(provider_type)
        config = OrchestratorConfig(max_iterations=max_iterations)
        orchestrator = GamePlanningOrchestrator(llm_provider, config)
        return await orchestrator.execute(prompt)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        # Initialize task
        task = progress.add_task("[cyan]Initializing...", total=None)

        # Create provider and orchestrator
        progress.update(task, description="[cyan]Creating LLM provider...")
        llm_provider = create_provider(provider_type)

        config = OrchestratorConfig(max_iterations=max_iterations)
        orchestrator = GamePlanningOrchestrator(llm_provider, config)

        # Run generation with progress updates
        progress.update(task, description="[cyan]Generating initial GDD (Actor)...")

        # Execute the orchestration
        result = await orchestrator.execute(prompt)

        # Update based on result
        if result.success:
            progress.update(
                task,
                description=f"[green]Approved after {result.total_iterations} iteration(s)",
            )
        else:
            progress.update(
                task,
                description=f"[yellow]Best effort after {result.total_iterations} iteration(s)",
            )

    return result


@app.command()
def version() -> None:
    """Show version information."""
    console.print(
        Panel(
            "[bold]Game Planner[/bold]\n"
            "AI-Powered Game Design Document Generator\n\n"
            "Version: 0.1.0\n"
            "Architecture: Dual-Agent Actor-Critic\n"
            f"GDD Schema: {GameDesignDocument.model_fields['schema_version'].default}",
            title="Version Info",
            border_style="blue",
        )
    )


@app.command()
def validate(
    file: str = typer.Argument(..., help="Path to GDD JSON file to validate"),
) -> None:
    """Validate an existing GDD JSON file against the schema."""
    path = Path(file)

    if not path.exists():
        console.print(f"[red]Error:[/red] File not found: {path}")
        raise typer.Exit(code=1)

    try:
        content = path.read_text(encoding="utf-8")
        data = json.loads(content)
        gdd = GameDesignDocument.model_validate(data)

        console.print(
            Panel(
                f"[green]Valid GDD[/green]\n\n"
                f"[bold]Title:[/bold] {gdd.meta.title}\n"
                f"[bold]Genres:[/bold] {', '.join(g.value for g in gdd.meta.genres)}\n"
                f"[bold]Systems:[/bold] {len(gdd.systems)}\n"
                f"[bold]Milestones:[/bold] {len(gdd.progression.milestones)}",
                title="Validation Result",
                border_style="green",
            )
        )

    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Validation failed:[/red] {e}")
        raise typer.Exit(code=1)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
