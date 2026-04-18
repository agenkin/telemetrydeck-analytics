---
description: Top-N event names over a window — raw pipeline triage for "what's firing right now?" questions.
disable-model-invocation: true
---

# Signals

Print the top-N events by count for a rolling window. Use when the question is "what's happening in the pipeline right now?" rather than a specific analytical cut.

```bash
tdq signals $ARGUMENTS
```

Defaults: last 30 days, top 25.

Examples:
- "What's firing today?" → `tdq signals --days 1 --top 25`
- "Top 50 events last week" → `tdq signals --days 7 --top 50`

For schema discovery (which events EVER fire, with both 7d and 30d windows) prefer `/telemetrydeck-analytics:events` — it's more comparative. `signals` is for a single-window raw look.
