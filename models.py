"""
models.py - Comprehensive Pydantic Models for Game Design Document (GDD) Schema
Based on Dual-Agent Actor-Critic Architecture (arXiv:2512.10501)

This module defines the complete GDD schema including:
- GameMeta: Basic game metadata and identity
- CoreLoop: The primary gameplay loop
- GameSystem: Individual game systems and mechanics
- Progression: Player progression and difficulty systems
- Narrative: Story, characters, and themes
- TechnicalSpec: Technical requirements and specifications
- MapGenerationHints: Integration hints for /Map command
- GameDesignDocument: Root model combining all sections
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator


# =============================================================================
# ENUMS - Type-safe string enumerations for game design concepts
# =============================================================================


class Genre(str, Enum):
    """Primary game genres for classification."""

    ACTION = "action"
    RPG = "rpg"
    PUZZLE = "puzzle"
    STRATEGY = "strategy"
    SIMULATION = "simulation"
    ROGUELIKE = "roguelike"
    PLATFORMER = "platformer"
    SHOOTER = "shooter"
    ADVENTURE = "adventure"
    HORROR = "horror"
    SURVIVAL = "survival"
    RACING = "racing"
    SPORTS = "sports"
    FIGHTING = "fighting"
    STEALTH = "stealth"
    SANDBOX = "sandbox"
    RHYTHM = "rhythm"
    VISUAL_NOVEL = "visual_novel"
    CARD_GAME = "card_game"
    TOWER_DEFENSE = "tower_defense"
    IDLE = "idle"
    METROIDVANIA = "metroidvania"


class Platform(str, Enum):
    """Target gaming platforms."""

    PC = "pc"
    WEB = "web"
    MOBILE_IOS = "mobile_ios"
    MOBILE_ANDROID = "mobile_android"
    CONSOLE_PLAYSTATION = "console_playstation"
    CONSOLE_XBOX = "console_xbox"
    CONSOLE_NINTENDO = "console_nintendo"
    VR = "vr"
    AR = "ar"


class AudienceRating(str, Enum):
    """Target audience age ratings."""

    EVERYONE = "everyone"
    TEEN = "teen"
    MATURE = "mature"
    ADULTS_ONLY = "adults_only"


class GameEngine(str, Enum):
    """Recommended game engines."""

    UNITY = "unity"
    UNREAL = "unreal"
    GODOT = "godot"
    LOVE2D = "love2d"
    PHASER = "phaser"
    PYGAME = "pygame"
    CONSTRUCT = "construct"
    GAMEMAKER = "gamemaker"
    CUSTOM = "custom"


class ArtStyle(str, Enum):
    """Visual art style categories."""

    PIXEL_ART = "pixel_art"
    VOXEL = "voxel"
    LOW_POLY = "low_poly"
    REALISTIC = "realistic"
    STYLIZED = "stylized"
    CARTOON = "cartoon"
    ANIME = "anime"
    MINIMALIST = "minimalist"
    HAND_DRAWN = "hand_drawn"
    ABSTRACT = "abstract"


class ProgressionType(str, Enum):
    """Types of player progression systems."""

    LINEAR = "linear"
    BRANCHING = "branching"
    OPEN_WORLD = "open_world"
    ROGUELIKE_RUNS = "roguelike_runs"
    LEVEL_BASED = "level_based"
    SKILL_TREE = "skill_tree"
    MASTERY = "mastery"


class NarrativeDelivery(str, Enum):
    """Methods of narrative delivery."""

    CUTSCENES = "cutscenes"
    DIALOGUE = "dialogue"
    ENVIRONMENTAL = "environmental"
    COLLECTIBLES = "collectibles"
    EMERGENT = "emergent"
    PROCEDURAL = "procedural"
    NONE = "none"


class SystemType(str, Enum):
    """Categories of game systems."""

    COMBAT = "combat"
    MOVEMENT = "movement"
    INVENTORY = "inventory"
    CRAFTING = "crafting"
    ECONOMY = "economy"
    DIALOGUE = "dialogue"
    QUEST = "quest"
    AI = "ai"
    PHYSICS = "physics"
    WEATHER = "weather"
    DAY_NIGHT = "day_night"
    STEALTH = "stealth"
    BUILDING = "building"
    FARMING = "farming"
    COOKING = "cooking"
    FISHING = "fishing"
    TRADING = "trading"
    SKILL = "skill"
    LEVELING = "leveling"
    EQUIPMENT = "equipment"
    SAVE_LOAD = "save_load"
    MULTIPLAYER = "multiplayer"
    ACHIEVEMENT = "achievement"
    TUTORIAL = "tutorial"
    UI = "ui"
    AUDIO = "audio"
    CUSTOM = "custom"


class BiomeType(str, Enum):
    """Environment biome types for map generation."""

    FOREST = "forest"
    DESERT = "desert"
    SNOW = "snow"
    OCEAN = "ocean"
    MOUNTAIN = "mountain"
    SWAMP = "swamp"
    JUNGLE = "jungle"
    PLAINS = "plains"
    VOLCANIC = "volcanic"
    CAVE = "cave"
    URBAN = "urban"
    RUINS = "ruins"
    DUNGEON = "dungeon"
    SPACE = "space"
    UNDERWATER = "underwater"


class Severity(str, Enum):
    """
    Issue severity levels for Critic feedback.
    From Section 3.1 (Table 1) of arXiv:2512.10501.
    """

    CRITICAL = "critical"
    MAJOR = "major"


class Decision(str, Enum):
    """
    Critic decision options.
    From Section 3.2 of arXiv:2512.10501.
    """

    APPROVE = "approve"
    REVISE = "revise"


class TerminationReason(str, Enum):
    """Reasons for terminating the refinement loop."""

    APPROVED = "approved"
    MAX_ITERATIONS = "max_iterations"
    ERROR = "error"
    TIMEOUT = "timeout"


# =============================================================================
# GAME META - Basic game information and identity
# =============================================================================


class GameMeta(BaseModel):
    """
    Core metadata about the game including title, genre, and target audience.

    Example:
        GameMeta(
            title="Zombie Survival Roguelike",
            genres=[Genre.ROGUELIKE, Genre.SURVIVAL, Genre.ACTION],
            target_platforms=[Platform.PC, Platform.CONSOLE_PLAYSTATION],
            target_audience="Fans of challenging survival games",
            audience_rating=AudienceRating.MATURE,
            unique_selling_point="Procedural base building with permadeath consequences",
            estimated_dev_time_weeks=52,
            team_size_estimate=5
        )
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Game title - should be memorable and descriptive",
        examples=["Zombie Survival Roguelike", "Space Explorer 3000"],
    )
    genres: List[Genre] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Primary game genres (1-5), ordered by importance",
    )
    target_platforms: List[Platform] = Field(
        ...,
        min_length=1,
        description="Target platforms for release",
    )
    target_audience: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Description of the target player demographic",
        examples=["Fans of challenging survival games aged 18-35"],
    )
    audience_rating: AudienceRating = Field(
        default=AudienceRating.TEEN,
        description="Age rating classification for content",
    )
    unique_selling_point: str = Field(
        ...,
        min_length=20,
        max_length=500,
        description="What makes this game unique and worth playing (USP)",
        examples=["Procedural base building with permadeath consequences"],
    )
    estimated_dev_time_weeks: int = Field(
        ...,
        ge=1,
        le=520,
        description="Estimated development time in weeks (1-520, up to 10 years)",
    )
    team_size_estimate: int = Field(
        default=1,
        ge=1,
        le=500,
        description="Estimated team size needed for development",
    )
    elevator_pitch: Optional[str] = Field(
        default=None,
        max_length=300,
        description="One-paragraph pitch for the game (optional)",
    )


