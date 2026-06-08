# Dry-run hillm commands

Execute `hillm://` URIs through `uri2hillm.run_uri` with `dry_run=true` where
applicable — safe for CI, no serial/USB/camera hardware required.

## Run

```bash
./e2e.sh
python main.py
```

Example output:

```json
{
  "uri": "hillm://cmd/HEALTH",
  "ok": true,
  "verb": "HEALTH",
  "data": { "package": "hillm", "status": "ok" }
}
```
