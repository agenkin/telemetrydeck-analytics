---
description: Break down an event count or user count by any TelemetryDeck dimension (license, OS version, country, etc.).
disable-model-invocation: true
---

# Groupby

Run a one-dimension breakdown. `$ARGUMENTS` starts with the dimension name and then any flags:

```bash
tdq groupby $ARGUMENTS
```

Examples:

- "License split for App_launched, last 30d" → `tdq groupby license --event App_launched --interval last-30d`
- "OS major-version breakdown by users, this month" → `tdq groupby majorSystemVersion --metric users --interval this-month`
- "License share vs. last period" → `tdq groupby license --event App_launched --interval last-30d --compare prior-period`
- "Top countries last week" → `tdq groupby countryCode --metric users --interval last-7d`

If the user mentions "share" / "mix" / "split", compute percentages client-side from the result and include them in the summary. If they say "vs last month" / "trending", add `--compare prior-period`.

Always state what the metric represents: `--metric count` is event count (not users), `--metric users` is unique `clientUser` cardinality.
