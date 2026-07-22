# AGENTS.md — slskd Agent Integration Guide

This document tells any AI agent (Claude, Codex, Gemini, Hermes, GPT, etc.)
how to interact with slskd on this machine.

## Overview

slskd is a headless Soulseek P2P client running as a macOS launchd service.
It exposes a REST API on localhost port 5030. Agents can search for music
files and enqueue downloads.

## Authoritative Agent Tool: `slskd-agent`

AI agents MUST exclusively use `slskd-agent` (`~/.local/bin/slskd-agent` or `scripts/slskd-agent`) for all interactions with slskd.
Do NOT use ad-hoc inline curl calls or custom scripts. It handles search polling, quality validation, completeness checks, cover art inclusion, and peer fallback rotation automatically.

### CLI Usage

```bash
# Check service & API health
slskd-agent service status

# Search and auto-enqueue complete album (with artwork/meta & fallback peers)
slskd-agent album "Demolition Hammer - Epidemic of Violence" 320

# Search query directly
slskd-agent search "Opeth - Ghost of Perdition"

# List active and queued downloads
slskd-agent downloads
```

## REST API Reference (For low-level inspection)

### Authentication

Add this header to every request:

```
X-API-Key: LrL7I2k2jMJu7Xc1QX0JcDtgqq0ZP1YzGNy75DYLi8X
```

### Endpoints Summary

| Purpose | Method | Path |
|---|---|---|
| Health check | GET | `/api/v0/application` |
| Search | POST | `/api/v0/searches` |
| Search results | GET | `/api/v0/searches/{id}` |
| List searches | GET | `/api/v0/searches` |
| Enqueue download | POST | `/api/v0/transfers/downloads` |
| List downloads | GET | `/api/v0/transfers/downloads` |
| Browse user | POST | `/api/v0/users/{username}/browse` |
| User info | GET | `/api/v0/users/{username}/info` |

## Guardrails

- Do NOT enqueue a download for a file that's already queued or completed. Check `slskd-agent downloads` first.
- Keep searches focused: `"Artist - Track Title"` or `"Artist Album Name"`.
- If a search returns 0 results, try a simpler query or alternate spelling.
- Downloads land in `/Volumes/Eksternal/Music/Soulseek` with subdirectories named after the source username.
