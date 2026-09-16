# Dataset Manifests

## Problem

Seven setup scripts duplicate the same loading logic with minor variations.
Adding a new demo means copying a script and editing it. The web UI also
needs to discover and load datasets but can't reuse the Python scripts.

## Goals

- One **manifest file per dataset** describing what to load, not how.
- A **manifest index** so both the CLI loader and the web UI can discover
  available datasets.
- All file references are **relative to the manifest** so they work over
  local file access, git clone, or the GitHub API.
- A single **shared Python loader** replaces the seven setup scripts.

## Manifest format

JSON. Lives alongside the dataset files, e.g.
`datasets/game-theory/manifest.json`.

```json
{
  "id": "gametheory",
  "name": "Game Theory",
  "description": "Game theory analysis of political events",

  "workspace": {
    "id": "gametheory",
    "name": "Game Theory"
  },

  "flows": [
    { "blueprint": "everything", "id": "default", "description": "Default" }
  ],

  "ontology": [
    { "key": "hwsec-ontology", "file": "hwsec-ontology.json" }
  ],

  "knowledge": [
    {
      "document_id": "urn:doc:game-theory",
      "collection": "default",
      "format": "turtle",
      "files": [
        "game-theory-ontology.ttl",
        "clacton-byelection.ttl"
      ]
    }
  ],

  "queries": [
    { "file": "game-theory-queries.json" },
    { "file": "game-theory-graph-rag-queries.json" },
    { "file": "game-theory-agent-queries.json" }
  ],

  "tools": [
    { "key": "game-theory-query", "file": "game-theory-tool.json" }
  ],

  "prompts": [
    { "key": "retail-assistant", "file": "retail-assistant-prompt.json" }
  ],

  "schema": [
    { "key": "stars", "file": "stars-schema.json" }
  ],

  "structured_data": [
    {
      "file": "hyg_v42.csv",
      "descriptor": "stars-sdl.json",
      "flow": "structured"
    }
  ]
}
```

### Field reference

| Field | Required | Type | Notes |
|---|---|---|---|
| `id` | yes | string | Dataset identifier. Used to look up manifests from the index. |
| `name` | yes | string | Human-readable dataset name. |
| `description` | no | string | Shown in the web UI dataset picker. |
| `workspace` | yes | object | Workspace to create. |
| `workspace.id` | yes | string | Workspace ID. Used as-is for the IAM create-workspace call. |
| `workspace.name` | yes | string | Human-readable workspace name shown in the UI. |
| `flows` | no | array | Flows to start. Most demos have one; space has two. Omit to skip. |
| `ontology` | no | array | JSON ontology configs to upload. Each entry has `key` (config key) and `file` (relative path). Omit if the ontology is only loaded as TTL triples. |
| `knowledge` | no | array | Documents to load as triples and entity contexts. Each entry is one logical document containing one or more TTL files. |
| `knowledge[].document_id` | yes | string | Document URN for metadata. |
| `knowledge[].collection` | yes | string | Collection name, typically `"default"`. |
| `knowledge[].format` | yes | string | RDF serialisation format, e.g. `"turtle"`. Passed to the parser; allows other formats (e.g. `"xml"`, `"json-ld"`) in future. |
| `knowledge[].files` | yes | array | Relative paths to data files. Order matters (ontology files first). |
| `queries` | no | array | Query JSON files. Each file contains an array of query objects with an `id` field. |
| `tools` | no | array | Tool definitions. `key` is the config key, `file` is relative path. |
| `prompts` | no | array | Prompt templates. `key` is the prompt ID (stored as `template.<key>`). The loader updates the `template-index` automatically. |
| `schema` | no | array | Schema configs to upload. Each entry has `key` (config key) and `file` (relative path). |
| `structured_data` | no | array | Structured data loads. Each entry has `file` (data file), `descriptor` (SDL descriptor file), and `flow` (target flow ID). |

Sections that are `null` or omitted are skipped.

## Manifest index

`datasets/index.json` lists all available manifests:

```json
[
  {
    "id": "gametheory",
    "name": "Game Theory",
    "description": "Game theory analysis of political events",
    "path": "game-theory/manifest.json"
  },
  {
    "id": "hwsec",
    "name": "Hardware Security",
    "description": "Hardware security vulnerability analysis",
    "path": "hwsec/manifest.json"
  }
]
```

Paths are relative to the `datasets/` directory. The web UI resolves
these against its base URL; the CLI loader resolves them against the
local filesystem.

## Shared Python loader

A single script `setup-data.py` at the repo root replaces all seven
per-demo scripts. Usage:

```
setup-data.py gametheory              # load by dataset ID
setup-data.py datasets/game-theory/manifest.json  # load by manifest path
setup-data.py --list                  # list available datasets from index
```

It supports the same `--skip-*` flags as the current scripts:
`--skip-workspace`, `--skip-flows`, `--skip-verify`, `--skip-knowledge`.

### Loader operations (in order)

1. **Create workspace** - uses `workspace.id` and `workspace.name` from manifest
2. **Start flows** - iterates `flows` array
3. **Verify LLM** - sends test prompt to first flow
4. **Upload ontology** - if `ontology` is present
5. **Load knowledge** - if `knowledge` is present; imports triples then
   entity contexts per file
6. **Upload queries** - if `queries` is present
7. **Upload tools** - if `tools` is present
8. **Upload prompts** - if `prompts` is present; updates template-index
9. **Upload schema** - if `schema` is present
10. **Load structured data** - if `structured_data` is present

### Web UI usage

The web UI follows the same logical sequence but fetches files over HTTP
(GitHub raw content or API) instead of local filesystem reads. The
manifest tells it what to fetch; the UI calls the TrustGraph API
directly for each operation.

The web UI resolves file paths by joining the manifest's directory URL
with the relative path from the manifest. For example, if the manifest
is at `https://raw.githubusercontent.com/.../datasets/game-theory/manifest.json`
and a knowledge file is `"game-theory-ontology.ttl"`, the resolved URL
is `https://raw.githubusercontent.com/.../datasets/game-theory/game-theory-ontology.ttl`.

## Migration

Once the shared loader is working, the individual `setup-*-data.py`
scripts can be removed. The manifests become the single source of truth
for what each demo dataset contains.
