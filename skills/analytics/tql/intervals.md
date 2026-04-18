# Intervals — time scoping

Two ways to scope a query to a time range:

| Field | Use when |
|---|---|
| `relativeIntervals` | Dynamic ("last 30 days", "this month") — the common case |
| `intervals` | Fixed ISO 8601 range (e.g. one specific week) |

Exactly one of these is required on every query. Both together works; only `intervals` wins where they overlap.

## `relativeIntervals`

Array of `{beginningDate, endDate}` objects. Both dates use the same grammar:

```json
{"component":"day","offset":-30,"position":"beginning"}
```

- `component`: `day | week | month | quarter | year`
- `offset`: integer. Negative = past. `0` = current.
- `position`: `beginning | end` — which edge of that component window

**Standard last-N-days:**
```json
"relativeIntervals": [{
  "beginningDate":{"component":"day","offset":-30,"position":"beginning"},
  "endDate":      {"component":"day","offset":0,"position":"end"}
}]
```

**This month (month-to-date):**
```json
"relativeIntervals": [{
  "beginningDate":{"component":"month","offset":0,"position":"beginning"},
  "endDate":      {"component":"day","offset":0,"position":"end"}
}]
```

**Last calendar month:**
```json
"relativeIntervals": [{
  "beginningDate":{"component":"month","offset":-1,"position":"beginning"},
  "endDate":      {"component":"month","offset":-1,"position":"end"}
}]
```

**Previous 7 days, excluding today:**
```json
"relativeIntervals": [{
  "beginningDate":{"component":"day","offset":-7,"position":"beginning"},
  "endDate":      {"component":"day","offset":-1,"position":"end"}
}]
```

**Prior-period comparison (two intervals side-by-side):**
```json
"relativeIntervals": [
  {"beginningDate":{"component":"day","offset":-60,"position":"beginning"},
   "endDate":      {"component":"day","offset":-31,"position":"end"}},
  {"beginningDate":{"component":"day","offset":-30,"position":"beginning"},
   "endDate":      {"component":"day","offset":0,"position":"end"}}
]
```

## Common `position` pitfalls

- Use `beginning` on the start and `end` on the end. Mixing them lops off a boundary day.
- `{"component":"day","offset":0,"position":"beginning"}` = today at 00:00:00 UTC. `"end"` = today at 23:59:59.
- `{"component":"week","offset":-1,"position":"beginning"}` = Monday 00:00 of last week (Druid defaults weeks to ISO — Mon start). Verify for your tenant if unsure.

## `intervals` — fixed ISO 8601

```json
"intervals": ["2026-01-01T00:00:00Z/2026-03-31T23:59:59Z"]
```

Slash-separated start/end. Multiple ranges allowed in the array — they union.

Use for:
- Reproducible historical queries ("what was March 2026's Pro share?")
- Back-dated reports where "last 30 days" would drift
- Period-over-period queries that compare specific named weeks

## CLI interval shortcuts

The `tdq.py` CLI exposes named intervals on `dau`, `mau`, `groupby`:

- `last-Nd` — any N, e.g. `last-7d`, `last-90d`
- `last-week`, `this-week` (alias: `wtd`)
- `last-month`, `this-month` (alias: `mtd`)
- `last-year`, `this-year` (alias: `ytd`)

Use `--interval <name>` — it wins over `--days`/`--months`.

For raw TQL, write `relativeIntervals` directly.
