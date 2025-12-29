# Game Planner

**Automatic Game Design Document Generator using Dual-Agent Actor-Critic Architecture**

Transform simple game concepts into comprehensive, production-ready Game Design Documents (GDD) using a sophisticated dual-agent system based on [arXiv:2512.10501](https://arxiv.org/abs/2512.10501).

## Features

- **Dual-Agent Architecture**: Game Designer (Actor) generates creative GDDs, Game Reviewer (Critic) validates quality
- **Structured Output**: Produces JSON-schema validated Game Design Documents
- **OpenCode Integration**: `/GamePlan` slash command for seamless workflow
- **Python CLI**: Standalone command-line interface for automation
- **Multi-format Output**: JSON and Markdown export formats
- **Downstream Integration**: Compatible with game-generator and /Map command

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Game Planning Orchestrator                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User Prompt ─────► Context Manager                         │
│  "zombie roguelike"      │                                  │
│                          ▼                                  │
│              ┌───────────────────────┐                      │
│              │   Dual-Agent Loop     │                      │
│              │                       │                      │
│              │  ┌─────────────────┐  │                      │
│              │  │ Game Designer   │  │ ◄── Temperature: 0.6 │
│              │  │ (Actor)         │  │     Creative focus   │
│              │  └────────┬────────┘  │                      │
│              │           │ GDD       │                      │
│              │           ▼           │                      │
│              │  ┌─────────────────┐  │                      │
│              │  │ Game Reviewer   │  │ ◄── Temperature: 0.2 │
│              │  │ (Critic)        │  │     Rigorous review  │
│              │  └────────┬────────┘  │                      │
│              │           │ Feedback  │                      │
│              │           ▼           │                      │
│              │  [Approve/Revise]     │ Max 3 iterations     │
│              └───────────────────────┘                      │
│                          │                                  │
│                          ▼                                  │
│              Structured GDD Output (JSON/MD)                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Option 1: OpenCode Global Installation (Recommended)

Install the `/GamePlan` command globally for use from any directory:

**Windows:**
```batch
cd game-planner
install.bat
```

**Unix/Linux/Mac:**
```bash
cd game-planner
chmod +x install.sh
./install.sh
```

**Manual Installation:**
```bash
# Copy agent configurations
cp .opencode/agent/game-designer.yaml ~/.opencode/agent/
cp .opencode/agent/game-reviewer.yaml ~/.opencode/agent/

# Copy slash command
cp .opencode/command/GamePlan.md ~/.opencode/command/
```

After installation, you can use `/GamePlan` from any OpenCode session:
```
opencode -c
/GamePlan zombie survival roguelike
```

### Option 2: Python CLI Installation

```bash
cd game-planner

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Unix/Mac
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run CLI
python main.py plan "zombie survival roguelike" --mock
```

## Usage

### OpenCode `/GamePlan` Command

Start OpenCode and use the slash command:

```bash
# Start OpenCode
opencode -c

# Generate GDD from text concept
/GamePlan zombie survival roguelike

# Generate GDD from detailed concept
/GamePlan A cozy farming simulation game where players inherit a magical farm. 
They must grow enchanted crops, befriend magical creatures, and restore an ancient forest.

# Generate GDD from concept art (attach image)
/GamePlan [attached concept art image]
```

### Python CLI

```bash
# Generate GDD with mock LLM (for testing)
python main.py plan "space exploration roguelike" --mock

# Generate GDD with real API
python main.py plan "medieval city builder" --output gdd.json

# Generate Markdown output
python main.py plan "puzzle platformer" --format markdown --output gdd.md

# Validate existing GDD file
python main.py validate gdd.json

# Show version
python main.py version

# Quiet mode (raw output, good for piping)
python main.py plan "racing game" --mock --quiet
```

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--output`, `-o` | Output file path | `gdd.json` |
| `--format`, `-f` | Output format: `json` or `markdown` | `json` |
| `--mock` | Use mock LLM (no API key required) | `false` |
| `--quiet`, `-q` | Suppress progress output, raw JSON/MD only | `false` |
| `--no-preview` | Skip GDD preview panel | `false` |

## GDD Schema

The generated Game Design Document follows a comprehensive schema:

### Top-Level Structure

```json
{
  "schema_version": "1.0",
  "generated_at": "2025-12-29T12:00:00Z",
  "meta": { ... },
  "core_loop": { ... },
  "systems": [ ... ],
  "progression": { ... },
  "narrative": { ... },
  "technical": { ... },
  "map_hints": { ... },
  "risks": [ ... ],
  "additional_notes": "..."
}
```

### Key Sections

| Section | Description |
|---------|-------------|
| `meta` | Game identity: title, genres, platforms, audience, USP |
| `core_loop` | Gameplay loop: actions, challenges, rewards, session length |
| `systems` | Game systems: combat, inventory, crafting, etc. (min 3) |
| `progression` | Player advancement: milestones, unlocks, difficulty (min 5 milestones) |
| `narrative` | Story: setting, characters, themes, delivery methods |
| `technical` | Implementation: engine, art style, performance targets |
| `map_hints` | Level generation hints for /Map command integration |
| `risks` | Development risks and mitigations |

### Valid Enum Values

<details>
<summary>Click to expand enum values</summary>

**Genres:** action, rpg, puzzle, strategy, simulation, roguelike, platformer, shooter, adventure, horror, survival, racing, sports, fighting, stealth, sandbox, rhythm, visual_novel, card_game, tower_defense, idle, metroidvania

**Platforms:** pc, web, mobile_ios, mobile_android, console_playstation, console_xbox, console_nintendo, vr, ar

**Engines:** unity, unreal, godot, love2d, phaser, pygame, construct, gamemaker, custom

**Art Styles:** pixel_art, voxel, low_poly, realistic, stylized, cartoon, anime, minimalist, hand_drawn, abstract

**Progression Types:** linear, branching, open_world, roguelike_runs, level_based, skill_tree, mastery

**System Types:** combat, movement, inventory, crafting, economy, dialogue, quest, ai, physics, weather, day_night, stealth, building, farming, cooking, fishing, trading, skill, leveling, equipment, save_load, multiplayer, achievement, tutorial, ui, audio, custom

**Biomes:** forest, desert, snow, ocean, mountain, swamp, jungle, plains, volcanic, cave, urban, ruins, dungeon, space, underwater

</details>

## Critic Review Framework

The Game Reviewer agent evaluates GDDs across 5 dimensions:

| Dimension | Weight | Focus |
|-----------|--------|-------|
| **Feasibility** | 25% | Can it be built within reasonable resources? |
| **Coherence** | 20% | Do all systems work together logically? |
| **Fun Factor** | 25% | Is the core loop engaging and motivating? |
| **Completeness** | 15% | Are all required sections properly filled? |
| **Originality** | 15% | Does it have a unique selling point? |

Each dimension is scored 1-10, with weighted average for overall score.

## Downstream Integration

### game-generator Integration

Extract a simplified prompt for browser game generation:

```
--format game-generator
```

Output format:
```
Create a [GENRE] game called "[TITLE]".

Core Gameplay:
[Core loop description]

Key Mechanics:
[List of mechanics]

Win Condition: [Based on progression]
Lose Condition: [Based on challenges]

Art Style: [Technical art style]
```

### /Map Command Integration

The `map_hints` section generates compatible arguments for the `/Map` command:

```bash
/Map post-apocalyptic urban map with urban,ruins biomes, large size, procedural_rooms style
```

## Configuration

Edit `config.yaml` to customize behavior:

```yaml
orchestrator:
  max_iterations: 3       # Maximum revision cycles
  actor_temperature: 0.6  # Creativity level (0.0-1.0)
  critic_temperature: 0.2 # Review consistency (0.0-1.0)

llm:
  provider: "anthropic"   # anthropic, openai, mock
  model: "claude-sonnet-4-20250514"

output:
  default_format: "json"  # json, markdown
  include_map_hints: true
```

## File Structure

```
game-planner/
├── __init__.py           # Package initialization
├── models.py             # Pydantic GDD schema models
├── prompts.py            # Actor/Critic system prompts
├── orchestrator.py       # Dual-agent loop implementation
├── llm_provider.py       # LLM abstraction (Anthropic/OpenAI/Mock)
├── main.py               # CLI entry point (Typer)
├── config.yaml           # Configuration
├── requirements.txt      # Python dependencies
├── install.sh            # Unix/Mac installer
├── install.bat           # Windows installer
├── .opencode/
│   ├── agent/
│   │   ├── game-designer.yaml  # Actor agent config
│   │   └── game-reviewer.yaml  # Critic agent config
│   └── command/
│       └── GamePlan.md         # /GamePlan slash command
└── tests/
    ├── test_models.py
    ├── test_prompts.py
    ├── test_orchestrator.py
    ├── test_llm_provider.py
    └── test_cli.py
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_models.py -v

# Run linting
python -m ruff check .
```

## Requirements

- Python 3.10+
- OpenCode (for `/GamePlan` command)
- API Key (for non-mock usage):
  - `ANTHROPIC_API_KEY` for Anthropic/Claude
  - `OPENAI_API_KEY` for OpenAI

## Examples

### Example 1: Zombie Roguelike

```bash
python main.py plan "zombie survival roguelike with base building" --mock
```

Generates a complete GDD with:
- Survival mechanics and zombie AI systems
- Base building and resource management
- Roguelike progression with meta-upgrades
- Post-apocalyptic narrative and setting

### Example 2: Cozy Farming Game

```bash
/GamePlan cozy farming simulation with magical creatures and seasons
```

Generates a complete GDD with:
- Farming, creature care, and crafting systems
- Seasonal progression and relationship building
- Heartwarming narrative with village restoration
- Pixel art style with adaptive music

### Example 3: Competitive Multiplayer

```bash
python main.py plan "fast-paced competitive arena shooter" -f markdown -o arena_shooter.md
```

Generates Markdown documentation with:
- Twitch-action combat systems
- Matchmaking and ranking progression
- Esports-ready technical specifications
- Map design hints for procedural arenas

## Complete GDD Schema Reference

This section documents every field in the Game Design Document schema.

### GameMeta

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Game title (2-100 characters) |
| `genres` | Genre[] | Yes | List of game genres (at least 1) |
| `target_platforms` | Platform[] | Yes | Target platforms (at least 1) |
| `target_audience` | string | Yes | Target audience description (10-500 chars) |
| `audience_rating` | string | No | Age rating (everyone, teen, mature) |
| `unique_selling_point` | string | Yes | What makes this game unique (20-500 chars) |
| `estimated_dev_time_weeks` | int | Yes | Development time estimate (1-520 weeks) |
| `team_size_estimate` | int | No | Recommended team size (1-500) |
| `elevator_pitch` | string | No | One-sentence pitch (max 280 chars) |

### CoreLoop

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `primary_actions` | string[] | Yes | Main player actions (at least 2) |
| `challenge_description` | string | Yes | What challenges players face |
| `reward_description` | string | Yes | How players are rewarded |
| `loop_description` | string | Yes | Full gameplay loop description |
| `session_length_minutes` | int | Yes | Typical session length (1-480 mins) |
| `feedback_mechanisms` | string[] | No | How game provides feedback |
| `hook_elements` | string[] | No | What keeps players coming back |

### GameSystem

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | System name (2-100 chars) |
| `type` | SystemType | Yes | System category |
| `description` | string | Yes | System description (10-1000 chars) |
| `mechanics` | string[] | No | Specific mechanics in this system |
| `parameters` | SystemParameter[] | No | Configurable parameters |
| `dependencies` | string[] | No | Other systems this depends on |
| `priority` | int | No | Implementation priority (1-10) |

### Progression

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `progression_type` | ProgressionType | Yes | Type of progression system |
| `milestones` | Milestone[] | Yes | Progression milestones (at least 5) |
| `unlock_system` | UnlockSystem | No | How content is unlocked |
| `difficulty_curve` | DifficultyCurve | No | Difficulty scaling approach |
| `meta_progression` | string | No | Progression across runs/sessions |
| `estimated_completion_hours` | float | No | Time to complete (0.5-1000 hours) |

### Milestone

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Milestone name |
| `description` | string | Yes | What player achieves |
| `estimated_hours` | float | Yes | Hours to reach (0.1-100) |
| `rewards` | string[] | No | What player earns |

### Narrative

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `setting` | string | Yes | Game world setting (10-500 chars) |
| `story_premise` | string | Yes | Story setup (20-1000 chars) |
| `characters` | Character[] | No | Main characters |
| `story_structure` | string | No | How story unfolds |
| `themes` | string[] | Yes | Narrative themes (at least 1) |
| `delivery_methods` | string[] | No | How story is delivered |
| `world_building_notes` | string | No | Additional world details |

### Character

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Character name |
| `role` | string | Yes | Character's role |
| `description` | string | Yes | Character description |
| `motivation` | string | No | Character's goals |
| `relationships` | string[] | No | Relationships with others |

### TechnicalSpec

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `recommended_engine` | Engine | Yes | Suggested game engine |
| `art_style` | ArtStyle | Yes | Visual art style |
| `key_technologies` | string[] | No | Technical requirements |
| `performance_targets` | string[] | Yes | FPS, load time targets |
| `asset_requirements` | string[] | No | Required assets |
| `audio` | AudioSpec | Yes | Audio specifications |
| `multiplayer_requirements` | string | No | Multiplayer tech needs |

### AudioSpec

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `music_style` | string | Yes | Music genre/style |
| `sound_design_notes` | string | Yes | Sound design approach |
| `voice_acting` | bool | No | Whether voice acting needed |
| `adaptive_audio` | bool | No | Whether music adapts to gameplay |

### MapGenerationHints

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `primary_biomes` | Biome[] | Yes | Main biome types |
| `map_size` | string | Yes | small/medium/large/procedural |
| `connectivity` | string | Yes | low/medium/high/fully_connected |
| `generation_style` | string | Yes | procedural_rooms/bsp_dungeon/etc |
| `special_features` | string[] | No | Special map elements |
| `environmental_hazards` | string[] | No | Hazards in the environment |

### Risk

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `category` | string | Yes | Risk category |
| `description` | string | Yes | Risk description |
| `severity` | Severity | Yes | low/medium/high/critical |
| `mitigation` | string | Yes | How to mitigate |

### CriticFeedback (Review Output)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `decision` | Decision | Yes | APPROVE or REVISE |
| `feasibility_score` | int | Yes | 1-10 score |
| `coherence_score` | int | Yes | 1-10 score |
| `fun_factor_score` | int | Yes | 1-10 score |
| `completeness_score` | int | Yes | 1-10 score |
| `originality_score` | int | Yes | 1-10 score |
| `blocking_issues` | Issue[] | No | Critical issues to fix |
| `suggestions` | Issue[] | No | Nice-to-have improvements |
| `summary` | string | Yes | Review summary |

---

## API Reference

### Orchestrator Module

```python
from orchestrator import GamePlanningOrchestrator, generate_gdd, create_mock_orchestrator

# Quick generation with mock provider
result = await generate_gdd("zombie roguelike", mock=True)

# Custom orchestrator with configuration
orchestrator = create_mock_orchestrator(
    max_iterations=5,
    actor_temperature=0.7,
    critic_temperature=0.3
)
result = await orchestrator.execute("my game concept")
```

#### `generate_gdd(prompt, mock=False, config=None)`

Convenience function for one-liner GDD generation.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | str | Required | Game concept description |
| `mock` | bool | False | Use mock provider |
| `config` | OrchestratorConfig | None | Custom configuration |

Returns: `RefinementResult` with `success`, `final_gdd`, `iterations`, `history`

#### `create_mock_orchestrator(**kwargs)`

Create orchestrator with mock LLM for testing.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_iterations` | int | 3 | Maximum revision cycles |
| `actor_temperature` | float | 0.6 | Actor creativity |
| `critic_temperature` | float | 0.2 | Critic consistency |
| `actor_responses` | list | None | Custom actor responses |
| `critic_responses` | list | None | Custom critic responses |

### LLM Provider Module

```python
from llm_provider import create_provider, MockLLMProvider

# Create provider
provider = create_provider("mock")  # or "anthropic", "openai"

# Generate response
response = await provider.generate(
    system_prompt="You are a game designer",
    user_prompt="Create a puzzle game",
    temperature=0.6
)
```

#### `create_provider(provider_type, **kwargs)`

Factory function to create LLM providers.

| Provider Type | Required Environment | Description |
|---------------|---------------------|-------------|
| `mock` | None | Testing provider with configurable responses |
| `anthropic` | `ANTHROPIC_API_KEY` | Claude API provider |
| `openai` | `OPENAI_API_KEY` | OpenAI API provider |

### Models Module

```python
from models import GameDesignDocument, CriticFeedback, Genre, Platform

# Create GDD from JSON
gdd = GameDesignDocument.from_llm_response(json_string)

# Validate GDD
gdd = GameDesignDocument.model_validate(dict_data)

# Export to JSON
json_str = gdd.model_dump_json(indent=2)
```

---

## Output Formats

### JSON Format (Default)

Standard JSON output with full GDD structure:

```bash
python main.py plan "puzzle game" --format json --output gdd.json
```

### Markdown Format

Human-readable documentation format:

```bash
python main.py plan "puzzle game" --format markdown --output gdd.md
```

Output structure:
```markdown
# [Game Title]

## Overview
- **Genres**: [list]
- **Platforms**: [list]
- **USP**: [unique selling point]

## Core Gameplay Loop
[description]

## Game Systems
### [System Name]
[description]

## Progression
[milestones and unlocks]

## Narrative
[story and characters]

## Technical Specifications
[engine, art style, performance]
```

### game-generator Format

Simplified prompt for browser game generation:

```bash
python main.py plan "puzzle game" --format game-generator
```

### map-hints Format

Level generation hints for /Map command:

```bash
python main.py plan "dungeon crawler" --format map-hints
```

Output includes:
- Biome recommendations
- Map size and connectivity
- Generation style hints
- TileWorldCreator4 configuration
- JSON export for programmatic use

---

## Troubleshooting

### Common Issues

#### "No module named 'anthropic'"

Install required dependencies:
```bash
pip install -r requirements.txt
```

#### "ANTHROPIC_API_KEY not set"

Set your API key:
```bash
# Unix/Mac
export ANTHROPIC_API_KEY="your-key-here"

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your-key-here"

# Windows (CMD)
set ANTHROPIC_API_KEY=your-key-here
```

#### "Critic JSON parse error"

This is normal behavior when using `--mock`. The mock provider returns placeholder responses that don't match the CriticFeedback schema. The orchestrator automatically falls back to approval. For real API usage, this error indicates the LLM response didn't match expected format - the orchestrator will retry up to 3 times.

#### "Max iterations reached without approval"

The Critic agent found issues but couldn't approve after maximum iterations. Check the output for the best GDD produced. Consider:
- Simplifying your game concept
- Increasing `max_iterations` in config
- Reviewing the blocking issues listed

#### Tests fail with "asyncio_mode not found"

Ensure pytest.ini has:
```ini
[pytest]
asyncio_mode = auto
```

And install pytest-asyncio:
```bash
pip install pytest-asyncio
```

### Debug Mode

Enable verbose logging:
```bash
# Set environment variable
export GAME_PLANNER_DEBUG=1

# Or use --no-preview to see raw output
python main.py plan "game concept" --no-preview
```

---

## Integration Guides

### Integrating with game-generator (Next.js)

1. Generate GDD with game-generator format:
```bash
python main.py plan "browser puzzle game" --format game-generator -o prompt.txt
```

2. Use the generated prompt in game-generator:
```javascript
const prompt = fs.readFileSync('prompt.txt', 'utf-8');
// Pass to game-generator API
```

### Integrating with /Map Command

1. Generate GDD with map hints:
```bash
python main.py plan "dungeon crawler" --format map-hints -o map_hints.txt
```

2. Extract /Map command:
```bash
# The output includes a ready-to-use /Map command
/Map dungeon,cave biomes; large size; bsp_dungeon style
```

### Integrating with Unity (via GenesisArchitect)

1. Generate technical GDD:
```bash
python main.py plan "3D adventure game" -o unity_gdd.json
```

2. The `technical` section includes Unity-specific recommendations:
   - Recommended Unity version
   - Required packages
   - Performance targets
   - Asset pipeline suggestions

### Programmatic Integration

```python
import asyncio
from orchestrator import generate_gdd

async def create_game_design():
    result = await generate_gdd(
        "A cozy farming simulation with magical elements",
        mock=False  # Use real API
    )
    
    if result.success:
        gdd = result.final_gdd
        # Access structured data
        print(f"Title: {gdd.meta.title}")
        print(f"Systems: {[s.name for s in gdd.systems]}")
        
        # Export to JSON
        with open("output.json", "w") as f:
            f.write(gdd.model_dump_json(indent=2))
    else:
        print(f"Failed after {result.iterations} iterations")
        print(f"Issues: {result.history[-1].feedback.blocking_issues}")

asyncio.run(create_game_design())
```

---

## Advanced Configuration

### Custom Temperature Settings

Temperature affects output creativity vs consistency:

| Setting | Actor (Designer) | Critic (Reviewer) | Use Case |
|---------|-----------------|-------------------|----------|
| Conservative | 0.4 | 0.1 | Established genres |
| Balanced | 0.6 | 0.2 | General use (default) |
| Creative | 0.8 | 0.3 | Experimental concepts |
| Wild | 1.0 | 0.4 | Brainstorming only |

Modify in `config.yaml`:
```yaml
orchestrator:
  actor_temperature: 0.8  # More creative
  critic_temperature: 0.3  # More lenient
```

### Custom Iteration Limits

```yaml
orchestrator:
  max_iterations: 5  # More revision cycles
```

### Provider Configuration

```yaml
llm:
  provider: "anthropic"
  model: "claude-sonnet-4-20250514"
  # Alternative models:
  # model: "claude-3-opus-20240229"  # More capable, slower
  # model: "gpt-4o"  # OpenAI (requires provider: "openai")
```

---

## Test Coverage

Current test coverage: **94%** (226 tests)

| Module | Coverage | Tests |
|--------|----------|-------|
| models.py | 98% | 55 |
| prompts.py | 100% | 48 |
| orchestrator.py | 82% | 28 |
| llm_provider.py | 77% | 43 |
| main.py | 86% | 52 |

Run tests with coverage:
```bash
python -m pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html  # View detailed report
```

---

## Changelog

### v1.0.0 (2025-12-29)

**Features:**
- Initial release with Dual-Agent Actor-Critic architecture
- Comprehensive GDD schema with 15+ model classes
- 5-Dimension Critic Review Framework (Feasibility, Coherence, Fun, Completeness, Originality)
- Python CLI with Typer and Rich console output
- OpenCode `/GamePlan` slash command integration
- Multiple output formats: JSON, Markdown, game-generator, map-hints
- Mock provider for testing without API keys
- Error handling with fallback GDD generation
- Exponential backoff for network errors

**Integrations:**
- game-generator compatible output format
- /Map command hints for TileWorldCreator4
- Unity/GenesisArchitect technical recommendations

**Documentation:**
- Complete GDD schema reference
- API documentation
- Integration guides
- Troubleshooting section

---

## License

MIT License - See [LICENSE](LICENSE) for details.

## References

- **Dual-Agent Architecture**: Based on [arXiv:2512.10501](https://arxiv.org/abs/2512.10501) - "Zero-shot 3D Map Generation with Dual-Agent LLMs"
- **GDD Best Practices**: Industry-standard Game Design Document patterns
- **OpenCode**: [OpenCode CLI](https://opencode.ai) for AI-assisted development
- **Pydantic**: [Pydantic v2](https://docs.pydantic.dev/) for data validation
- **Typer**: [Typer CLI](https://typer.tiangolo.com/) for command-line interface

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`python -m pytest tests/ -v`)
5. Run linting (`python -m ruff check .`)
6. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions/changes
- `chore:` Maintenance tasks
- `refactor:` Code refactoring

---

**Made with the Dual-Agent Actor-Critic architecture for reliable, creative game design automation.**

*Maintained by the Game Planner team*
