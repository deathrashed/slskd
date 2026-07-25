# slskd Architecture

## System Overview

slskd is a .NET-based headless Soulseek client that runs as a macOS launchd
service. It provides a REST API for searching and downloading music from the
Soulseek P2P network.

```
┌─────────────────────────────────────────────────────────┐
│                      macOS Host                          │
│                                                          │
│  ┌──────────────┐     ┌──────────────────────────────┐   │
│  │  launchd      │────▶│  slskd daemon                │   │
│  │  (KeepAlive)  │     │  (.NET 10, Kestrel web)      │   │
│  └──────────────┘     │                              │   │
│                        │  Port 5030 (HTTP API)        │   │
│  ┌──────────────┐     │  Port 5031 (HTTPS)           │   │
│  │  AI Agents    │────▶│  Port 50300 (Soulseek P2P)   │   │
│  │  (Hermes,     │     └──────────┬───────────────────┘   │
│  │   Claude,     │                │                        │
│  │   Codex, etc) │     ┌──────────▼───────────────────┐   │
│  └──────────────┘     │    Soulseek Network            │   │
│                        │    (server.slsknet.org:2242)   │   │
│  ┌──────────────┐     └──────────────────────────────┘   │
│  │  External     │                                        │
│  │  Volume       │     /Volumes/Eksternal/                │
│  │  (SSD)        │       ├── Audio/ (shared)              │
│  └──────────────┘     │   └── Music/Soulseek/ (dl)       │
│                        │                                    │
│  ┌──────────────┐     │                                    │
│  │  ~/.config/   │     │  Config & docs repo               │
│  │  slskd/       │     │                                    │
│  └──────────────┘     └──────────────────────────────────────┘
```

## Data Flow

### Search Flow

```
Agent → POST /api/v0/searches
  → slskd sends query to Soulseek network
  → Peers respond with matching files
  → Agent polls GET /api/v0/searches/{id}
  → slskd returns aggregated results
  → Agent selects best file
```

### Download Flow

```
Agent → POST /api/v0/transfers/downloads
  → slskd queues file in Soulseek transfer queue
  → When slot opens: slskd requests file from peer
  → File downloads to /Volumes/Eksternal/Music/Soulseek/<username>/
  → Transfer state: Queued → InProgress → Completed
```

## Configuration Sources

slskd loads config in this priority order:
1. CLI flags (highest)
2. Environment variables (`SLSKD_*`)
3. YAML config file (`slskd.yml`)
4. Defaults (lowest)

The canonical config is at:
`~/Library/Application Support/slskd/slskd.yml`

A copy for repo management is at:
`~/.config/slskd/config/slskd.yml`

## Persistence

| Data | Storage |
|---|---|
| Search history | `data/search.db` (SQLite) |
| Transfers | `data/transfers.db` (SQLite) |
| Messages | `data/messaging.db` (SQLite) |
| Events | `data/events.db` (SQLite) |
| Shares cache | `data/shares.local.bak.db` (SQLite, memory mode) |

## Security Model

- API key required for all endpoints (except `/api/v0/application` health check)
- Web UI requires basic auth (same credentials as API user)
- JWT tokens used for web session persistence (7-day TTL)
- API keys scoped to roles: `readonly`, `readwrite`, `administrator`
- All traffic restricted to localhost (127.0.0.1) — no remote access
- HTTPS available on port 5031 with auto-generated self-signed cert

## Resource Budget

| Resource | Usage | Notes |
|---|---|---|
| RAM | ~80-120MB idle | Acceptable for 8GB system |
| CPU | ~0% idle | Spikes to 30-50% during share scan |
| CPU | ~5-10% during active downloads | Scales with transfer count |
| Disk | ~50MB for SQLite databases | Grows with search/transfer history |
| Network | Depends on transfers | Soulseek uses port 50300 |
