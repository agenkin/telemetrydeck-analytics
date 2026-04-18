---
description: Schema discovery — list every event name firing for the current TelemetryDeck app with 7-day and 30-day counts side by side.
disable-model-invocation: true
---

# Events

Run the schema-discovery command:

```bash
tdq events $ARGUMENTS
```

Defaults to the top 100 events per window. The user can pass `--top N` to widen.

After the table prints, call out:

- **Events present in 30d but absent from 7d** — they stopped firing in the last week. Classic causes: feature was removed, `@AppStorage` default-not-mirrored-to-`UserDefaults.register(defaults:)` bug, or release gating. Ask whether an engineering change correlates with the drop date.
- **Events with `count_7d` much higher than `count_30d / 4`** — new event or recent surge.
- **Suspiciously low counts on events you expected to be frequent** — may indicate a signal-ingestion regression.

If the user is hunting a specific event ("is `Transcription_completed` firing?"), grep/filter the table output for the name and report presence/absence explicitly.
