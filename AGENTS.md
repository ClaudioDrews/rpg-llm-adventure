# AGENTS.md - RPG LLM Adventure

Guidelines for AI agents working on this codebase.

## Project Overview

A text-based RPG adventure game powered by LLMs (Ollama, OpenAI, Anthropic). Built with Python/FastAPI backend and vanilla JavaScript frontend.

---

## Build / Run / Test Commands

```bash
# Quick start (recommended)
./start.sh

# Manual start
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd backend && python main.py

# CLI mode
cd cli && python rpg_cli.py

# Access
# Local: http://localhost:8000
# Network: http://<IP>:8000
```

---

## Code Style Guidelines

### Python

- **Version**: Python 3.10+
- **Formatting**: 4 spaces indentation, no tabs
- **Line length**: ~100 characters
- **Imports**: Group stdlib, third-party, then local imports
- **Type hints**: Use `typing` module (Optional, List, Literal, etc.)

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `GameState`, `LLMManager` |
| Functions | snake_case | `start_game()`, `get_local_ip()` |
| Variables | snake_case | `session_id`, `narrative_style` |
| Constants | UPPER_SNAKE | `LOGS_DIR`, `FRONTEND_DIR` |
| Private | _leading_underscore | `_parse_response()` |

### Documentation

- Docstrings in **Portuguese** (project language)
- Use triple quotes for module, class, and function docs

### Error Handling

- Use specific exception types
- Provide meaningful error messages in Portuguese
- Always use try/except with proper cleanup

### Async Patterns

- Use `async/await` for I/O operations
- FastAPI endpoints are async by default
- LLM calls use `httpx.AsyncClient`

### Project Structure

```
rpg-llm-adventure/
├── backend/
│   ├── main.py          # FastAPI server
│   ├── llm_manager.py   # LLM provider management
│   └── game_state.py    # Game state models
├── frontend/
│   ├── index.html       # Web UI
│   └── app.js           # Frontend logic
├── cli/
│   └── rpg_cli.py       # Terminal interface
├── logs/                # Adventure logs (gitignored)
├── requirements.txt
└── start.sh
```

### Key Dependencies

- FastAPI 0.115.0
- uvicorn[standard] 0.32.0
- pydantic 2.9.2
- httpx 0.27.2

### Frontend (JavaScript)

- Vanilla JS, no frameworks
- Use modern ES6+ features
- Event listeners for user interactions
- Fetch API for backend communication

---

## Critical Rules

1. **NEVER** suppress type errors with `as any` or `# type: ignore`
2. **ALWAYS** use type hints for function signatures
3. **ALWAYS** handle errors gracefully with try/except
4. **NEVER** expose API keys in code (use env vars or user input)
5. **ALWAYS** validate user input before processing
6. **NEVER** commit logs or .env files
7. **ALWAYS** use Pathlib for file operations
8. **NEVER** use bare except clauses - catch specific exceptions

---

## Testing

No formal test suite exists. Test manually:

1. Start server: `./start.sh`
2. Test web UI at http://localhost:8000
3. Test CLI: `cd cli && python rpg_cli.py`
4. Test with different LLM providers (Ollama, OpenAI, Anthropic)

---

## LLM Integration Patterns

When adding new LLM providers:

1. Add to `llm_manager.py` with `_generate_<name>()` method
2. Update `Literal` type in `configure()` method
3. Add error handling for provider-specific failures
4. Update frontend dropdown in `index.html`
5. Add default model name to frontend `app.js`