# =============================================================================
# CORE LOOP - The primary gameplay loop
# =============================================================================


class FeedbackMechanism(BaseModel):
    """A single feedback mechanism in the core loop."""

    trigger: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="What triggers this feedback",
        examples=["Enemy defeated", "Level completed", "Item collected"],
    )
    response: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="The feedback response to the player",
        examples=["XP gain animation", "Victory fanfare", "Screen shake"],
    )
    purpose: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="Why this feedback is important for player engagement",
    )


class CoreLoop(BaseModel):
    """
    The core gameplay loop - the fundamental cycle players repeat.

    A strong core loop has:
    1. Clear primary actions
    2. Meaningful challenges
    3. Satisfying rewards
    4. Compelling feedback

    Example:
        CoreLoop(
            primary_actions=["Explore", "Fight", "Loot", "Upgrade"],
            challenge_description="Survive increasingly difficult zombie waves...",
            reward_description="Gain resources to upgrade base and unlock new weapons",
            loop_description="Explore -> Encounter Zombies -> Fight/Flee -> Loot -> Return to Base -> Upgrade -> Repeat",
            session_length_minutes=30,
            feedback_mechanisms=[...]
        )
    """

    primary_actions: List[str] = Field(
        ...,
        min_length=2,
        max_length=10,
        description="Core actions players perform repeatedly (2-10)",
        examples=[["Explore", "Fight", "Loot", "Upgrade"]],
    )
    challenge_description: str = Field(
        ...,
        min_length=20,
        max_length=1000,
        description="What challenges players face in the core loop",
    )
    reward_description: str = Field(
        ...,
        min_length=20,
        max_length=1000,
        description="What rewards players receive for overcoming challenges",
    )
    loop_description: str = Field(
        ...,
        min_length=20,
        max_length=1000,
        description="Step-by-step description of the full gameplay loop",
    )
    session_length_minutes: int = Field(
        ...,
        ge=1,
        le=480,
        description="Typical play session length in minutes (1-480)",
    )
    feedback_mechanisms: List[FeedbackMechanism] = Field(
        default_factory=list,
        max_length=20,
        description="Feedback mechanisms that reinforce the loop",
    )
    hook_elements: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Elements that keep players coming back",
        examples=[["Daily rewards", "Leaderboards", "Story progression"]],
    )


