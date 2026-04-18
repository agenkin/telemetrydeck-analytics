# Publishing

How to ship `telemetrydeck-analytics` as a standalone open-source repo on GitHub, listed in the **Claude Code plugin marketplace** and indexed by **skills.sh**.

---

## 0. Prereqs

- GitHub account (the examples assume `agenkin` — swap for your own).
- `gh` CLI authenticated (`gh auth login`).
- A TelemetryDeck account and test app to verify with.

---

## 1. Push the repo to GitHub

The repo already lives at `~/telemetrydeck-analytics` with `git init` done. All that's left is the first commit and the push.

```bash
cd ~/telemetrydeck-analytics

# stage + first commit
git add .
git commit -m "Initial public release — v0.6.0"

# create the GitHub repo and push
gh repo create agenkin/telemetrydeck-analytics \
    --public \
    --source=. \
    --description "TelemetryDeck product analytics for Claude Code — CLI + slash commands + progressive-disclosure TQL docs." \
    --homepage "https://github.com/agenkin/telemetrydeck-analytics" \
    --push
```

Tag the release:

```bash
git tag -a v0.6.0 -m "v0.6.0 — initial public release"
git push origin v0.6.0
gh release create v0.6.0 --title "v0.6.0" --notes "Initial public release."
```

---

## 2. Validate locally

Before publishing, run Claude's built-in validator:

```bash
claude plugin validate .
```

Both `plugin.json` and `marketplace.json` should pass. Then smoke-test as a local marketplace:

```bash
claude plugin marketplace add .
claude plugin install telemetrydeck-analytics@telemetrydeck-analytics
claude plugin list
```

Run the CLI directly from the cache to confirm `bin/tdq` works:

```bash
~/.claude/plugins/cache/telemetrydeck-analytics/telemetrydeck-analytics/0.6.0/bin/tdq --help
```

And from inside a Claude session, try a slash command:

```
/telemetrydeck-analytics:doctor
```

If everything passes, uninstall + remove the local marketplace so your next install comes from GitHub:

```bash
claude plugin uninstall telemetrydeck-analytics@telemetrydeck-analytics
claude plugin marketplace remove telemetrydeck-analytics
```

---

## 3. Publish to the Claude Code marketplace

### 3a. Self-hosted marketplace (instant, no approval)

This repo ships its own `.claude-plugin/marketplace.json`. Anyone with the repo URL can install it:

```bash
/plugin marketplace add agenkin/telemetrydeck-analytics
/plugin install telemetrydeck-analytics@telemetrydeck-analytics
```

Done. That's the full publish path for the Claude Code plugin ecosystem — the marketplace is just a GitHub repo. To ship updates, push commits (or tags) to `main`; users pick them up with `/plugin marketplace update`.

### 3b. Submit to official / third-party marketplaces (optional)

- **Official Anthropic marketplace** (`anthropics/claude-plugins-official`): watch that repo for submission instructions. At the time of writing, the marketplace is curated — open an issue or PR on that repo describing the plugin, linking to this repo.
- **Community marketplaces** (e.g. `everything-claude-code`, `awesome-claude-code-plugins`): most accept PRs that add a plugin entry pointing at your repo. Find one by running `/plugin marketplace list` after Claude Code is freshly installed.

To have your plugin featured in one of these, open a PR on their `.claude-plugin/marketplace.json` with an entry like:

```json
{
  "name": "telemetrydeck-analytics",
  "source": {
    "source": "github",
    "repo": "agenkin/telemetrydeck-analytics",
    "ref": "v0.6.0"
  },
  "description": "TelemetryDeck product analytics for Claude Code.",
  "category": "analytics",
  "keywords": ["telemetrydeck", "analytics", "dau", "mau"]
}
```

---

## 4. Publish to skills.sh

skills.sh auto-indexes any GitHub repo containing `SKILL.md` files in standard locations (`skills/<name>/SKILL.md` — which this repo already uses). Two paths:

### 4a. Zero-effort: just let users install

Once the repo is public, it works immediately:

```bash
npx skills add agenkin/telemetrydeck-analytics
```

The skills CLI scans the repo, finds every `skills/*/SKILL.md`, and installs the skill(s) into the active agent environment.

### 4b. Get listed on the leaderboard

The skills.sh homepage shows a leaderboard of popular skills. To appear there:

1. Check [skills.sh](https://skills.sh) for a "Submit" link / form.
2. If none exists, open an issue or PR on [`vercel-labs/skills`](https://github.com/vercel-labs/skills) requesting inclusion. Include:
   - Repo URL: `https://github.com/agenkin/telemetrydeck-analytics`
   - Install command: `npx skills add agenkin/telemetrydeck-analytics`
   - One-line description (see `.claude-plugin/plugin.json` `description` field)
3. The skills.sh team will typically audit for malicious content before listing (see [skills.sh/audits](https://skills.sh/audits)).

**SKILL.md sanity check.** skills.sh requires `name` + `description` in the YAML frontmatter of every `SKILL.md`. This repo's skills already meet that — verify with:

```bash
for f in skills/*/SKILL.md; do
  head -5 "$f"
  echo "---"
done
```

---

## 5. Release checklist

Before each release, walk through:

- [ ] Bump `version` in `.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` (keep them in sync)
- [ ] Run `claude plugin validate .`
- [ ] Smoke test: `/telemetrydeck-analytics:doctor` from a fresh install
- [ ] Smoke test: `tdq test` (runs 3 known-good TQL queries and asserts row counts)
- [ ] Update the version line at the bottom of `README.md`
- [ ] Commit, tag `vX.Y.Z`, push tag
- [ ] `gh release create vX.Y.Z --generate-notes`
- [ ] Announce (optional): tweet, TelemetryDeck community Slack, r/ClaudeAI

---

## 6. Troubleshooting

### `/plugin install` fails with "path not found"

You added the marketplace by URL instead of as a git repo. URL-based marketplaces can't resolve relative plugin sources. Either:

- Add via GitHub shorthand: `/plugin marketplace add agenkin/telemetrydeck-analytics`
- Or edit `marketplace.json` to use a `github` source object instead of `"./"`.

### `tdq: command not found` inside a Claude session

The plugin isn't enabled (`/plugin list` should show it as enabled). If it is enabled but `tdq` still isn't on PATH, re-enable it: `/plugin disable telemetrydeck-analytics` then `/plugin enable telemetrydeck-analytics`.

### `(no rows)` on every query

TelemetryDeck v3 envelope shape may have changed again. Re-run with `TDQ_RAW=1` to dump the raw HTTP response to stderr:

```bash
TDQ_RAW=1 tdq doctor 2>/tmp/raw.log
```

Then open an issue with the raw payload attached (scrub any API keys first).
