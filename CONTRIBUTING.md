# Contributing to The Aviator

Thanks for your interest in contributing! Here's how to get started.

## Getting Started

1. Fork the repository
2. Clone your fork and set up the environment (see [README](readme.md))
3. Create a feature branch: `git checkout -b my-feature`
4. Make your changes
5. Run the tests: `python -m pytest tests/ -q`
6. Commit and push: `git push origin my-feature`
7. Open a Pull Request

## Code Style

- Python 3.12+
- Follow PEP 8
- Use type hints for function signatures
- Keep SQL in `db_manager.py` — other modules should not contain raw queries

## Architecture

The project follows a **Repository → Service → UI** pattern:

| Layer | Files | Rule |
|-------|-------|------|
| Repository | `db_manager.py` | All SQL lives here |
| Service | `game_logic.py`, `airport_service.py`, `player_service.py` | Pure logic, returns dicts |
| UI | `main.py` | User interaction only |
| Game | `action_game.py`, `sprites.py` | Pygame action level |

## Testing

- All tests are in `tests/`
- Tests use a real database connection (configured via `.env`)
- Run: `python -m pytest tests/ -q`
- Add tests for any new logic or bug fixes

## Reporting Issues

Open an issue with:
- Steps to reproduce
- Expected vs actual behaviour
- Python version and OS

## Pull Request Guidelines

- One feature/fix per PR
- Include tests for new functionality
- Make sure all existing tests pass
- Update README if you change setup steps or add features