# =============================================================================
# GAME SYSTEMS - Individual mechanics and systems
# =============================================================================


class SystemParameter(BaseModel):
    """A configurable parameter within a game system."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Parameter name",
        examples=["damage_multiplier", "spawn_rate", "cooldown_seconds"],
    )
    type: str = Field(
        ...,
        description="Data type of the parameter",
        examples=["float", "int", "bool", "string", "enum"],
    )
    default_value: str = Field(
        ...,
        description="Default value as string",
        examples=["1.0", "5", "true", "normal"],
    )
    description: str = Field(
        ...,
        min_length=5,
        max_length=300,
        description="What this parameter controls",
    )
    range: Optional[str] = Field(
        default=None,
        description="Valid range for numeric values",
        examples=["0.1-10.0", "1-100"],
    )


class GameSystem(BaseModel):
    """
    A single game system or mechanic.

    Example:
        GameSystem(
            name="Combat System",
            type=SystemType.COMBAT,
            description="Real-time melee and ranged combat with dodge mechanics",
            mechanics=["Light attack", "Heavy attack", "Block", "Dodge roll", "Ranged aim"],
            parameters=[...],
            dependencies=["Movement System", "Inventory System"]
        )
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="System name",
        examples=["Combat System", "Inventory System", "Weather System"],
    )
    type: SystemType = Field(
        ...,
        description="Category of the game system",
    )
    description: str = Field(
        ...,
        min_length=20,
        max_length=1000,
        description="Detailed description of what the system does",
    )
    mechanics: List[str] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Specific mechanics within this system",
    )
    parameters: List[SystemParameter] = Field(
        default_factory=list,
        max_length=30,
        description="Configurable parameters for balancing",
    )
    dependencies: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Other systems this one depends on",
    )
    priority: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Implementation priority (1=highest, 10=lowest)",
    )


# =============================================================================
# PROGRESSION - Player advancement and difficulty
# =============================================================================


class Milestone(BaseModel):
    """A progression milestone or achievement point."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Milestone name",
        examples=["First Boss Defeated", "Base Level 5", "100 Zombies Killed"],
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="What this milestone represents",
    )
    unlock_condition: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="How to unlock this milestone",
    )
    rewards: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Rewards granted upon reaching milestone",
    )
    estimated_hours: Optional[float] = Field(
        default=None,
        ge=0.1,
        le=1000,
        description="Estimated hours to reach this milestone",
    )


class UnlockItem(BaseModel):
    """An item or feature that can be unlocked."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the unlockable",
    )
    type: str = Field(
        ...,
        description="Type of unlock (weapon, ability, area, character, etc.)",
    )
    unlock_method: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="How to unlock this item",
    )
    impact: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="How this unlock affects gameplay",
    )


