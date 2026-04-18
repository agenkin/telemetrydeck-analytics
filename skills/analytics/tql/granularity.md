# Granularity — bucket size

Every query needs `granularity`. Controls row count for `timeseries`; for `topN`/`groupBy`/`funnel`/`retention` it controls whether results are bucketed or flattened.

## Values

| Value | Bucket | Common use |
|---|---|---|
| `all` | No buckets — one row total | `topN`, `groupBy`, most aggregate reports |
| `none` | Per-signal — raw rows | Debugging only. Huge payloads. |
| `second`, `minute`, `fifteen_minute`, `thirty_minute` | Sub-hour | Real-time ops dashboards |
| `hour` | Hourly | Intraday patterns |
| `day` | Daily | DAU, daily trends |
| `week` | Weekly | WAU, weekly roll-ups |
| `month` | Monthly | MAU, monthly reports |
| `quarter` | Quarterly | Board-deck rollups |
| `year` | Yearly | Long-term baselines |

Weeks start Monday (ISO). Month/quarter/year boundaries follow UTC calendar.

## Picking the right one

- **Flat aggregate** (one number per group): `all`
- **Trend over time**: match to the interval
  - `last-7d` → `day`
  - `last-30d` → `day` (30 rows) or `week` (4–5 rows)
  - `last-90d` → `day` (90 rows) or `week`
  - `last-year` → `month` or `week`
- **topN over a period**: `all` — else you'll get top-N-per-bucket which is usually not what you want.

## `all` on `groupBy` / `topN`

Both query types almost always use `granularity: "all"`. Setting `day` on a `groupBy` produces per-day + per-group rows — sometimes useful (stacked area chart input), usually overwhelming.

## `none` is rarely right

`none` returns every signal as its own row. For 30d of a busy app that's hundreds of thousands of rows. Server often times out. Use `scan` + `limit` for raw rows instead.

## Timezone

All buckets are UTC. The API does not accept a timezone override at time of writing. If the app's users cluster in one zone, expect day boundaries to not match their local day.
