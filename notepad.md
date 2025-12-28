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
