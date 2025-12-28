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

## License

MIT License - See [LICENSE](LICENSE) for details.

## References

- **Dual-Agent Architecture**: Based on [arXiv:2512.10501](https://arxiv.org/abs/2512.10501) - "Zero-shot 3D Map Generation with Dual-Agent LLMs"
- **GDD Best Practices**: Industry-standard Game Design Document patterns
- **OpenCode**: [OpenCode CLI](https://opencode.ai) for AI-assisted development

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with tests

---

**Made with the Dual-Agent Actor-Critic architecture for reliable, creative game design automation.**
