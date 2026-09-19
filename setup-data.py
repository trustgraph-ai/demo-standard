#!/usr/bin/env python3

"""
Shared dataset loader driven by manifest files.

Usage:
    setup-data.py gametheory                           # load by dataset ID
    setup-data.py datasets/game-theory/manifest.json   # load by manifest path
    setup-data.py --list                               # list available datasets
"""

import argparse
import json
import os
import sys

def _import_deps():
    global requests, Api, ConfigKey, ConfigValue, Triple, rdflib
    import requests as _requests
    from trustgraph.api import (
        Api as _Api, ConfigKey as _ConfigKey,
        ConfigValue as _ConfigValue, Triple as _Triple,
    )
    import rdflib as _rdflib
    requests = _requests
    Api = _Api
    ConfigKey = _ConfigKey
    ConfigValue = _ConfigValue
    Triple = _Triple
    rdflib = _rdflib


DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")
INDEX_FILE = os.path.join(DATASETS_DIR, "index.json")

DEFAULT_URL = os.getenv("TRUSTGRAPH_URL", "http://localhost:8888/")
DEFAULT_TOKEN = os.getenv("TRUSTGRAPH_TOKEN", None)


def load_index():
    with open(INDEX_FILE) as f:
        return json.load(f)


def resolve_manifest(target):
    if os.path.isfile(target):
        return os.path.abspath(target)

    index = load_index()
    for entry in index:
        if entry["id"] == target:
            return os.path.join(DATASETS_DIR, entry["path"])

    print(f"Error: '{target}' is not a manifest path or known dataset ID.")
    print("Use --list to see available datasets.")
    sys.exit(1)


def load_manifest(path):
    with open(path) as f:
        return json.load(f)


def call_iam(url, token, request):
    endpoint = url.rstrip("/") + "/api/v1/iam"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.post(endpoint, headers=headers, data=json.dumps(request))
    resp.raise_for_status()
    body = resp.json()
    if "error" in body:
        raise RuntimeError(body["error"])
    return body


def create_workspace(url, token, workspace):
    ws_id = workspace["id"]
    ws_name = workspace["name"]
    print(f"Creating workspace '{ws_id}'...")
    try:
        call_iam(url, token, {
            "operation": "create-workspace",
            "workspace_record": {
                "id": ws_id,
                "enabled": True,
                "name": ws_name,
            },
        })
        print("  Workspace created.")
    except Exception as e:
        print(f"  Workspace creation: {e}")
        print("  (may already exist, continuing)")


def start_flows(api, flows):
    for flow in flows:
        flow_id = flow["id"]
        blueprint = flow["blueprint"]
        description = flow.get("description", flow_id)
        print(f"Starting flow '{flow_id}' (blueprint: {blueprint})...")
        try:
            api.flow().start(
                blueprint_name=blueprint,
                id=flow_id,
                description=description,
            )
            print(f"  Flow '{flow_id}' started.")
        except Exception as e:
            print(f"  Flow start: {e}")
            print("  (may already be running, continuing)")


def verify_llm(api, flows):
    flow_id = flows[0]["id"] if flows else "default"
    print(f"Verifying LLM on flow '{flow_id}'...")
    result = api.flow().id(flow_id).text_completion(
        system="",
        prompt="2+2",
    )
    print(f"  LLM response: {result}")


def put_config(api, config_type, key, value):
    api.config().put([ConfigValue(type=config_type, key=key, value=value)])
    print(f"  Config set: {config_type}/{key}")


def upload_ontology(api, base_dir, ontology_list):
    print("Uploading ontology configs...")
    for entry in ontology_list:
        path = os.path.join(base_dir, entry["file"])
        with open(path) as f:
            value = f.read()
        put_config(api, "ontology", entry["key"], value)
    print(f"  {len(ontology_list)} ontology config(s) uploaded.")


