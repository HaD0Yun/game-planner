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
