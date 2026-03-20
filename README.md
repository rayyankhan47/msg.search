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

## Platform Sync Instructions

### Telegram (auto-connect, recommended)

```bash
msgsearch sync telegram
```

On first run, you authenticate with phone number + OTP (and 2FA password if enabled).  
`msgsearch` stores a local Telegram session under `~/.msgsearch/telegram_session/` and reuses it.

If needed, Telegram export-file fallback is still supported via `--file`.

### iMessage (auto-connect on macOS)

```bash
msgsearch sync imessage
```

If access fails, grant Full Disk Access to your terminal:

- System Settings -> Privacy & Security -> Full Disk Access
- Add your terminal app, then run sync again

### WhatsApp (manual export)

1. In WhatsApp, export a chat as `.txt` (or ZIP if available)
2. Run:

```bash
msgsearch sync whatsapp --file /path/to/export.txt
```

or

```bash
msgsearch sync whatsapp --file /path/to/export.zip
```

### Instagram (Meta export)

1. Instagram -> Settings -> Your Activity -> Download Your Information
2. Request export with:
   - Format: JSON
   - Scope: Messages
3. Wait for Meta email
4. Run:

```bash
msgsearch sync instagram --file /path/to/export.zip
```

### Messenger (Meta export)

1. Facebook -> Settings -> Your Information -> Download Your Information
2. Request export with:
   - Format: JSON
   - Scope: Messages
3. Wait for Meta email
4. Run:

```bash
msgsearch sync messenger --file /path/to/export.zip
```

Meta exports can take hours to days depending on account size.

### Discord (local JSON file only)

1. Ensure you already have a Discord DM export JSON in DiscordChatExporter-compatible format
2. Run:

```bash
msgsearch sync discord --file /path/to/export.json
```

`msgsearch` validates local file format, then indexes messages.

## Discord & Terms of Service

`msgsearch` does **not** connect to Discord APIs, does **not** request tokens, and does **not** perform exports.  
It only reads a local JSON file you provide.

Exporting Discord messages with third-party tools may violate Discord Terms of Service.  
The creator of `msg.search` does not endorse or facilitate ToS violations.  
You are fully responsible for how your export file was obtained.

## Performance Expectations

Performance depends on machine specs, data distribution, and model cache state.  
Use:

```bash
python3 scripts/benchmark.py --mode embed --messages 10000 --batch-size 128
python3 scripts/benchmark.py --mode search --messages 50000 --queries 20 --top-k 10
```

Current indicative local run (small sample) showed:

- Embedding + insert throughput: ~199 messages/sec (`200` message run)
- Average query latency: ~0.86 ms (`500` indexed messages, `5` queries)

Practical expectation target for v1:

- Search latency should remain under `500ms` around `50,000` indexed messages.

## Status

Active development. See `project_plan.md` for build phases and progress.

