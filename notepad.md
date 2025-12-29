# Game Planner Project Notes

## NOTEPAD SECTION

[2025-12-29 03:20] - Task 5: Implement Dual-Agent Orchestrator

### DISCOVERED ISSUES
- Lint errors for unused `last_error` variables in orchestrator.py (_invoke_actor and _invoke_critic methods)
- Test fixtures had `unlock_condition` values that didn't meet 10-character minimum requirement
- models.py had minor changes needed to align with test expectations

### IMPLEMENTATION DECISIONS
- Used context replacement strategy (not append) for Actor iterations - fresh context each time
- Critic auto-approves on failure to avoid blocking the pipeline
- Actor uses fallback GDD on parse errors to ensure graceful degradation
- Implemented exponential backoff for network errors (1s, 2s, 4s base)
- Temperature settings: Actor=0.6 (creative), Critic=0.2 (consistent) per arXiv:2512.10501
- Max iterations default: 3 (suitable for game planning complexity)

### PROBLEMS FOR NEXT TASKS
- None identified - Task 5 is complete and all systems functional

### VERIFICATION RESULTS
- Ran: `python -m pytest tests/ -v` → 174 tests passed (28 orchestrator + 146 others)
- Ran: `python -m ruff check orchestrator.py tests/test_orchestrator.py` → All checks passed!
- Verified: Actor-Critic loop respects max_iterations config
- Verified: Error handling works (JSONDecodeError → fallback, TimeoutError → template, NetworkError → backoff)

### LEARNINGS
- Test command: `python -m pytest tests/ -v` runs all tests
- Lint command: `python -m ruff check <files>`
- Convention: All unlock_condition fields must be >= 10 characters
- Convention: Use `from_llm_response()` class method for parsing LLM outputs
- Gotcha: Unused variable declarations trigger F841 lint errors even if intentionally unused
- Pattern: GameDesignDocument.from_llm_response() handles JSON extraction from markdown code blocks

Time taken: ~30 minutes (continuation session)

[2025-12-29 03:41] - Task 6: Implement CLI Entry Point

### DISCOVERED ISSUES
- Initial CLI structure used callback with `invoke_without_command=True` which caused argument parsing issues
- Typer interprets options after positional arguments as commands when subcommands exist
- Windows CP949 encoding issues with Rich's Unicode spinners required stdout wrapper

### IMPLEMENTATION DECISIONS
- Changed from callback-based to command-based structure with `plan` command
- CLI usage: `python main.py plan "concept" --mock` instead of positional arg in callback
- Added Windows encoding fix with UTF-8 TextIOWrapper
- Used Rich for progress display with spinners, tables, and panels
- gdd_to_markdown() function converts GDD to human-readable markdown format
- `--quiet` mode for raw JSON/markdown output to stdout (for piping)
- `--no-preview` flag to suppress GDD preview panel

### PROBLEMS FOR NEXT TASKS
- None identified - CLI is fully functional with all tests passing

### VERIFICATION RESULTS
- Ran: `python -m pytest tests/test_cli.py -v` → 30 tests passed
- Ran: `python -m pytest tests/ -v` → 204 tests passed total
- Ran: `python -m ruff check main.py tests/test_cli.py` → All checks passed!
- Manual test: `python main.py plan "zombie roguelike" --mock -q` → Valid JSON output
- Manual test: `python main.py version` → Shows version info
- Manual test: `python main.py validate gdd.json` → Validates GDD files

### LEARNINGS
- CLI Pattern: Use explicit commands (e.g., `plan`) instead of callback with `invoke_without_command=True` when subcommands exist
- Typer quirk: Options after positional argument can be misinterpreted as commands
- Windows encoding: Wrap stdout/stderr with UTF-8 TextIOWrapper for Rich console compatibility
- Test pattern: Use `CliRunner` from `typer.testing` for CLI tests
- Convention: Commands use verb names (plan, validate, version)

Time taken: ~20 minutes (continuation session)

[2025-12-29 03:56] - Task 8: Create GamePlan Slash Command

### DISCOVERED ISSUES
- No issues found - directory structure was already in place from Task 7

