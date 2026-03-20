# msg.search (`msgsearch`)

Search your personal message history across platforms, locally and privately.

- Local-first by default
- Semantic search over message content
- Metadata filters for sender/date/platform
- No cloud backend required for core usage

## Platforms

<p>
  <img src="https://cdn.simpleicons.org/telegram" height="18" alt="Telegram" /> Telegram
  &nbsp;&nbsp;
  <img src="https://cdn.simpleicons.org/whatsapp" height="18" alt="WhatsApp" /> WhatsApp
  &nbsp;&nbsp;
  <img src="https://cdn.simpleicons.org/apple/9ca3af" height="18" alt="Apple" /> iMessage (macOS only)
  &nbsp;&nbsp;
  <img src="https://cdn.simpleicons.org/instagram" height="18" alt="Instagram" /> Instagram
  &nbsp;&nbsp;
  <img src="https://cdn.simpleicons.org/messenger" height="18" alt="Messenger" /> Messenger
  &nbsp;&nbsp;
  <img src="https://cdn.simpleicons.org/discord" height="18" alt="Discord" /> Discord
</p>

## Privacy

- Your messages stay on your machine
- Embeddings and vector index are stored locally in `~/.msgsearch/`
- No telemetry or analytics in normal operation
- Deleting `~/.msgsearch/` removes all indexed data

## Requirements

- Python `3.10+`
- macOS required for iMessage support
- One-time model download on first embedding run

## Installation

```bash
git clone https://github.com/yourusername/msg.search
cd msg.search
pip install -r requirements.txt
pip install -e .
```

## Quick Start

1) Sync a platform:

```bash
msgsearch sync telegram
msgsearch sync imessage
msgsearch sync whatsapp --file /path/to/export.zip
```

2) Search your messages:

```bash
msgsearch search "that pasta place"
msgsearch search "job offer" --platform telegram --from "Sarah"
msgsearch search "address" --after 2023-01-01 --before 2023-12-31
```

3) Check platform status:

```bash
msgsearch status
```

4) Reset indexed data (if needed):

```bash
msgsearch reset --platform telegram
msgsearch reset
```

## CLI Reference

```bash
msgsearch sync <platform> [--file PATH]
msgsearch sync all
msgsearch search "<query>" [--platform P] [--from NAME] [--after DATE] [--before DATE] [--limit N]
msgsearch status
msgsearch reset [--platform P]
```

## Data Directory

`msgsearch` stores local state in:

```text
~/.msgsearch/
  db/
  raw/
  logs/
  config.json
```

## Status

Active development. See `project_plan.md` for build phases and progress.

