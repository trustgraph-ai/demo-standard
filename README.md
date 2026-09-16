
# TrustGraph Demo Datasets

Demo datasets for TrustGraph, each with a manifest-driven loader.

## Available datasets

| ID | Name | Description |
|----|------|-------------|
| `space` | Space Exploration | Solar system missions and HYG star catalogue |
| `risk` | Risk Management | Enterprise security events, actors, and incident response |
| `lithuanialaw` | Lithuanian Law | Cybersecurity legislation and institutional governance |
| `gametheory` | Game Theory | Political strategy modelled as a sequential game |
| `hwsec` | Hardware Security | IoT device teardowns and vulnerability analysis |
| `retail` | Retail UX | AI shopping assistant with product compatibility and user journeys |

## Usage

List available datasets:

```
python3 list-datasets.py
python3 list-datasets.py -v    # verbose: show manifest details
```

Load a dataset by ID:

```
python3 setup-data.py space
python3 setup-data.py risk
python3 setup-data.py gametheory
```

Or by manifest path:

```
python3 setup-data.py datasets/space/manifest.json
```

Use `--help` to see options for skipping individual steps or
overriding the API URL and token.

## Dataset structure

Each dataset lives in its own directory under `datasets/` with a
`manifest.json` that declares its workspace, flows, knowledge graph
files, queries, tools, prompts, and any structured data. The loader
reads the manifest and handles all setup steps automatically.
