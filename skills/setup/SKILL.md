---
description: Interactive first-run setup for the TelemetryDeck analytics CLI — prompts for email/password, mints a bearer, lets the user pick an app.
disable-model-invocation: true
---

# Setup

Run the interactive setup flow for the TelemetryDeck CLI bundled with this plugin. Use the Bash tool to execute:

```bash
tdq login
```

The CLI prompts for:
1. TelemetryDeck email
2. Password (hidden input)
3. App selection — it lists the user's apps after the bearer is minted and asks the user to pick one by number (or paste a UUID)

Secrets go into the OS-native store (Keychain on macOS, libsecret on Linux, file fallback mode 0600 otherwise). Non-secret state (email, registered apps, token expiry) goes in the platform config dir.

After this runs once, every other `tdq` subcommand refreshes the bearer automatically.

If the user passes a specific UUID as `$ARGUMENTS`, skip the picker:

```bash
tdq login --app-id "$ARGUMENTS"
```

When setup finishes, run `tdq doctor` and relay the output so the user sees the end-to-end health check pass.