### IMPLEMENTATION DECISIONS
- Followed /Map command structure as reference (YAML frontmatter + markdown body)
- Used `subagent_type="game-designer"` and `subagent_type="game-reviewer"` to spawn the agents from Task 7
- Input type detection: TEXT only vs CONCEPT ART image (like /Map's text vs image vs heightmap)
- Dual-Agent loop: Max 3 iterations, then best-effort output
- Included complete GDD schema documentation inline (all enums, all field constraints)
- Added downstream integration section for game-generator and /Map command
- Revision loop passes previous GDD + critic feedback to Actor for targeted fixes

### PROBLEMS FOR NEXT TASKS
- Task 9 will need to copy GamePlan.md and agent YAMLs to global ~/.opencode/ directory
- Task 10-11 will implement actual game-generator and /Map integration output formatters

### VERIFICATION RESULTS
- File created: `game-planner/.opencode/command/GamePlan.md` (confirmed exists)
- YAML frontmatter valid: description, argument-hint present
- Command structure matches /Map.md reference pattern
- All GDD schema sections documented
- Usage examples included

### LEARNINGS
- OpenCode command structure: YAML frontmatter + $ARGUMENTS placeholder for user input
- Task tool spawns agents via subagent_type matching agent YAML filenames
- Conservative Certainty Policy: Critic should approve unless CERTAIN of problem
- /Map command uses image type detection (text/reference_image/heightmap) - good pattern for other commands

Time taken: ~15 minutes

[2025-12-29 04:05] - Task 9: Install to Global OpenCode Config

### DISCOVERED ISSUES
- No issues found - global ~/.opencode/ directory already existed with proper structure
- Both ~/.opencode/ and ~/.config/opencode/ exist; used ~/.opencode/ as primary (matches /Map installation)

### IMPLEMENTATION DECISIONS
- Target: ~/.opencode/ directory (C:\Users\hdy86\.opencode\)
  - Matches existing /Map command and pcg-actor/pcg-critic agent locations
- Created install.sh (Unix/Mac) and install.bat (Windows) scripts
  - Both scripts backup existing files before overwriting
  - Colored output for user-friendly installation experience
  - Auto-detect OpenCode config location (priority: ~/.opencode > ~/.config/opencode)
- Created comprehensive README.md with:
  - Installation instructions (both automatic and manual)
  - Python CLI usage examples
  - OpenCode /GamePlan command examples
  - GDD schema reference with all enum values
  - Architecture diagram (ASCII)
  - Critic review framework documentation
  - Downstream integration guides

### PROBLEMS FOR NEXT TASKS
- Task 10 will need to implement actual --format game-generator output formatter
- Task 11 will need to generate actual /Map command arguments from map_hints

### VERIFICATION RESULTS
- Files copied successfully:
  - game-designer.yaml → ~/.opencode/agent/ (12454 bytes)
  - game-reviewer.yaml → ~/.opencode/agent/ (11135 bytes)
  - GamePlan.md → ~/.opencode/command/ (16341 bytes)
- All 204 tests pass (no regressions)
- install.sh made executable with chmod +x
- README.md created (~550 lines with comprehensive documentation)

### LEARNINGS
- OpenCode global config locations:
  - Windows: ~/.opencode/ or ~/.config/opencode/
  - Unix: ~/.opencode/ or ~/.config/opencode/
- Priority: ~/.opencode/ takes precedence (project-level in home dir acts as global)
- Existing agents in ~/.opencode/agent/: pcg-actor.yaml, pcg-critic.yaml
- Existing commands in ~/.opencode/command/: Map.md
- Bash works on Windows via Git Bash/MSYS2 shell

Time taken: ~10 minutes

[2025-12-29 11:34] - Task 10: Add game-generator Integration

### DISCOVERED ISSUES
- No issues found - game-generator project was in expected location
- game-generator input format is simple: just a text prompt string passed to AI

### IMPLEMENTATION DECISIONS
- Created `gdd_to_game_generator_prompt()` function in main.py
- Format converts GDD to a detailed text prompt optimized for browser game generation
- Prompt includes: title, genres, gameplay (actions, challenge, rewards), mechanics, visual style, unique features
- Added browser game requirements (single HTML, score tracking, restart, controls)
- Limited mechanics and milestones in output to avoid overwhelming the generator (top 5 each)
- Truncated long text fields (setting, difficulty curve) to keep prompt focused

### PROBLEMS FOR NEXT TASKS
- Task 11 will add /Map integration hints to GDD output
- Task 12 will do final testing and documentation

### VERIFICATION RESULTS
- Ran: `python -m pytest tests/test_cli.py -v` → 41 tests passed (10 new game-generator tests)
- Ran: `python -m pytest tests/ -v` → 215 tests passed total (no regressions)
- Ran: `python -m ruff check main.py tests/test_cli.py` → All checks passed!
- Manual test: `python main.py plan "space shooter" --mock --format game-generator -q` → Valid prompt output

### LEARNINGS
- game-generator input format: Simple text prompt like "Create this game: {description}"
- game-generator uses AI (Claude/OpenAI) to generate single HTML file with embedded CSS/JS
- game-generator project location: C:\Users\hdy86\game-generator (Next.js app)
- CLI format option: Use `--format game-generator` (with hyphen, not underscore)
- Prompt structure: GAMEPLAY, KEY MECHANICS, VISUAL STYLE, UNIQUE FEATURES, REQUIREMENTS sections

Time taken: ~15 minutes

[2025-12-29 12:05] - Task 12: Final Testing and Documentation

### DISCOVERED ISSUES
- No issues found - all tests pass, lint is clean, README is comprehensive
- Minor cleanup: .gitignore was missing .coverage and nul entries

### IMPLEMENTATION DECISIONS
- Confirmed all 226 tests pass (100% pass rate)
- Verified 94% code coverage (exceeds 80% requirement)
- Confirmed README.md is 924 lines with all required sections:
  - Architecture (ASCII diagram), Installation (Win/Unix), Usage (CLI + OpenCode)
  - GDD Schema (complete field reference), Integration Guides
  - Examples, Testing, Configuration, API Reference, Troubleshooting
- Added .coverage and nul to .gitignore for cleaner git status

### PROBLEMS FOR NEXT TASKS
- None for Phase 1-3 (COMPLETE)
- Phase 4 tasks (13+) will need research on GDD→Game generation

### VERIFICATION RESULTS
- Ran: `python -m pytest tests/ -v` → 226 tests passed
- Ran: `python -m pytest tests/ --cov=. --cov-report=term-missing` → 94% coverage
  - models.py: 98%, prompts.py: 100%, orchestrator.py: 82%, main.py: 86%, llm_provider.py: 77%
- Ran: `python -m ruff check .` → All checks passed!
- Verified: No TODO/FIXME/XXX/HACK comments in code
- Verified: README.md is 924 lines (>500 requirement)
- Verified: All sections present (Features, Architecture, Installation, Usage, GDD Schema, Integration Guides, etc.)

### LEARNINGS
- Test coverage command: `python -m pytest tests/ --cov=. --cov-report=term-missing`
- Line count command on Windows: `wc -l README.md` (via Git Bash)
- Section headers in README extracted via: `grep "^## " README.md`
- .gitignore should include .coverage, htmlcov/, and nul for cleaner status

Time taken: ~10 minutes (verification and finalization)

[2025-12-29 12:09] - Task 17: Verify Documentation (Final Work Verification Checklist Item 5)

### DISCOVERED ISSUES
- No issues found - README.md is comprehensive and complete

### IMPLEMENTATION DECISIONS
- Performed thorough line-by-line verification of all 5 documentation requirements
- Documented exact line numbers for each requirement for traceability

### PROBLEMS FOR NEXT TASKS
- None - this is a verification-only task

### VERIFICATION RESULTS
README.md verification (925 lines total):

| Requirement | Status | Location |
|-------------|--------|----------|
| Installation instructions (pip + OpenCode) | ✅ | Lines 50-100: Two options (OpenCode Global + Python CLI) |
| Usage examples (CLI + OpenCode) | ✅ | Lines 102-153: /GamePlan command + Python CLI examples |
| GDD schema reference | ✅ | Lines 155-209 (overview), Lines 368-506 (complete field reference) |
| Architecture diagram | ✅ | Lines 16-48: ASCII Dual-Agent architecture diagram |
| Integration guides for downstream systems | ✅ | Lines 225-258 + Lines 726-793 (game-generator, /Map, Unity) |

All 5 documentation requirements verified ✅

### LEARNINGS
- README.md has grown to 925 lines (was 924 in previous task)
- Architecture diagram uses ASCII art format suitable for terminals
- Integration guides cover 4 systems: game-generator, /Map, Unity, and Programmatic

Time taken: ~3 minutes (verification only)

[2025-12-29 12:10] - Task 18: Verify Existing Features Unaffected (Final Work Verification Checklist Item 6)

### DISCOVERED ISSUES
- No issues found - all existing systems are intact and unmodified

### IMPLEMENTATION DECISIONS
- Verified by checking file modification dates and git commit history
- Confirmed game-planner is the ONLY new project created (as intended)

### PROBLEMS FOR NEXT TASKS
- None - this is a verification-only task

### VERIFICATION RESULTS
| Check | Status | Evidence |
|-------|--------|----------|
| `/Map` command exists | ✅ PASS | `~/.opencode/command/Map.md` - Last modified Dec 27 19:03 (BEFORE Dec 29 work) |
| `dual_agent_pcg` unchanged | ✅ PASS | Last commits: `a8d3baa`, `83eed82` (Dec 24-25, before Dec 29 work) |
| `game-generator` unchanged | ✅ PASS | Last commit: `8da152d` from Dec 17 (Create Next App, before work) |
| `game-planner` is NEW | ✅ PASS | All 15 commits from Dec 29 - this is the only new project |

File date analysis:
- /Map command: Dec 27 19:03 (before our Dec 29 work)
- dual_agent_pcg files: Dec 24-25 (before our work)
- game-generator files: Dec 17 (well before our work)
- game-planner files: Dec 29 (our new project)

Git history analysis:
- dual_agent_pcg: 2 commits total, none from Dec 29
- game-generator: 1 commit (initial), none from Dec 29
- game-planner: 15 commits, all from Dec 29 (expected)

All 3 verification criteria met ✅

### LEARNINGS
- Game-planner project was created as an isolated new project (best practice)
- No cross-contamination with existing projects
- /Map command uses TileWorldCreator4 for 3D map generation
- dual_agent_pcg is the reference architecture we adapted for game-planner

Time taken: ~5 minutes (verification only)

[2025-12-29 12:41] - Add HTML Format Output to Game Planner

### DISCOVERED ISSUES
- No major issues found - existing code structure was clean and easy to extend
- Minor lint issues: unused import (Optional), unused variables (rewards, avatar) - fixed

### IMPLEMENTATION DECISIONS
- Created `html_template.py` module with `gdd_to_html(gdd: GameDesignDocument) -> str` function
- Used the reference HTML file `gdd-axis-of-us.html` for styling consistency
- Dark theme with neon accents: --bg-primary (#0f0f1a), --accent (#e94560), --neon-blue (#00d9ff)
- All CSS embedded in HTML for single-file distribution
- Auto-opens browser when --output not specified (saves to `gdd-{title-slug}.html`)
- Sections: Hero, Navigation, Meta, Core Loop, Systems, Progression, Narrative, Characters, Technical, Risks, Map Hints
- Used html.escape() for XSS-safe HTML generation
- Responsive design with CSS Grid and media queries

### PROBLEMS FOR NEXT TASKS
- None identified - HTML format fully integrated

### VERIFICATION RESULTS
- Ran: `python -m pytest tests/test_cli.py -v` → 71 tests passed (19 new HTML tests)
- Ran: `python -m ruff check html_template.py main.py` → All checks passed!
- Manual test: `python main.py plan "zombie roguelike" --mock --format html --output test.html` → Valid HTML

### LEARNINGS
- html.escape() is the standard library function for escaping HTML special characters
- webbrowser.open() with Path.absolute().as_uri() opens local files in default browser
- Title slug generation: re.sub(r'[^\w\s-]', '', title).lower() + re.sub(r'[\s_]+', '-', ...).strip('-')
- CLI option: Use `--format html` to generate styled HTML output
- CSS variables make theme customization easy (:root { --accent: #e94560; })

Time taken: ~15 minutes

[2025-12-29 15:00] - Improve SYSTEM_SPECIFICATION.md with Visual Diagrams

### DISCOVERED ISSUES
- Original SYSTEM_SPECIFICATION.md had only 3 Mermaid diagrams
- Section numbers were inconsistent (duplicate section 3 after initial edits)
- Some sections were text-heavy without visual aids (CLI, Prompt, Integration)
- File Structure section was plain text only
- No Quick Visual Overview for at-a-glance understanding

### IMPLEMENTATION DECISIONS
- Added Quick Visual Overview at top with flowchart showing Input→Process→Output
- Added mindmap diagram for System Overview (technology stack visualization)
- Added Design Pillars section with 4-pillar flowchart (Quality, Self-Improving, Extensible, Reliable)
- Added Pydantic Models class diagram showing full hierarchy (GameDesignDocument, CriticFeedback, etc.)
- Added State Diagram for Refinement states (Initializing→Actor→Critic→Approved/Revise loop)
- Added LLM Provider layer diagram (BaseLLMProvider abstraction pattern)
- Added Prompt layer diagram (Constants→Functions flow)
- Added CLI command flow diagram (Commands→Options→Outputs)
- Enhanced 5-Dimension Review Framework with visual flowchart and severity diagram
- Enhanced Integration Interfaces with architecture overview diagram
- Enhanced File Structure with hierarchical flowchart
- Enhanced Quality Metrics with visual metric blocks
- Added Table of Contents at end for navigation
- Renumbered all sections properly (1-15)
- Added horizontal rule separators between major sections

### PROBLEMS FOR NEXT TASKS
- None identified - document is now comprehensive and visual

### VERIFICATION RESULTS
- Before: 3 Mermaid diagrams, 430 lines
- After: 16 Mermaid diagrams, 922 lines
- Added 13 NEW diagrams:
  1. Quick Visual Overview flowchart
  2. System Overview mindmap
  3. Design Pillars flowchart
  4. Pydantic Models class diagram
  5. Refinement State diagram
  6. LLM Provider layer flowchart
  7. Prompt layer flowchart
  8. CLI command flow diagram
  9. 5-Dimension Framework flowchart
  10. Issue Severity diagram
  11. Integration Architecture flowchart
  12. File Structure hierarchical diagram
  13. Quality Metrics visualization
- All Mermaid syntax valid (flowchart, mindmap, classDiagram, stateDiagram-v2, sequenceDiagram)
- All existing content preserved
- Section structure improved from flat to visual/scannable

### LEARNINGS
- Mermaid supports multiple diagram types: flowchart, mindmap, classDiagram, stateDiagram-v2, sequenceDiagram
- mindmap syntax uses indentation for hierarchy (no arrows)
- stateDiagram-v2 supports notes with `note right of`
- classDiagram uses `*--` for composition relationships
- Style blocks use fill colors like `fill:#e8f5e9` for visual differentiation
- subgraph labels can include emojis and HTML tags like `<br/>`
- Tables with centered headers use `|:---:|` alignment syntax

Time taken: ~20 minutes

[2025-12-29 15:15] - Update html_template.py to Generate Richer Visual GDDs

### DISCOVERED ISSUES
- No issues found - existing html_template.py was well-structured and easy to extend
- LSP import resolution error for models.py is a path context issue (not a real error)

### IMPLEMENTATION DECISIONS
- Added Mermaid.js CDN script (v11) with dark theme configuration
- Created `_generate_core_loop_mermaid()` function to generate flowchart from primary_actions
- Created `_generate_systems_mermaid()` function to show system relationships and dependencies
- Added `_escape_mermaid()` helper function to sanitize text for Mermaid syntax
- Implemented collapsible `<details>` sections for:
  - Hook elements, feedback mechanisms (core loop)
  - Mechanics lists per system
  - Difficulty levels, story beats, world lore
  - Performance targets, accessibility features, localization
  - Special map features, obstacles
- Added emoji icons to all section headers (📋, 🔄, ⚙️, 📈, etc.)
- Added priority badges with color coding (Critical=red, High=orange, Medium=blue)
- Enhanced visual hierarchy with system tags and colored indicators
- Added neon-purple CSS variable for diagrams
- Added print styles for PDF export compatibility
- Added dependency legend below system relationship diagram
- Added character role emoji mapping (protagonist, antagonist, mentor, etc.)
- Enhanced footer with AI-generated branding

### PROBLEMS FOR NEXT TASKS
- None identified - all enhancements are backward compatible

### VERIFICATION RESULTS
- Ran: `python -m pytest tests/ -v` → 245 tests passed (all passing)
- Ran: `python -m ruff check html_template.py` → All checks passed!
- Manual test: Generated test-enhanced.html with enhanced visuals
- Verified: Mermaid.js CDN script included at line 636
- Verified: Mermaid diagrams render in core loop (flowchart) and systems (relationship graph)
- Verified: Collapsible sections work with <details>/<summary> elements
- Verified: All existing functionality preserved

### LEARNINGS
- Mermaid.js v11 CDN: `https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js`
- Mermaid dark theme: Use `mermaid.initialize({ theme: 'dark' })` for dark backgrounds
- Mermaid syntax escaping: Replace [], {}, <>, # with safer alternatives
- Collapsible sections: Use native `<details>` and `<summary>` elements (no JS needed)
- CSS variable --neon-purple: #a855f7 for diagram accent colors
- Print styles: Use `@media print` with `break-inside: avoid` for cards

Time taken: ~25 minutes
