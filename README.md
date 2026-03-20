# msg.search (`msgsearch`)

Search your personal message history across platforms, locally.

- **Private by default**: messages stay on your machine
- **Offline-first**: works without internet after first model download
- **Semantic search**: find messages by meaning, not just keywords

## Supported platforms (v1)

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

## Install

Requirements:
- Python 3.10+

Setup:

```bash
pip install -r requirements.txt
```

## Quickstart

Index messages (first time) or update the index (later):

```bash
msgsearch sync imessage
msgsearch sync telegram
msgsearch sync whatsapp
msgsearch sync instagram
msgsearch sync messenger
msgsearch sync discord

msgsearch sync all
```

Search:

```bash
msgsearch search "restaurant recommendation"
msgsearch search "job offer" --from "Sarah" --platform imessage --after 2020-01-01
```

See what is connected:

```bash
msgsearch status
```

Wipe indexed data:

```bash
msgsearch reset
msgsearch reset --platform telegram
```

## Notes

- **Data location**: everything is stored in `~/.msgsearch/`. Delete that folder to remove all indexed data.
- **iMessage on macOS**: you may need to grant your terminal Full Disk Access to read `~/Library/Messages/chat.db`.
- **Discord exports**: `msgsearch` only reads a local export file you provide. It does not call Discord APIs or request tokens.

## Status

Work in progress. The interface above is the target CLI.