class DifficultyLevel(BaseModel):
    """A difficulty setting configuration."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Difficulty name",
        examples=["Easy", "Normal", "Hard", "Nightmare"],
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="What makes this difficulty different",
    )
    modifiers: Dict[str, str] = Field(
        default_factory=dict,
        description="Parameter modifiers for this difficulty",
        examples=[{"enemy_damage": "+50%", "player_health": "-25%"}],
    )


class Progression(BaseModel):
    """
    Player progression system including unlocks and difficulty scaling.

    Example:
        Progression(
            type=ProgressionType.ROGUELIKE_RUNS,
            milestones=[...],
            unlocks=[...],
            difficulty_levels=[...],
            meta_progression_description="Permanent upgrades persist between runs"
        )
    """

    type: ProgressionType = Field(
        ...,
        description="Overall progression structure",
    )
    milestones: List[Milestone] = Field(
        ...,
        min_length=5,
        description="Key progression milestones (minimum 5)",
    )
    unlocks: List[UnlockItem] = Field(
        default_factory=list,
        description="Items/features that can be unlocked",
    )
    difficulty_levels: List[DifficultyLevel] = Field(
        default_factory=list,
        description="Available difficulty settings",
    )
    difficulty_curve_description: str = Field(
        ...,
        min_length=20,
        max_length=1000,
        description="How difficulty scales throughout the game",
    )
    meta_progression_description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Description of any meta-progression systems",
    )
    estimated_completion_hours: Optional[float] = Field(
        default=None,
        ge=0.5,
        le=1000,
        description="Estimated hours to complete main content",
    )

    @model_validator(mode="after")
    def validate_milestones(self) -> "Progression":
        """Ensure minimum 5 milestones as per config requirements."""
        if len(self.milestones) < 5:
            raise ValueError(
                f"Progression requires at least 5 milestones, got {len(self.milestones)}"
            )
        return self


# =============================================================================
# NARRATIVE - Story, characters, and themes
# =============================================================================


class Character(BaseModel):
    """A game character (player, NPC, or enemy type)."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Character name",
    )
    role: str = Field(
        ...,
        description="Role in the story",
        examples=["Protagonist", "Antagonist", "Mentor", "Companion", "Enemy"],
    )
    description: str = Field(
        ...,
        min_length=20,
        max_length=1000,
        description="Character description and personality",
    )
    motivation: Optional[str] = Field(
        default=None,
        max_length=500,
        description="What drives this character",
    )
    abilities: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Special abilities or traits",
    )


class Narrative(BaseModel):
    """
    Game narrative including setting, story, and characters.

    Example:
        Narrative(
            setting="Post-apocalyptic urban wasteland, 2045",
            story_premise="Survivors must rebuild society while fighting zombie hordes",
            themes=["Survival", "Hope", "Sacrifice"],
            characters=[...],
            narrative_delivery=[NarrativeDelivery.ENVIRONMENTAL, NarrativeDelivery.DIALOGUE],
            story_structure="Three-act structure with branching endings"
        )
    """

    setting: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="World setting and time period",
        examples=["Post-apocalyptic urban wasteland, 2045"],
    )
    story_premise: str = Field(
        ...,
        min_length=20,
        max_length=2000,
        description="Main story premise and setup",
    )
    themes: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Central themes explored in the game",
        examples=[["Survival", "Hope", "Sacrifice", "Community"]],
    )
    characters: List[Character] = Field(
        default_factory=list,
        max_length=50,
        description="Key characters in the game",
    )
    narrative_delivery: List[NarrativeDelivery] = Field(
        ...,
        min_length=1,
        description="Methods used to deliver the narrative",
    )
    story_structure: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Overall structure of the story (linear, branching, emergent, etc.)",
    )
    key_story_beats: List[str] = Field(
        default_factory=list,
        max_length=20,
        description="Major plot points or story events",
    )
    world_lore: Optional[str] = Field(
        default=None,
        max_length=3000,
        description="Background lore and world history",
    )


# =============================================================================
# TECHNICAL SPECS - Technical requirements and specifications
# =============================================================================


class PerformanceTarget(BaseModel):
    """Performance targets for a specific platform."""

    platform: Platform = Field(
        ...,
        description="Target platform",
    )
    target_fps: int = Field(
        default=60,
        ge=30,
        le=240,
        description="Target frames per second",
    )
    min_resolution: str = Field(
        default="1920x1080",
        description="Minimum supported resolution",
    )
    max_ram_mb: int = Field(
        default=4096,
        ge=256,
        le=65536,
        description="Maximum RAM usage in MB",
    )


class AudioRequirements(BaseModel):
    """Audio system requirements."""

    music_style: str = Field(
        ...,
        min_length=5,
        max_length=300,
        description="Musical style and mood",
        examples=["Atmospheric electronic with tense orchestral elements"],
    )
    sound_categories: List[str] = Field(
        ...,
        min_length=1,
        description="Categories of sound effects needed",
        examples=[["Ambient", "Combat", "UI", "Environmental", "Voice"]],
    )
    voice_acting: bool = Field(
        default=False,
        description="Whether voice acting is required",
    )
    adaptive_music: bool = Field(
        default=False,
        description="Whether music adapts to gameplay",
    )