def load_triples_from_file(path, fmt):
    g = rdflib.Graph()
    g.parse(path, format=fmt)
    for s, p, o in g:
        kwargs = {"s": str(s), "p": str(p), "o": str(o)}
        if isinstance(o, rdflib.term.Literal):
            if o.language:
                kwargs["o_language"] = str(o.language)
            elif o.datatype:
                kwargs["o_datatype"] = str(o.datatype)
        yield Triple(**kwargs)


def load_entity_contexts_from_file(path, fmt):
    g = rdflib.Graph()
    g.parse(path, format=fmt)
    for s, p, o in g:
        if isinstance(o, rdflib.term.URIRef):
            continue
        yield {"entity": {"t": "i", "i": str(s)}, "context": str(o)}


def load_knowledge(api, base_dir, knowledge_list):
    print("Loading knowledge graph triples and entity contexts...")
    bulk = api.bulk()

    for doc in knowledge_list:
        document_id = doc["document_id"]
        collection = doc["collection"]
        fmt = doc["format"]
        files = doc["files"]
        flow = doc.get("flow", "default")

        metadata = {
            "id": document_id,
            "metadata": [],
            "collection": collection,
        }

        for filename in files:
            path = os.path.join(base_dir, filename)
            print(f"  Loading triples from {filename}...")
            count = 0

            def counting_triples(p=path, f=fmt):
                nonlocal count
                for triple in load_triples_from_file(p, f):
                    count += 1
                    yield triple

            bulk.import_triples(
                flow=flow,
                triples=counting_triples(),
                metadata=metadata,
            )
            print(f"    {count} triples loaded.")

        for filename in files:
            path = os.path.join(base_dir, filename)
            print(f"  Loading entity contexts from {filename}...")
            count = 0

            def counting_contexts(p=path, f=fmt):
                nonlocal count
                for ctx in load_entity_contexts_from_file(p, f):
                    count += 1
                    yield ctx

            bulk.import_entity_contexts(
                flow=flow,
                contexts=counting_contexts(),
                metadata=metadata,
            )
            print(f"    {count} entity contexts loaded.")


def upload_queries(api, base_dir, query_list):
    print("Uploading queries...")
    total = 0
    for entry in query_list:
        path = os.path.join(base_dir, entry["file"])
        with open(path) as f:
            queries = json.load(f)
        for obj in queries:
            qid = obj.pop("id")
            put_config(api, "query", qid, json.dumps(obj))
        total += len(queries)
        print(f"  {len(queries)} queries from {entry['file']}")
    print(f"  {total} total queries uploaded.")


def upload_tools(api, base_dir, tool_list):
    print("Uploading tool definitions...")
    for entry in tool_list:
        path = os.path.join(base_dir, entry["file"])
        with open(path) as f:
            value = f.read()
        put_config(api, "tool", entry["key"], value)
    print(f"  {len(tool_list)} tool(s) uploaded.")


def upload_prompts(api, base_dir, prompt_list):
    print("Uploading prompt templates...")
    for entry in prompt_list:
        path = os.path.join(base_dir, entry["file"])
        with open(path) as f:
            value = f.read()
        put_config(api, "prompt", f"template.{entry['key']}", value)

    try:
        results = api.config().get(
            [ConfigKey(type="prompt", key="template-index")]
        )
        current_index = json.loads(results[0].value) if results else []
    except Exception:
        current_index = []

    for entry in prompt_list:
        if entry["key"] not in current_index:
            current_index.append(entry["key"])

    put_config(api, "prompt", "template-index", json.dumps(current_index))
    print(
        f"  {len(prompt_list)} prompt(s) uploaded, "
        f"template-index: {current_index}"
    )


def upload_schema(api, base_dir, schema_list):
    print("Uploading schema configs...")
    for entry in schema_list:
        path = os.path.join(base_dir, entry["file"])
        with open(path) as f:
            value = f.read()
        put_config(api, "schema", entry["key"], value)
    print(f"  {len(schema_list)} schema(s) uploaded.")


