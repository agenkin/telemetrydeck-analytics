# Filters

Filters narrow the rows a query sees. Every query needs the mandatory app + test-mode filter; anything else is layered on top with `and`.

## Types

| Type | Matches rows where... |
|---|---|
| `selector` | Dimension equals a single value |
| `in` | Dimension is in a set of values |
| `and` / `or` / `not` | Boolean compose other filters |
| `columnComparison` | Two dimensions equal each other |
| `regex` | Dimension matches regex |
| `interval` | Timestamp inside explicit ISO ranges |
| `range` | Dimension (numeric or lexical) inside bounds |

## `selector` — equals

```json
{"type":"selector","dimension":"license","value":"Pro"}
```

Null/missing values: use `"value": null`.

## `in` — one of

```json
{"type":"in","dimension":"license","values":["Pro","Trial"]}
```

Cheaper than `or` of selectors.

## `and` / `or` / `not`

```json
{"type":"and","fields":[
  {"type":"selector","dimension":"appID","value":"<UUID>"},
  {"type":"selector","dimension":"isTestMode","value":"false"},
  {"type":"selector","dimension":"license","value":"Pro"}
]}
```

```json
{"type":"or","fields":[
  {"type":"selector","dimension":"license","value":"Pro"},
  {"type":"selector","dimension":"license","value":"Trial"}
]}
```

```json
{"type":"not","field":{"type":"selector","dimension":"isSimulator","value":"true"}}
```

## `columnComparison`

```json
{"type":"columnComparison","dimensions":["buildNumber","appVersion"]}
```

Useful only when comparing two raw dimensions on the same row.

## `regex`

```json
{"type":"regex","dimension":"appVersion","pattern":"^2\\..*"}
```

Escape backslashes once for JSON.

## `interval`

```json
{"type":"interval","dimension":"__time","intervals":["2026-03-01T00:00:00Z/2026-03-31T23:59:59Z"]}
```

Same semantics as top-level `intervals`. Rarely needed — prefer top-level `intervals` or `relativeIntervals`.

## `range` (aka `bound`)

```json
{"type":"bound","dimension":"majorSystemVersion","lower":"14","upper":"16","ordering":"numeric"}
```

`ordering`: `numeric | alphanumeric | lexicographic | strlen`. Either bound optional.

## Mandatory app + test-mode filter

Always include:

```json
{"type":"and","fields":[
  {"type":"selector","dimension":"appID","value":"<APP-UUID>"},
  {"type":"selector","dimension":"isTestMode","value":"false"}
]}
```

Or the sentinel `{ "__auto_app_and_test_mode_filter__": true }` when running via `tdq.py query -`. Forget this and results mix other tenant apps + test traffic.

## Combining with extra predicates

Wrap the mandatory filter with your predicates in a single `and`:

```json
{"type":"and","fields":[
  {"type":"selector","dimension":"appID","value":"<UUID>"},
  {"type":"selector","dimension":"isTestMode","value":"false"},
  {"type":"selector","dimension":"type","value":"App_launched"},
  {"type":"selector","dimension":"license","value":"Pro"}
]}
```

When using the auto-filter sentinel, you can't mix it with custom `and` — the CLI only injects when `filter` is missing or exactly the sentinel. Write the full filter yourself for custom predicates.
