---
description: Daily active users for the current TelemetryDeck app. Accepts optional interval / event / compare flags as arguments.
disable-model-invocation: true
---

# DAU

Run the daily-active-users recipe. Default window: last 30 days.

Pass any `$ARGUMENTS` straight through to the CLI — the user may be asking for a specific window, event filter, or period comparison:

```bash
tdq dau $ARGUMENTS
```

Examples of how users ask → what to run:

- "DAU for the last week" → `tdq dau --interval last-7d`
- "DAU trend this month" → `tdq dau --interval this-month`
- "DAU week-over-week" → `tdq dau --interval last-7d --compare prior-period`
- "DAU of App_launched last 30 days" → `tdq dau --event App_launched --days 30`

If the user didn't specify a window, use `--interval last-30d`. After the table prints, add a one-paragraph plain-English summary: peak day, trough day, trend direction, any obvious drops. Always note the opt-in-sample caveat ("Numbers reflect the opted-in cohort only").
