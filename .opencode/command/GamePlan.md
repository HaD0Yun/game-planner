---
description: "GDD Generator using Dual-Agent Actor-Critic architecture"
argument-hint: "game concept description or image"
---

# Dual-Agent Game Design Document Generator

You are the **Orchestrator** for generating comprehensive Game Design Documents (GDD) via natural language prompts or concept art images.

## Your Role

You MUST spawn **separate agents** using the Task tool to implement a true dual-agent loop.
- **DO NOT** roleplay as both Actor and Critic yourself
- **DO** use the Task tool to spawn agents with the agent configurations in this project

## User Request

**Game Concept**: $ARGUMENTS

---

## STEP 0: INPUT TYPE DETECTION (MANDATORY FIRST STEP)

Before spawning Actor, you MUST determine the input type:

### Check for Image Input
Look for image indicators in the user's message:
- File paths ending in `.png`, `.jpg`, `.jpeg`, `.webp`
- Phrases like "this image", "attached image", "concept art", "screenshot"
- Direct image attachments in the conversation

### Input Type A: TEXT ONLY
If no image detected -> Go to **Step 1A: Text-based Actor**

### Input Type B: CONCEPT ART IMAGE
If image is detected -> Go to **Step 1B: Image Analysis Pipeline**

---

## STEP 1A: Text-based Actor (Default)

```
Task(
  subagent_type="game-designer",
  description="Game Designer Agent - Generate GDD",
  prompt="Generate a comprehensive Game Design Document (GDD) for this concept:

USER CONCEPT: [USER_REQUEST]

IMPORTANT:
1. Output ONLY valid JSON matching the GDD schema
2. Include ALL required sections: meta, core_loop, systems, progression, narrative, technical
3. Create at least 3 game systems and 5 progression milestones
4. Ensure a unique, compelling USP (Unique Selling Point)
5. If this is a revision, address ALL blocking issues from previous feedback

GDD SCHEMA:
[Include the schema documentation from Step 4 below]

RESPOND WITH JSON ONLY - No explanations before or after."
)
```

---

## STEP 1B: Image Analysis Pipeline (Concept Art)

When user provides concept art or reference image:

### Step 1B-1: Analyze Image

```
Task(
  subagent_type="multimodal-looker",
  description="Analyze concept art for game design extraction",
  prompt="Analyze this game concept art and extract design parameters.

IMAGE: [user's image path or attachment]

Extract and describe:
1. **Visual Style**: Art direction, color palette, mood
2. **Setting**: Environment, era, world type
3. **Characters**: Visible characters, roles, design elements
4. **Gameplay Hints**: Implied mechanics, genre indicators
5. **Atmosphere**: Tone, themes, emotional hooks
6. **Technical Implications**: Art style complexity, asset requirements

Output a structured analysis:
{
  \"image_analysis\": {
    \"visual_style\": \"...\",
    \"implied_genres\": [\"...\"],
    \"setting_description\": \"...\",
    \"character_hints\": [\"...\"],
    \"gameplay_indicators\": [\"...\"],
    \"mood_and_themes\": [\"...\"],
    \"suggested_art_style\": \"pixel_art|stylized|realistic|etc\",
    \"technical_notes\": \"...\"
  },
  \"natural_language_concept\": \"A detailed text description synthesizing the visual into a game concept...\"
}"
)
```

### Step 1B-2: Pass Analysis to Actor

```
Task(
  subagent_type="game-designer",
  description="Game Designer Agent - Generate GDD from Image Analysis",
  prompt="Generate a comprehensive Game Design Document (GDD) based on this concept art analysis:

IMAGE ANALYSIS:
[Output from multimodal-looker]

Use the visual analysis to inform:
1. Art style and technical specifications
2. Setting and narrative elements
3. Suggested genre and mechanics
4. Mood-appropriate progression and themes

GDD SCHEMA:
[Include the schema documentation from Step 4 below]

RESPOND WITH JSON ONLY - No explanations before or after."
)
```

---

## STEP 2: Spawn Critic Agent

After receiving the Actor's GDD output:

