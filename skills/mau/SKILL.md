---
description: Monthly active users for the current TelemetryDeck app. Accepts optional interval / event / compare flags as arguments.
disable-model-invocation: true
---

# MAU

Run the monthly-active-users recipe. Default: last 6 calendar months.

```bash
tdq mau $ARGUMENTS
```

Examples:

- "MAU for the last 12 months" → `tdq mau --months 12`
- "MAU this year" → `tdq mau --interval this-year`
- "MAU month-over-month" → `tdq mau --interval last-month --compare prior-period`

After the table prints, summarize in one paragraph: latest month's value, trend direction over the window, any month that stands out. Call out if the current month is partial (`this-month` / `this-year` compares partial-to-full).