class TechnicalSpec(BaseModel):
    """
    Technical specifications and requirements for the game.

    Example:
        TechnicalSpec(
            recommended_engine=GameEngine.UNITY,
            art_style=ArtStyle.PIXEL_ART,
            key_technologies=["Procedural generation", "Pathfinding AI", "Save system"],
            performance_targets=[...],
            audio=AudioRequirements(...),
            networking_required=False
        )
    """

    recommended_engine: GameEngine = Field(
        ...,
        description="Recommended game engine for development",
    )
    art_style: ArtStyle = Field(
        ...,
        description="Primary visual art style",
    )
    key_technologies: List[str] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Key technologies and systems needed",
        examples=[["Procedural generation", "Pathfinding AI", "Save system"]],
    )
    performance_targets: List[PerformanceTarget] = Field(
        default_factory=list,
        max_length=10,
        description="Performance targets per platform",
    )
    audio: AudioRequirements = Field(
        ...,
        description="Audio system requirements",
    )
    asset_requirements: List[str] = Field(
        default_factory=list,
        max_length=30,
        description="Types of assets needed (art, audio, etc.)",
    )
    networking_required: bool = Field(
        default=False,
        description="Whether networking/multiplayer is needed",
    )
    accessibility_features: List[str] = Field(
        default_factory=list,
        max_length=20,
        description="Planned accessibility features",
    )
    localization_languages: List[str] = Field(
        default_factory=list,
        max_length=30,
        description="Languages for localization",
    )


# =============================================================================
# MAP GENERATION HINTS - Integration with /Map command
# =============================================================================


class ObstacleHint(BaseModel):
    """Hint for obstacle placement in map generation."""

    type: str = Field(
        ...,
        description="Type of obstacle",
        examples=["wall", "water", "pit", "barrier", "destructible"],
    )
    density: str = Field(
        default="medium",
        description="Placement density (sparse, medium, dense)",
    )
    purpose: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="Gameplay purpose of this obstacle",
    )


