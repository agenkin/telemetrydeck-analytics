# TelemetryDeck v3 API — HTTP & auth reference

Load only when extending `tdq.py` or debugging the raw HTTP surface. For TQL syntax (query types, filters, aggregators, intervals, etc.) see `tql/index.md`. For normal usage, the CLI handles auth, async orchestration, and filter injection.

**Status:** v3 beta. Nominally Tier 2+ gated; grace period in effect, not enforced at time of writing. No documented per-minute rate limit. Sync endpoint may terminate long queries.

## Base URL & auth

- Base: `https://api.telemetrydeckapi.com`
- Header: `Authorization: Bearer <token>`

### Minting a bearer (what the CLI does under `login`)

```
POST /api/v3/users/login
Authorization: Basic base64(email:password)
→ { "value": "<bearer>", "expiresAt": "<iso>", "id": "...", "user": { "id": "..." } }
```

`value` is the bearer. `expiresAt` tells you when to re-mint. The CLI treats anything within 5 minutes of expiry as stale and re-mints automatically from the Keychain-stored password.

## Identifiers

| Identifier | Where it comes from | How it's used |
|------------|---------------------|---------------|
| `appID` (UUID) | App detail in TelemetryDeck dashboard; same UUID passed to the SDK `initialize(config: .init(appID:))` | `selector` filter dimension on every query |
| `insightID` | URL when viewing an insight | Path parameter to resolve a saved insight to TQL |
| `orgID` / `userID` | `GET /api/v3/users/info` | Not needed for queries; bearer is scoped to the user |

## Async query (3 steps)

```
POST /api/v3/query/calculate-async/     { ...TQL... }  → { "queryTaskID": "..." }
GET  /api/v3/task/<taskID>/status/                     → { "status": "running" | "successful" | "failed" }
GET  /api/v3/task/<taskID>/value/                      → query result
```

Poll `status` at a modest cadence (the CLI polls every 1s, caps at 30 polls / 120s wallclock). If a query pushes those limits, tighten `threshold` and shrink `relativeIntervals` instead of raising the caps — long queries either time out server-side or return data too coarse to trust.

Sync variant: drop `-async` from the path. Discouraged; the server may terminate long-running sync queries and the docs flag that future support is uncertain.

## Running a saved insight

Two-step: resolve the insight to TQL, then execute.

```
POST /api/v3/insights/<insightID>/query/     { "relativeInterval": { ... } }
→ full TQL query JSON
→ submit to /api/v3/query/calculate-async/
```

The CLI's `insight` subcommand does both.

## Error handling

- `401 Unauthorized` — bearer expired or invalid. CLI re-mints once automatically.
- `403 Forbidden` — tier gate or scope issue.
- `4xx` with a JSON body — inspect the body, the error messages are usually specific.
- Network timeout — the `calculate-async` endpoint returns a task id almost immediately; if submitting the task times out, something is wrong with the JSON shape, not the server load.

## Where to find TQL syntax

Don't read this file for TQL — it's just auth/HTTP. Go to `tql/index.md` and follow the routing table to the specific topic (query types, filters, aggregators, intervals, granularity, funnel, retention, recipes).