```
Task(
  subagent_type="game-reviewer",
  description="Game Reviewer Agent - Validate GDD",
  prompt="Review this Game Design Document against professional standards.

GDD TO REVIEW:
[Actor's JSON output]

Apply the 5-DIMENSION REVIEW FRAMEWORK:

1. **Feasibility (25%)**: Can this be built within reasonable resources/time?
2. **Coherence (20%)**: Do all systems logically connect and support each other?
3. **Fun Factor (25%)**: Is the core loop engaging? Would players enjoy this?
4. **Completeness (15%)**: Are all required GDD sections properly filled?
5. **Originality (15%)**: Does the game have a unique, compelling selling point?

CRITICAL CONSTRAINT - Conservative Certainty Policy:
- Only flag blocking issues if you are CERTAIN of a problem
- When in doubt, APPROVE and note your concern in review_notes
- Every blocking issue MUST include an actionable suggestion

Output ONLY valid JSON:
{
  \"decision\": \"approve\" or \"revise\",
  \"blocking_issues\": [
    {
      \"section\": \"meta|core_loop|systems|progression|narrative|technical|map_hints|risks\",
      \"issue\": \"Clear, specific description of what is wrong\",
      \"severity\": \"critical|major\",
      \"suggestion\": \"Specific, actionable fix for the issue\"
    }
  ],
  \"feasibility_score\": 1-10,
  \"coherence_score\": 1-10,
  \"fun_factor_score\": 1-10,
  \"completeness_score\": 1-10,
  \"originality_score\": 1-10,
  \"review_notes\": \"Additional observations and suggestions\"
}"
)
```

---

## STEP 3: Loop Logic

After receiving Critic's feedback:

- **IF** `decision === "approve"` -> Go to **Step 5: Output Final Result**
- **IF** `decision === "revise"` AND iteration < 3 -> Go to **Step 3A: Revision Loop**
- **IF** iteration >= 3 -> Go to **Step 5: Output Best Effort Result**

### Step 3A: Revision Loop

When revision is needed, spawn Actor again with feedback context:

```
Task(
  subagent_type="game-designer",
  description="Game Designer Agent - Revise GDD (Iteration N)",
  prompt="REVISION REQUEST - Address ALL blocking issues.

ORIGINAL CONCEPT: [USER_REQUEST]

PREVIOUS GDD:
[Previous iteration's GDD JSON]

CRITIC FEEDBACK:
[Critic's feedback with blocking_issues]

INSTRUCTIONS:
1. Read ALL blocking issues carefully
2. Address EACH issue explicitly in your revision
3. Do NOT repeat the same mistakes
4. Maintain the strengths of the previous version while fixing weaknesses
5. Ensure the revised GDD still matches the original concept

Output ONLY valid JSON matching the GDD schema."
)
```

Then return to **Step 2** to validate the revision.

---

## STEP 4: GDD Schema Documentation

### Complete GameDesignDocument Schema