class SpecialFeature(BaseModel):
    """Special feature or point of interest for maps."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Feature name",
        examples=["Safe Room", "Boss Arena", "Treasure Vault", "Shop"],
    )
    frequency: str = Field(
        default="rare",
        description="How often this appears (common, uncommon, rare, unique)",
    )
    requirements: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Conditions for spawning this feature",
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="What this feature contains or does",
    )


class MapGenerationHints(BaseModel):
    """
    Hints for procedural map generation, designed for /Map command integration.

    These hints can be passed to the TileWorldCreator system for level generation.

    Example:
        MapGenerationHints(
            biomes=[BiomeType.URBAN, BiomeType.RUINS],
            map_size="large",
            obstacles=[...],
            special_features=[...],
            connectivity="high",
            generation_style="procedural_rooms"
        )
    """

    biomes: List[BiomeType] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Biome types to include in maps",
    )
    map_size: str = Field(
        default="medium",
        description="Default map size (tiny, small, medium, large, huge)",
    )
    obstacles: List[ObstacleHint] = Field(
        default_factory=list,
        max_length=20,
        description="Obstacle types and placement hints",
    )
    special_features: List[SpecialFeature] = Field(
        default_factory=list,
        max_length=20,
        description="Special features and points of interest",
    )
    connectivity: str = Field(
        default="medium",
        description="How connected areas should be (low, medium, high)",
    )
    verticality: str = Field(
        default="low",
        description="Amount of vertical gameplay (none, low, medium, high)",
    )
    generation_style: str = Field(
        default="procedural_rooms",
        description="Map generation algorithm style",
        examples=[
            "procedural_rooms",
            "cellular_automata",
            "bsp_dungeon",
            "wave_function_collapse",
            "perlin_noise",
        ],
    )
    enemy_spawn_zones: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Types of enemy spawn zone configurations",
    )
    visual_themes: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Visual theme hints for the map generator",
    )

    def to_map_command_args(self) -> str:
        """Convert hints to /Map command arguments."""
        args = []
        if self.biomes:
            args.append(f"biomes: {', '.join(b.value for b in self.biomes)}")
        args.append(f"size: {self.map_size}")
        args.append(f"connectivity: {self.connectivity}")
        args.append(f"style: {self.generation_style}")
        return "; ".join(args)


# =============================================================================
# DEVELOPMENT TASKS - Dynamic checklist based on game systems
# =============================================================================


class TaskRequirement(BaseModel):
    """A single requirement/sub-task within a development task."""

    description: str = Field(
        ...,
        min_length=5,
        max_length=300,
        description="What needs to be implemented",
        examples=[
            "Implement player movement with WASD keys",
            "Add jump mechanics with variable height",
        ],
    )
    estimated_hours: Optional[float] = Field(
        default=None,
        ge=0.5,
        le=100,
        description="Estimated hours to complete this requirement",
    )


class DevelopmentTask(BaseModel):
    """
    A development task for implementing a game feature.
    Generated dynamically based on the game's systems.
    """

    id: str = Field(
        ...,
        description="Unique task identifier (e.g., 'p1-task1', 'p2-task3')",
        examples=["p1-task1", "p2-task3", "p3-task2"],
    )
    phase: int = Field(
        ...,
        ge=1,
        le=10,
        description="Development phase number (1-10)",
    )
    phase_name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Name of the development phase",
        examples=[
            "Core Mechanics",
            "System Implementation",
            "Content Creation",
            "Polish",
        ],
    )
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Task name",
        examples=[
            "Implement Combat System",
            "Create Player Controller",
            "Design UI Layout",
        ],
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Detailed description of what needs to be implemented",
    )
    related_system: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Which game system this task relates to (from systems list)",
    )
    requirements: List[TaskRequirement] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Specific implementation requirements (sub-tasks)",
    )
    priority: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Implementation priority (1=highest, 10=lowest)",
    )
    estimated_hours: Optional[float] = Field(
        default=None,
        ge=1,
        le=500,
        description="Total estimated hours for this task",
    )
    dependencies: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Task IDs this task depends on",
        examples=[["p1-task1", "p1-task2"]],
    )


# =============================================================================
# RISK ASSESSMENT - Potential implementation risks
# =============================================================================


class Risk(BaseModel):
    """A potential risk or concern for the game design."""

    category: str = Field(
        ...,
        description="Risk category",
        examples=["Technical", "Design", "Scope", "Market", "Team"],
    )
    description: str = Field(
        ...,
        min_length=20,
        max_length=500,
        description="Description of the risk",
    )
    severity: Severity = Field(
        ...,
        description="How severe this risk is",
    )
    mitigation: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Suggested mitigation strategy",
    )
    likelihood: str = Field(
        default="medium",
        description="Likelihood of this risk (low, medium, high)",
    )


# =============================================================================
# GAME DESIGN DOCUMENT - Root model combining all sections
# =============================================================================


class GameDesignDocument(BaseModel):
    """
    Complete Game Design Document (GDD) combining all sections.

    This is the root model that the Actor agent generates and the Critic agent reviews.
    Schema version follows semantic versioning.

    Example:
        gdd = GameDesignDocument(
            schema_version="1.0",
            meta=GameMeta(...),
            core_loop=CoreLoop(...),
            systems=[GameSystem(...), ...],
            progression=Progression(...),
            narrative=Narrative(...),
            technical=TechnicalSpec(...),
            map_hints=MapGenerationHints(...),
            risks=[Risk(...), ...]
        )
    """

    schema_version: str = Field(
        default="1.0",
        description="GDD schema version for compatibility",
    )
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="UTC timestamp when this GDD was generated",
    )
    meta: GameMeta = Field(
        ...,
        description="Core game metadata and identity",
    )
    core_loop: CoreLoop = Field(
        ...,
        description="Primary gameplay loop definition",
    )
    systems: List[GameSystem] = Field(
        ...,
        min_length=3,
        description="Game systems and mechanics (minimum 3)",
    )
    progression: Progression = Field(
        ...,
        description="Player progression and difficulty systems",
    )
    narrative: Narrative = Field(
        ...,
        description="Story, characters, and themes",
    )
    technical: TechnicalSpec = Field(
        ...,
        description="Technical specifications and requirements",
    )
    map_hints: Optional[MapGenerationHints] = Field(
        default=None,
        description="Hints for /Map command integration (optional)",
    )
    risks: List[Risk] = Field(
        default_factory=list,
        max_length=20,
        description="Identified risks and mitigations",
    )
    development_tasks: List[DevelopmentTask] = Field(
        default_factory=list,
        max_length=50,
        description="Development tasks generated based on game systems (for checklist)",
    )
    additional_notes: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Additional notes or considerations",
    )

    @model_validator(mode="after")
    def validate_systems_count(self) -> "GameDesignDocument":
        """Ensure minimum 3 systems as per config requirements."""
        if len(self.systems) < 3:
            raise ValueError(
                f"GDD requires at least 3 game systems, got {len(self.systems)}"
            )
        return self

    @model_validator(mode="after")
    def validate_usp_present(self) -> "GameDesignDocument":
        """Ensure unique selling point is meaningful."""
        if len(self.meta.unique_selling_point) < 20:
            raise ValueError(
                "Unique selling point must be at least 20 characters to be meaningful"
            )
        return self

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json(indent=indent)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()

    @classmethod
    def from_json(cls, json_str: str) -> "GameDesignDocument":
        """Parse from JSON string."""
        return cls.model_validate_json(json_str)

    @classmethod
    def from_llm_response(cls, response: str) -> "GameDesignDocument":
        """
        Parse LLM response into validated GameDesignDocument.

        Handles:
        - Raw JSON
        - JSON wrapped in ```json ... ```
        - JSON wrapped in ``` ... ```
        """
        cleaned = response.strip()

        # Handle ```json ... ``` wrapping
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        cleaned = cleaned.strip()

        # Parse JSON
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON in LLM response: {e}\nResponse: {cleaned[:500]}..."
            )

        # Validate and return
        return cls.model_validate(data)

    def get_summary(self) -> str:
        """Generate a human-readable summary of the GDD."""
        lines = [
            "=" * 60,
            f"GAME DESIGN DOCUMENT: {self.meta.title}",
            "=" * 60,
            f"Genres: {', '.join(g.value for g in self.meta.genres)}",
            f"Platforms: {', '.join(p.value for p in self.meta.target_platforms)}",
            f"USP: {self.meta.unique_selling_point}",
            "",
            "CORE LOOP:",
            f"  Actions: {', '.join(self.core_loop.primary_actions)}",
            f"  Session Length: {self.core_loop.session_length_minutes} minutes",
            "",
            f"SYSTEMS ({len(self.systems)}):",
        ]

        for system in self.systems[:5]:  # Show first 5
            lines.append(f"  - {system.name} ({system.type.value})")

        if len(self.systems) > 5:
            lines.append(f"  ... and {len(self.systems) - 5} more")

        lines.extend(
            [
                "",
                f"PROGRESSION: {self.progression.type.value}",
                f"  Milestones: {len(self.progression.milestones)}",
                "",
                f"NARRATIVE: {self.narrative.setting[:50]}...",
                f"  Themes: {', '.join(self.narrative.themes)}",
                "",
                "TECHNICAL:",
                f"  Engine: {self.technical.recommended_engine.value}",
                f"  Art Style: {self.technical.art_style.value}",
                "",
                f"RISKS: {len(self.risks)} identified",
                "",
                f"Generated: {self.generated_at}",
                f"Schema Version: {self.schema_version}",
            ]
        )

        return "\n".join(lines)


# =============================================================================
# CRITIC OUTPUT MODELS - For Dual-Agent feedback
# =============================================================================


class BlockingIssue(BaseModel):
    """
    A specific issue identified in the GDD that needs fixing.
    Mirrors the pattern from dual_agent_pcg for consistency.
    """

    section: str = Field(
        ...,
        description="GDD section where the issue was found",
        examples=["meta", "core_loop", "systems", "progression", "narrative"],
    )
    issue: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Clear, specific description of what is wrong",
    )
    severity: Severity = Field(
        ...,
        description="How severe is this issue (critical or major)",
    )
    suggestion: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Specific, actionable fix for the issue",
    )

    def to_feedback_string(self) -> str:
        """Format issue for human-readable feedback."""
        severity_marker = (
            "[CRITICAL]" if self.severity == Severity.CRITICAL else "[MAJOR]"
        )
        return (
            f"{severity_marker} {self.section}:\n"
            f"   Issue: {self.issue}\n"
            f"   Fix: {self.suggestion}"
        )


class CriticFeedback(BaseModel):
    """
    Complete output from the Critic Agent reviewing a GDD.
    Uses the 5-dimension review framework from the todo specification.
    """

    decision: Decision = Field(
        ...,
        description="Whether the GDD is approved or needs revision",
    )
    blocking_issues: List[BlockingIssue] = Field(
        default_factory=list,
        description="List of issues that must be fixed",
    )
    # 5-Dimension scores (1-10 scale)
    feasibility_score: int = Field(
        ...,
        ge=1,
        le=10,
        description="Feasibility score (1-10): Can this be built with reasonable resources?",
    )
    coherence_score: int = Field(
        ...,
        ge=1,
        le=10,
        description="Coherence score (1-10): Do all systems work together logically?",
    )
    fun_factor_score: int = Field(
        ...,
        ge=1,
        le=10,
        description="Fun factor score (1-10): Is the core loop engaging?",
    )
    completeness_score: int = Field(
        ...,
        ge=1,
        le=10,
        description="Completeness score (1-10): Are all GDD sections properly filled?",
    )
    originality_score: int = Field(
        ...,
        ge=1,
        le=10,
        description="Originality score (1-10): Does the game have a unique selling point?",
    )
    review_notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Additional notes from the review",
    )

    @model_validator(mode="after")
    def validate_decision_consistency(self) -> "CriticFeedback":
        """Ensure decision matches blocking_issues state."""
        has_critical = any(
            i.severity == Severity.CRITICAL for i in self.blocking_issues
        )

        if has_critical and self.decision == Decision.APPROVE:
            raise ValueError(
                "Decision cannot be 'approve' when critical blocking_issues exist."
            )
        if not self.blocking_issues and self.decision == Decision.REVISE:
            raise ValueError(
                "Decision cannot be 'revise' when no blocking_issues exist."
            )
        return self

    @property
    def overall_score(self) -> float:
        """Calculate weighted overall score."""
        return (
            self.feasibility_score * 0.25
            + self.coherence_score * 0.20
            + self.fun_factor_score * 0.25
            + self.completeness_score * 0.15
            + self.originality_score * 0.15
        )

    @property
    def is_approved(self) -> bool:
        """Quick check if GDD was approved."""
        return self.decision == Decision.APPROVE

    def to_actor_feedback(self) -> str:
        """Format feedback for injection into Actor's revision context."""
        lines = [
            f"## CRITIC DECISION: {self.decision.value.upper()}",
            "",
            f"### SCORES (Overall: {self.overall_score:.1f}/10)",
            f"- Feasibility: {self.feasibility_score}/10",
            f"- Coherence: {self.coherence_score}/10",
            f"- Fun Factor: {self.fun_factor_score}/10",
            f"- Completeness: {self.completeness_score}/10",
            f"- Originality: {self.originality_score}/10",
            "",
        ]

        if self.blocking_issues:
            lines.append("### BLOCKING ISSUES (Must Fix)")
            lines.append("")
            for issue in self.blocking_issues:
                lines.append(issue.to_feedback_string())
                lines.append("")

        if self.review_notes:
            lines.append("### REVIEWER NOTES")
            lines.append(self.review_notes)
            lines.append("")

        return "\n".join(lines)

    @classmethod
    def from_llm_response(cls, response: str) -> "CriticFeedback":
        """Parse LLM response into validated CriticFeedback."""
        cleaned = response.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON in Critic response: {e}\nResponse: {cleaned[:500]}..."
            )

        return cls.model_validate(data)


