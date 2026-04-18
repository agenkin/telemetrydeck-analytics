# Aggregators

Aggregators compute metric values per bucket (timeseries) or per group (topN/groupBy). Every non-scan query needs at least one.

## Quick picker

| Goal | Aggregator |
|---|---|
| Count matching events | `eventCount` or `count` |
| Count unique users | `userCount` |
| Sum / min / max / mean a numeric parameter | `doubleSum` / `doubleMin` / `doubleMax` / `doubleMean` |
| Unique cardinality of any dimension (not just users) | `thetaSketch` |
| Conditional metric inside one query | `filtered` wrapping another aggregator |
| Latest value per user | `longLast` / `doubleLast` / `stringLast` |

**`cardinality` is deprecated** — TelemetryDeck docs say "use thetaSketch instead". Use `userCount` specifically for unique users.

## `eventCount` / `count`

```json
{"type":"eventCount","name":"events"}
```

Counts rows matching the query's filter. `count` is the Druid alias — same result.

## `userCount`

```json
{"type":"userCount","name":"users"}
```

Unique `clientUser` count. Canonical for DAU/MAU. Much faster than a cardinality sketch.

## `thetaSketch` — cardinality for any dimension

```json
{"type":"thetaSketch","name":"unique_countries","fieldName":"countryCode","size":16384}
```

`size` optional (default 16384, higher = more accurate, more memory). Use when counting uniques of something other than `clientUser`.

## Numeric aggregators

Only work on numeric-typed parameters.

```json
{"type":"doubleSum","name":"total_duration","fieldName":"durationSeconds"}
{"type":"doubleMin","name":"min_duration","fieldName":"durationSeconds"}
{"type":"doubleMax","name":"max_duration","fieldName":"durationSeconds"}
{"type":"doubleMean","name":"avg_duration","fieldName":"durationSeconds"}
```

`longSum`, `longMin`, `longMax` also exist for integer-typed parameters.

If you get zero/null results, the parameter may be string-typed — TelemetryDeck parameters are strings by default unless the SDK sent them as numbers.

## `filtered` — conditional aggregation

Wrap any aggregator with a filter to count only a subset, inside a single query:

```json
{
  "type":"filtered",
  "filter":{"type":"selector","dimension":"license","value":"Pro"},
  "aggregator":{"type":"eventCount","name":"pro_events"}
}
```

Lets you emit multiple conditional metrics per bucket without a `groupBy`:

```json
"aggregations": [
  {"type":"filtered","filter":{"type":"selector","dimension":"license","value":"Pro"},
   "aggregator":{"type":"eventCount","name":"pro"}},
  {"type":"filtered","filter":{"type":"selector","dimension":"license","value":"Free"},
   "aggregator":{"type":"eventCount","name":"free"}}
]
```

## Last-value aggregators

```json
{"type":"longLast","name":"last_build","fieldName":"buildNumber"}
{"type":"stringLast","name":"last_version","fieldName":"appVersion"}
{"type":"doubleLast","name":"last_duration","fieldName":"durationSeconds"}
```

"Last" = most recent by `__time`. Useful for "current state per user" style queries combined with a `clientUser` groupBy.

## `cardinality` (deprecated)

```json
{"type":"cardinality","name":"users","fields":["clientUser"]}
```

Still accepted by the API, but marked deprecated. Prefer `userCount` for users, `thetaSketch` for other dimensions.

## `postAggregations`

Derived metrics computed from other aggregators, in the same query:

```json
"aggregations": [
  {"type":"eventCount","name":"events"},
  {"type":"userCount","name":"users"}
],
"postAggregations": [
  {"type":"arithmetic","name":"events_per_user","fn":"/",
   "fields":[
     {"type":"fieldAccess","fieldName":"events"},
     {"type":"fieldAccess","fieldName":"users"}
   ]}
]
```

`fn`: `+`, `-`, `*`, `/`, `quotient`. Other postAgg types: `constant`, `fieldAccess`, `javascript` (likely disabled), `thetaSketchEstimate`.