```json
{
  "schema_version": "1.0",
  "generated_at": "<ISO 8601 timestamp>",
  
  "meta": {
    "title": "<Game title - memorable and descriptive>",
    "genres": ["<genre1>", "<genre2>"],
    "target_platforms": ["<platform1>", "<platform2>"],
    "target_audience": "<Description of target demographic, 10-500 chars>",
    "audience_rating": "<everyone|teen|mature|adults_only>",
    "unique_selling_point": "<What makes this game unique, 20-500 chars>",
    "estimated_dev_time_weeks": "<1-520>",
    "team_size_estimate": "<1-500>",
    "elevator_pitch": "<Optional one-paragraph pitch>"
  },
  
  "core_loop": {
    "primary_actions": ["<action1>", "<action2>", "..."],
    "challenge_description": "<What challenges players face, 20-1000 chars>",
    "reward_description": "<What rewards players receive, 20-1000 chars>",
    "loop_description": "<Step-by-step gameplay loop, 20-1000 chars>",
    "session_length_minutes": "<1-480>",
    "feedback_mechanisms": [
      {
        "trigger": "<What triggers feedback>",
        "response": "<The feedback response>",
        "purpose": "<Why this feedback matters>"
      }
    ],
    "hook_elements": ["<element1>", "<element2>"]
  },
  
  "systems": [
    {
      "name": "<System name>",
      "type": "<combat|movement|inventory|crafting|economy|dialogue|quest|ai|physics|weather|day_night|stealth|building|farming|cooking|fishing|trading|skill|leveling|equipment|save_load|multiplayer|achievement|tutorial|ui|audio|custom>",
      "description": "<Detailed description, 20-1000 chars>",
      "mechanics": ["<mechanic1>", "<mechanic2>"],
      "parameters": [
        {
          "name": "<parameter_name>",
          "type": "<float|int|bool|string|enum>",
          "default_value": "<value>",
          "description": "<What it controls>",
          "range": "<optional valid range>"
        }
      ],
      "dependencies": ["<other_system_name>"],
      "priority": "<1-10, 1=highest>"
    }
  ],
  
  "progression": {
    "type": "<linear|branching|open_world|roguelike_runs|level_based|skill_tree|mastery>",
    "milestones": [
      {
        "name": "<Milestone name>",
        "description": "<What it represents>",
        "unlock_condition": "<How to unlock>",
        "rewards": ["<reward1>"],
        "estimated_hours": "<0.1-1000>"
      }
    ],
    "unlocks": [
      {
        "name": "<Unlockable name>",
        "type": "<weapon|ability|area|character|etc>",
        "unlock_method": "<How to unlock>",
        "impact": "<How it affects gameplay>"
      }
    ],
    "difficulty_levels": [
      {
        "name": "<Difficulty name>",
        "description": "<What makes it different>",
        "modifiers": {"<param>": "<modifier>"}
      }
    ],
    "difficulty_curve_description": "<How difficulty scales, 20-1000 chars>",
    "meta_progression_description": "<Optional: Persistent progression between runs>",
    "estimated_completion_hours": "<0.5-1000>"
  },
  
  "narrative": {
    "setting": "<World setting and time period, 10-1000 chars>",
    "story_premise": "<Main story premise, 20-2000 chars>",
    "themes": ["<theme1>", "<theme2>"],
    "characters": [
      {
        "name": "<Character name>",
        "role": "<Protagonist|Antagonist|Mentor|Companion|Enemy|etc>",
        "description": "<Character description, 20-1000 chars>",
        "motivation": "<What drives this character>",
        "abilities": ["<ability1>"]
      }
    ],
    "narrative_delivery": ["<cutscenes|dialogue|environmental|collectibles|emergent|procedural|none>"],
    "story_structure": "<Overall story structure, 10-1000 chars>",
    "key_story_beats": ["<beat1>", "<beat2>"],
    "world_lore": "<Optional background lore, max 3000 chars>"
  },
  
  "technical": {
    "recommended_engine": "<unity|unreal|godot|love2d|phaser|pygame|construct|gamemaker|custom>",
    "art_style": "<pixel_art|voxel|low_poly|realistic|stylized|cartoon|anime|minimalist|hand_drawn|abstract>",
    "key_technologies": ["<tech1>", "<tech2>"],
    "performance_targets": [
      {
        "platform": "<pc|web|mobile_ios|etc>",
        "target_fps": "<30-240>",
        "min_resolution": "<WxH>",
        "max_ram_mb": "<256-65536>"
      }
    ],
    "audio": {
      "music_style": "<Musical style and mood>",
      "sound_categories": ["<category1>"],
      "voice_acting": "<true|false>",
      "adaptive_music": "<true|false>"
    },
    "asset_requirements": ["<asset_type1>"],
    "networking_required": "<true|false>",
    "accessibility_features": ["<feature1>"],
    "localization_languages": ["<lang1>"]
  },
  
  "map_hints": {
    "biomes": ["<forest|desert|snow|ocean|mountain|swamp|jungle|plains|volcanic|cave|urban|ruins|dungeon|space|underwater>"],
    "map_size": "<tiny|small|medium|large|huge>",
    "obstacles": [
      {
        "type": "<obstacle_type>",
        "density": "<sparse|medium|dense>",
        "purpose": "<gameplay purpose>"
      }
    ],
    "special_features": [
      {
        "name": "<feature name>",
        "frequency": "<common|uncommon|rare|unique>",
        "requirements": ["<requirement1>"],
        "description": "<what it does>"
      }
    ],
    "connectivity": "<low|medium|high>",
    "verticality": "<none|low|medium|high>",
    "generation_style": "<procedural_rooms|cellular_automata|bsp_dungeon|wave_function_collapse|perlin_noise>",
    "enemy_spawn_zones": ["<zone_type1>"],
    "visual_themes": ["<theme1>"]
  },
  
  "risks": [
    {
      "category": "<Technical|Design|Scope|Market|Team>",
      "description": "<Risk description, 20-500 chars>",
      "severity": "<critical|major>",
      "mitigation": "<Mitigation strategy, 10-500 chars>",
      "likelihood": "<low|medium|high>"
    }
  ],
  
  "additional_notes": "<Optional additional notes, max 5000 chars>"
}
```