# =============================================================================
# REFINEMENT RESULT - Output from the orchestrator
# =============================================================================


class IterationRecord(BaseModel):
    """Record of a single iteration in the refinement loop."""

    iteration_number: int = Field(..., ge=0)
    gdd: GameDesignDocument
    feedback: Optional[CriticFeedback] = None
    actor_duration_ms: float = Field(..., ge=0)
    critic_duration_ms: Optional[float] = Field(default=None, ge=0)
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class RefinementResult(BaseModel):
    """
    Complete result of the iterative GDD refinement process.
    This is the final output from the GamePlanningOrchestrator.
    """

    final_gdd: GameDesignDocument = Field(
        ...,
        description="The final approved or best-effort GDD",
    )
    termination_reason: TerminationReason = Field(
        ...,
        description="Why the refinement loop terminated",
    )
    total_iterations: int = Field(
        ...,
        ge=1,
        description="Total number of iterations performed",
    )
    iteration_history: List[IterationRecord] = Field(
        default_factory=list,
        description="Complete history of all iterations",
    )
    total_duration_ms: float = Field(
        ...,
        ge=0,
        description="Total time taken in milliseconds",
    )
    user_prompt: str = Field(
        ...,
        description="Original user request",
    )
    success: bool = Field(
        ...,
        description="Whether the result was approved by critic",
    )

    @property
    def final_feedback(self) -> Optional[CriticFeedback]:
        """Get the final critic feedback (if any)."""
        if self.iteration_history:
            return self.iteration_history[-1].feedback
        return None

    def to_summary(self) -> str:
        """Generate human-readable summary."""
        status = "[OK] SUCCESS" if self.success else "[!] BEST EFFORT"
        return (
            f"{status}\n"
            f"Game: {self.final_gdd.meta.title}\n"
            f"Termination: {self.termination_reason.value}\n"
            f"Iterations: {self.total_iterations}\n"
            f"Duration: {self.total_duration_ms:.2f}ms"
        )
