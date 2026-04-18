---
description: Run the TelemetryDeck CLI end-to-end health check (platform, config, secret store, auth, query round-trip).
disable-model-invocation: true
---

# Doctor

Run the `tdq doctor` end-to-end health check. Use the Bash tool:

```bash
tdq doctor
```

Relay the output verbatim. If any check reports `FAIL`, explain what the remediation is in one line each:

- **platform / secret store** — install `libsecret-tools` on Linux, or set `TELEMETRYDECK_PASSWORD` + `TELEMETRYDECK_TOKEN` env vars for CI/containers.
- **config file** — run `/telemetrydeck-analytics:setup` (or `tdq login`).
- **whoami (auth)** — credentials rejected; run setup with `tdq login --reset`.
- **query round-trip returns 0 rows** — either the app is genuinely quiet (check with `/telemetrydeck-analytics:events`), the wrong appID is current (check `tdq apps`), or a parser regression (re-run with `TDQ_RAW=1 tdq doctor` to see the raw JSON).

Do not offer to "auto-fix" — surface the hint and let the user run the next step.