def load_structured_data(api, base_dir, url, token, workspace_id, sd_list):
    from trustgraph.cli.load_structured_data import load_structured_data

    print("Loading structured data...")
    for entry in sd_list:
        input_file = os.path.join(base_dir, entry["file"])
        descriptor_file = os.path.join(base_dir, entry["descriptor"])
        flow = entry.get("flow", "structured")

        print(f"  Parsing {entry['file']} (dry run)...")
        load_structured_data(
            api_url=url,
            input_file=input_file,
            descriptor_file=descriptor_file,
            parse_only=True,
            token=token,
            workspace=workspace_id,
        )

        print(f"  Loading {entry['file']} into TrustGraph...")
        load_structured_data(
            api_url=url,
            input_file=input_file,
            descriptor_file=descriptor_file,
            load=True,
            flow=flow,
            token=token,
            workspace=workspace_id,
        )
        print(f"  {entry['file']} loaded.")


def list_datasets():
    index = load_index()
    print(f"{'ID':<20} {'Name':<30} Description")
    print(f"{'─' * 20} {'─' * 30} {'─' * 40}")
    for entry in index:
        print(
            f"{entry['id']:<20} {entry['name']:<30} "
            f"{entry.get('description', '')}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Shared dataset loader driven by manifest files.",
    )
    parser.add_argument(
        "target", nargs="?",
        help="Dataset ID or path to manifest.json",
    )
    parser.add_argument(
        "-u", "--api-url", default=DEFAULT_URL,
        help=f"API URL (default: {DEFAULT_URL})",
    )
    parser.add_argument(
        "-t", "--token", default=DEFAULT_TOKEN,
        help="Auth token (default: $TRUSTGRAPH_TOKEN)",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List available datasets and exit",
    )
    parser.add_argument(
        "--skip-workspace", action="store_true",
        help="Skip workspace creation",
    )
    parser.add_argument(
        "--skip-flows", action="store_true",
        help="Skip starting flows",
    )
    parser.add_argument(
        "--skip-verify", action="store_true",
        help="Skip LLM verification",
    )
    parser.add_argument(
        "--skip-knowledge", action="store_true",
        help="Skip loading knowledge graph and structured data",
    )
    args = parser.parse_args()

    if args.list:
        list_datasets()
        return

    if not args.target:
        parser.print_help()
        sys.exit(1)

    _import_deps()

    manifest_path = resolve_manifest(args.target)
    base_dir = os.path.dirname(manifest_path)
    manifest = load_manifest(manifest_path)

    url = args.api_url
    token = args.token
    workspace = manifest["workspace"]

    print(f"Loading dataset: {manifest['name']}")
    print(f"Manifest: {manifest_path}")
    print()

    if not args.skip_workspace:
        create_workspace(url, token, workspace)

    api = Api(url, token=token, workspace=workspace["id"])

    flows = manifest.get("flows", [])

    if not args.skip_flows and flows:
        start_flows(api, flows)

    if not args.skip_verify and flows:
        verify_llm(api, flows)

    if manifest.get("ontology"):
        upload_ontology(api, base_dir, manifest["ontology"])

    if not args.skip_knowledge and manifest.get("catalog"):
        load_knowledge(api, base_dir, manifest["catalog"])

    if not args.skip_knowledge and manifest.get("knowledge"):
        load_knowledge(api, base_dir, manifest["knowledge"])

    if manifest.get("queries"):
        upload_queries(api, base_dir, manifest["queries"])

    if manifest.get("tools"):
        upload_tools(api, base_dir, manifest["tools"])

    if manifest.get("prompts"):
        upload_prompts(api, base_dir, manifest["prompts"])

    if manifest.get("schema"):
        upload_schema(api, base_dir, manifest["schema"])

    if not args.skip_knowledge and manifest.get("structured_data"):
        load_structured_data(
            api, base_dir, url, token, workspace["id"],
            manifest["structured_data"],
        )

    print("\nSetup complete.")


if __name__ == "__main__":
    main()
