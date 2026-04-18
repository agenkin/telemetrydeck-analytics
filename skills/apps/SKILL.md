---
description: List, switch, add, or remove the TelemetryDeck apps the CLI queries against. Accepts a subcommand as arguments (use / list / add / remove / refresh).
disable-model-invocation: true
---

# Apps

Manage registered TelemetryDeck apps. Pass the subcommand + args through `$ARGUMENTS`:

```bash
tdq apps $ARGUMENTS
```

Common uses:

| User intent | Command |
|---|---|
| List registered apps | `tdq apps` |
| Switch current app | `tdq apps use <uuid\|name\|index>` |
| Rename an app | `tdq apps use <uuid> --name "New Name"` |
| Register another app | `tdq apps add <uuid> --name "Other App" [--set-current]` |
| Unregister an app | `tdq apps remove <selector>` |
| Re-pull the list from the API | `tdq apps refresh` |

If `$ARGUMENTS` is empty, run `tdq apps` (list). If the user's intent is ambiguous ("switch to my other app") and `tdq apps` shows multiple registered, show the list and ask which one to pick rather than guessing. If only one other app is registered, you can switch without asking — but state what you did.
