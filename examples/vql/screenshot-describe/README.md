# VQL screenshot + describe via nlp2uri

End-to-end flow:

1. NL prompt (`zrób zrzut ekranu vql`) → `vql://window/analyze?...`
2. `nlp2uri` compiles to `uri2vql run --uri ...`
3. Adopted PNG grid → `*.vql.json`
4. NL prompt (`opisz ekran vql`) → `vql://window/summary?...`
5. Summary returns object count, dominant colors, scene size

Requires editable install of `oqlos/vql` packages (`uri2vql`, `nlp2vql`, `dsl2vql`).

```bash
bash examples/vql/screenshot-describe/e2e.sh
```
