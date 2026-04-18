---
description: Run an arbitrary TQL query against the current TelemetryDeck app. Use when no recipe fits and a hand-written TQL is required (funnel, retention, multi-dim groupBy, postAggregations, filtered aggregations).
disable-model-invocation: true
---

# Query

Run raw TQL against the current app. Two ways:

**(a) Inline JSON from `$ARGUMENTS`** — pipe it to `tdq query -`:

```bash
echo '$ARGUMENTS' | tdq query -
```

**(b) JSON file path** — pass the path directly:

```bash
tdq query $ARGUMENTS
```

Pick (b) if `$ARGUMENTS` looks like a file path, else (a).

## Writing the TQL

Before writing the JSON, read `skills/analytics/tql/index.md` in this plugin to route to the right sub-reference (filters, aggregators, intervals, funnel, retention, recipes, etc.). Do **not** try to recall TQL syntax from memory — the progressive-disclosure tree is there for a reason.

Rules that always apply:
- Set `"filter": { "__auto_app_and_test_mode_filter__": true }` unless you need a custom filter (in which case include the `appID` + `isTestMode=false` selectors yourself).
- Every query needs `queryType` and `granularity`.
- Prefer `userCount` / `thetaSketch` over deprecated `cardinality`.

If the user's first query returns `(no rows)`, re-run with `--raw` to see whether the result is genuinely empty or the parser dropped it:

```bash
tdq query /tmp/q.json --raw 2>/tmp/raw.json
```
