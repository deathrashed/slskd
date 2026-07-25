# slskd REST API Reference

Base URL: `http://127.0.0.1:5030/api/v0`
Auth: `X-API-Key: LrL7I2k2jMJu7Xc1QX0JcDtgqq0ZP1YzGNy75DYLi8X`
Content-Type: `application/json`

---

## Application

### Health Check

```
GET /api/v0/application
```

Returns 200 if running (no auth required for this endpoint).
Returns 401 without auth.

---

## Searches

### Submit a Search

```
POST /api/v0/searches
```

Request body:

```json
{
  "searchText": "Opeth - Ghost of Perdition",
  "searchTimeout": 15000
}
```

| Field | Type | Description |
|---|---|---|
| `searchText` | string (required) | The search query. Best format: `"Artist - Track"` or `"Album"` |
| `searchTimeout` | int (optional) | Max time to wait for results in ms. Default: 15000 |

Response (202 Accepted):

```json
{
  "id": "aa726015-bcc8-4cd0-b302-6d26863a9d72",
  "searchText": "Opeth - Ghost of Perdition",
  "state": "InProgress",
  "responseCount": 0,
  "fileCount": 0,
  "responses": [],
  "startedAt": "2026-07-20T22:28:03.656746Z",
  "token": 11
}
```

### Get Search Results

```
GET /api/v0/searches/{id}
```

Response when complete:

```json
{
  "id": "aa726015-bcc8-4cd0-b302-6d26863a9d72",
  "searchText": "Opeth",
  "state": "Completed, ResponseLimitReached",
  "responseCount": 250,
  "fileCount": 1523,
  "responses": [
    {
      "username": "some_user",
      "files": [
        {
          "filename": "/Music/Opeth/Ghost of Perdition/01 Ghost of Perdition.flac",
          "size": 52428800,
          "bitRate": 1411,
          "length": 636
        }
      ],
      "queueLength": 0,
      "freeSlots": true,
      "uploadSpeed": 524288
    }
  ]
}
```

States:
- `InProgress` — search still running, poll again
- `Completed, ResponseLimitReached` — hit 250 response limit, results ready
- `Completed, TimedOut` — search finished with partial results
- `Completed` — search finished

User fields:
- `username` — Soulseek user to download from
- `files` — array of matching files
- `freeSlots` — true if user has download slots open
- `uploadSpeed` — user's upload speed in bytes/sec

File fields:
- `filename` — full remote path (use this for download)
- `size` — file size in bytes
- `bitRate` — bitrate in kbps (lossless FLAC = usually 900-1411)
- `length` — duration in seconds

### List All Searches

```
GET /api/v0/searches
```

Returns all recent searches with their final states.

---

## Downloads

### Enqueue a Download

```
POST /api/v0/transfers/downloads
```

Request body:

```json
{
  "username": "some_user",
  "filename": "/Music/Opeth/Ghost of Perdition/01 Ghost of Perdition.flac"
}
```

| Field | Type | Description |
|---|---|---|
| `username` | string (required) | Soulseek username from search results |
| `filename` | string (required) | Full remote path from search file entry |
| `size` | int (optional) | File size in bytes (for deduplication) |

Response (200):

```json
{
  "username": "some_user",
  "filename": "/Music/Opeth/Ghost of Perdition/01 Ghost of Perdition.flac",
  "size": 52428800,
  "state": "Queued",
  "priority": 0,
  "position": 1
}
```

### List All Downloads

```
GET /api/v0/transfers/downloads
```

Returns all transfers with their current state. Useful for deduplication:
check if a username+filename pair already exists before enqueuing again.

States: `Queued`, `InProgress`, `Completed`, `Errored`, `Cancelled`

### Get Specific Download

```
GET /api/v0/transfers/downloads/{id}
```

### Remove a Download

```
DELETE /api/v0/transfers/downloads/{id}
```

---

## Users

### Browse User's Shares

```
POST /api/v0/users/{username}/browse
```

Initiates a browse of a user's shared files. Returns the browse ID.
Poll status with `GET /api/v0/users/{username}/browse` (returns progress).

### Get User Info

```
GET /api/v0/users/{username}/info
```

Returns user's description, picture, and stats.

### Get User Status

```
GET /api/v0/users/{username}/status
```

Returns 0 (offline), 1 (away), or 2 (online).

---

## Error Responses

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created |
| 202 | Accepted (search started) |
| 400 | Bad request — missing or invalid fields |
| 401 | Unauthorized — missing or invalid API key |
| 404 | Not found — search/download ID doesn't exist |
| 409 | Conflict — already in progress (searches/downloads) |
| 500 | Server error |

---

## Best Practices

1. **Polling interval**: Wait 8-12 seconds after submitting a search before
   first poll. Then poll every 2-3 seconds until state != `InProgress`.

2. **Duplicate prevention**: Always check `/api/v0/transfers/downloads` before
   enqueuing. Filter by exact username + filename match.

3. **File selection priority**:
   - Prefer FLAC > ALAC > WAV > MP3 320 > MP3 V0 > MP3 V2
   - Within same format, prefer larger files (better quality rip)
   - Avoid files < 1MB for music (likely samples or junk)
   - Avoid filenames containing `.exe`, `.zip`, `.rar` in music searches

4. **Download path**: Files land in `/Volumes/Eksternal/Music/Soulseek`
   with a subdirectory named after the source user. slskd auto-renames
   if a file with the same name exists.

5. **Rate limiting**: Don't submit more than 5 concurrent searches.
   The server has a circuit breaker at 200 pending searches.
