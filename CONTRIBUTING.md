# Contributing to msg.search

Thanks for contributing.

## Project Structure

- `main.py`: Typer CLI entrypoint
- `cli/`: command helpers (`sync`, `search`, `status`, `reset`)
- `importers/`: platform-specific parsers/connectors
- `core/`: embeddings and vector DB logic
- `search/`: query and filter logic
- `utils/`: console, config, storage, color mapping
- `scripts/`: utility scripts and smoke tests

## Development Setup

```bash
pip install -r requirements.txt
pip install -e .
```

## Running Common Checks

```bash
python3 -m py_compile main.py cli/*.py core/*.py importers/*.py search/*.py utils/*.py
python3 scripts/test_embed.py
python3 scripts/test_importers.py
```

## Adding a New Platform Importer

1. Add a new module under `importers/`.
2. Parse source data into the standard message schema:
   - `id`
   - `content`
   - `sender`
   - `timestamp` (ISO string)
   - `platform`
   - `conversation`
3. Ensure IDs are stable and deterministic for delta sync.
4. Hook platform into `cli/sync.py`.
5. Add docs in `README.md`.

If your platform shares an export format with an existing one, prefer extending a shared base parser (see `importers/meta_base.py`) instead of duplicating logic.

## Code Style

- Keep modules focused and small.
- Favor explicit helper functions over deep nested logic.
- Surface user-facing errors with clean messages.
- Keep local-first guarantees intact. Do not add remote telemetry.
- Prefer deterministic IDs and predictable outputs.

## Pull Requests

- Keep changes scoped to one step or feature.
- Include short verification notes in PR description.
- Update docs when behavior or CLI UX changes.
