# Compile hillm:// URIs

Build `hillm://cmd/{VERB}?...` URIs with `uri2hillm`, then compile them to
`OSAction` argv lists through `nlp2uri.compile_uri_to_actions` and the CQRS
`uri2hillm` driver.

Requires `uri2hillm` (from the [hillm](https://github.com/semcod/hillm) monorepo
or PyPI once published):

```bash
pip install ../hillm/packages/uri2hillm   # editable from sibling checkout
```

## Run

```bash
./e2e.sh
python main.py
```
