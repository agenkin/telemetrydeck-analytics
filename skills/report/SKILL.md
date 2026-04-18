---
description: Generate a short markdown analytics report answering a specific product question. Pass the question as arguments.
disable-model-invocation: true
---

# Report

Write a compact markdown analytics report that answers the user's question in `$ARGUMENTS`. This skill is the high-level wrapper: pick the right sub-query (recipe or raw TQL), run it, and turn the numbers into a narrative.

## Process

1. **Parse the question** in `$ARGUMENTS`. Identify: metric (count vs. users), dimension (if any), window, comparison target.
2. **Pick the command**:
   - DAU/MAU trend → `tdq dau` / `tdq mau`
   - Breakdown by one dimension → `tdq groupby <dim>`
   - Which events fire → `tdq events`
   - Funnel / retention / multi-dim groupby / derived metric → write raw TQL and run via `tdq query -` (consult `skills/analytics/tql/index.md` for syntax).
3. **Run it** — use the Bash tool. Capture the table output.
4. **Write the report** using this structure:

```markdown
## <question restated as a header>

**Top-line:** <one sentence with the key number and window>

**Method:** `<the exact `tdq …` invocation you ran>`

**Result:**
<markdown table — paste the CLI output directly>

**Interpretation:** <1–3 sentences: what the numbers mean, any trend or outlier, compared-to-what>

**Caveats:** Opt-in cohort only (TelemetryDeck samples self-selected users). <add channel skew / partial-period / small-sample notes if applicable>
```

5. **Where to save**: inline in the conversation by default. If the user asks for a file, ask them where to save it; write to the absolute path they give. Suggest `~/Documents/TelemetryDeck/YYYY-MM-DD-<slug>.md`. **Never create new top-level folders in the current working directory.**

## Defaults

- Window: last 30 days unless the question implies otherwise.
- Format: `table` (markdown-ready).
- Always include the opt-in-cohort caveat.
- For "trending" / "growing" / "vs. last period" phrasings, add `--compare prior-period`.
