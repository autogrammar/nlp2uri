# `vql://` — CQRS + ES (v1)

| Field | Value |
|-------|-------|
| Layer | `control` |
| Pattern | `vql://{selector}?file={path}` |
| Drivers | uri2vql, dsl2vql |
| Status | active |
| IR | `—` |

## Aggregate

- **ID:** canonical URI string (`uri.raw`)
- **Stream:** `vqlEventEnvelope` appended to `EventStore`

## Commands → Events

| Command | Event |
|---------|-------|
| `Register` | `VqlRegistered` |
| `Resolve` | `VqlResolved` |
| `Compile` | `VqlCompiled` |
| `Execute` | `VqlExecuted` |

## Codegen

```bash
cd schemas && ./codegen/generate.sh --scheme vql
```