### Valid Enum Values Reference

**Genres**: action, rpg, puzzle, strategy, simulation, roguelike, platformer, shooter, adventure, horror, survival, racing, sports, fighting, stealth, sandbox, rhythm, visual_novel, card_game, tower_defense, idle, metroidvania

**Platforms**: pc, web, mobile_ios, mobile_android, console_playstation, console_xbox, console_nintendo, vr, ar

**Audience Rating**: everyone, teen, mature, adults_only

**Engines**: unity, unreal, godot, love2d, phaser, pygame, construct, gamemaker, custom

**Art Styles**: pixel_art, voxel, low_poly, realistic, stylized, cartoon, anime, minimalist, hand_drawn, abstract

**Progression Types**: linear, branching, open_world, roguelike_runs, level_based, skill_tree, mastery

**Narrative Delivery**: cutscenes, dialogue, environmental, collectibles, emergent, procedural, none

**System Types**: combat, movement, inventory, crafting, economy, dialogue, quest, ai, physics, weather, day_night, stealth, building, farming, cooking, fishing, trading, skill, leveling, equipment, save_load, multiplayer, achievement, tutorial, ui, audio, custom

**Biomes**: forest, desert, snow, ocean, mountain, swamp, jungle, plains, volcanic, cave, urban, ruins, dungeon, space, underwater

---

## STEP 5: Output Final Result

After the loop completes, output the structured result:

```json
{
  "execution_log": [
    {
      "iteration": 0,
      "actor_spawned": true,
      "critic_spawned": true,
      "decision": "revise|approve",
      "scores": {
        "feasibility": 8,
        "coherence": 7,
        "fun_factor": 9,
        "completeness": 8,
        "originality": 7,
        "overall": 7.85
      }
    }
  ],
  "input_type": "text|concept_art",
  "image_analysis": { "..." },
  "final_gdd": {
    "summary": "<Human-readable summary>",
    "gdd": { "<Complete GDD JSON>" },
    "risks_summary": ["<Key risks>"]
  },
  "termination": {
    "reason": "approved|max_iterations",
    "total_iterations": 2,
    "final_overall_score": 8.2
  },
  "downstream_integration": {
    "game_generator_prompt": "<Formatted prompt for game-generator>",
    "map_command_args": "<Arguments for /Map command>"
  }
}
```

---

## STEP 6: Downstream Integration

### For game-generator Integration

Extract a simplified prompt for the game-generator browser game tool:

```
Create a [GENRE] game called "[TITLE]".

Core Gameplay:
[CORE_LOOP.loop_description]

Key Mechanics:
[List of PRIMARY_ACTIONS and SYSTEM mechanics]

Win Condition: [Based on progression milestones]
Lose Condition: [Based on challenge_description]

Art Style: [TECHNICAL.art_style]
```

### For /Map Command Integration

If the GDD includes `map_hints`, generate arguments for the /Map command:

```
/Map [SETTING] map with [BIOMES] biomes, [MAP_SIZE] size, [GENERATION_STYLE] style, [CONNECTIVITY] connectivity
```

Example:
```
/Map post-apocalyptic urban map with urban,ruins biomes, large size, procedural_rooms style, medium connectivity
```

---

## USAGE EXAMPLES

### Example 1: Text-based Simple Concept
```
/GamePlan zombie survival roguelike
```

### Example 2: Detailed Text Concept
```
/GamePlan A cozy farming simulation game where players inherit a magical farm. They must grow enchanted crops, befriend magical creatures, and restore an ancient forest. Features day/night cycle, seasons, and a branching storyline with multiple endings.
```

### Example 3: With Concept Art
```
/GamePlan [attached concept art of a cyberpunk city street scene]
```

### Example 4: Specific Genre Mix
```
/GamePlan medieval city builder with roguelike elements - each playthrough is a different dynasty trying to build a lasting kingdom
```

---

## BEGIN ORCHESTRATION

**User Request**: $ARGUMENTS

NOW:
1. **FIRST**: Detect input type (text / concept art image)
2. Execute appropriate pipeline (Step 1A or 1B)
3. Spawn the Critic agent (Step 2) with Actor's output
4. Check Critic's decision and apply loop logic (Step 3)
5. Output final result with downstream integration (Step 5 & 6)

START by analyzing the input type now.
