---
description: Interactive first-run setup for the TelemetryDeck analytics CLI — prompts for email/password, mints a bearer, lets the user pick an app.
disable-model-invocation: true
---

# Setup

`tdq login` requires a real TTY for interactive prompts. Claude Code's Bash tool is not a TTY, so attempt the login and handle the two cases:

## Case 1 — credentials not yet stored (first run)

Running `tdq login` via Bash will fail with:

```
stdin is not a TTY — cannot prompt for email.
Run `tdq login` directly in your terminal.
```

Tell the user: **open a terminal and run `tdq login`**. Walk them through what to expect:

1. TelemetryDeck email prompt
2. Password prompt (hidden)
3. Numbered app picker — type the number next to their app and press Enter
4. A login summary is printed on success

Once they confirm it completed, run `tdq doctor` via Bash to verify the token is live.

## Case 2 — credentials already stored, only app selection needed

If email + password are already in the keychain (e.g. re-setup after switching apps), the non-TTY error will be on the app picker step. The CLI prints the app list before exiting. Read the app names and UUIDs from the error output and ask the user which app to use. Then run:

```bash
tdq login --app-id <chosen-uuid>
```

`--app-id` skips the picker entirely and works non-interactively.

## Case 3 — `$ARGUMENTS` contains a UUID

Skip the picker immediately:

```bash
tdq login --app-id $ARGUMENTS
```

## After any successful login

Run `tdq doctor` and relay the output so the user sees the end-to-end health check pass.
