#!/usr/bin/env python3

"""
Sets up the TrustGraph solar system demo workspace with knowledge graph
data, ontology, queries, and tools.

Equivalent to the shell commands in README.md but using the Python API.
"""

import argparse
import json
import os
import sys
import time

import requests
from trustgraph.api import Api, ConfigValue, Triple
import rdflib


DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")

DEFAULT_URL = os.getenv("TRUSTGRAPH_URL", "http://localhost:8888/")
DEFAULT_TOKEN = os.getenv("TRUSTGRAPH_TOKEN", None)

WORKSPACE = "space"


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


def create_workspace(url, token):
    print(f"Creating workspace '{WORKSPACE}'...")
    try:
        call_iam(url, token, {
            "operation": "create-workspace",
            "workspace_record": {
                "id": WORKSPACE,
                "enabled": True,
                "name": "Space exploration",
            },
        })
        print("  Workspace created.")
    except Exception as e:
        print(f"  Workspace creation: {e}")
        print("  (may already exist, continuing)")


def start_flow(api, blueprint, flow_id, description):
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


def verify_llm(api, flow_id="default"):
    print(f"Verifying LLM on flow '{flow_id}'...")
    result = api.flow().id(flow_id).text_completion(
        system="",
        prompt="2+2",
    )
    print(f"  LLM response: {result}")


def put_config(api, config_type, key, value):
    api.config().put([ConfigValue(type=config_type, key=key, value=value)])
    print(f"  Config set: {config_type}/{key}")


def upload_ontology(api):
    print("Uploading ontology config...")
    path = os.path.join(
        DATASETS_DIR, "solar-system", "solar-system-ontology.json"
    )
    with open(path) as f:
        value = f.read()
    put_config(api, "ontology", "solar-system-ontology", value)


def load_triples_from_file(path):
    g = rdflib.Graph()
    g.parse(path, format="turtle")
    for s, p, o in g:
        yield Triple(s=str(s), p=str(p), o=str(o))


def load_entity_contexts_from_file(path):
    g = rdflib.Graph()
    g.parse(path, format="turtle")
    for s, p, o in g:
        if isinstance(o, rdflib.term.URIRef):
            continue
        yield {"entity": {"t": "i", "i": str(s)}, "context": str(o)}


def load_knowledge(api, flow="default"):
    print("Loading knowledge graph triples and entity contexts...")
    files = [
        os.path.join(
            DATASETS_DIR, "solar-system", "solar-system-ontology.ttl"
        ),
        os.path.join(
            DATASETS_DIR, "solar-system", "solar-system-data.ttl"
        ),
    ]
    document_id = "urn:doc:solar-system"
    collection = "default"

    bulk = api.bulk()

    for path in files:
        print(f"  Loading triples from {os.path.basename(path)}...")
        count = 0

        def counting_triples(p=path):
            nonlocal count
            for triple in load_triples_from_file(p):
                count += 1
                yield triple

        bulk.import_triples(
            flow=flow,
            triples=counting_triples(),
            metadata={
                "id": document_id,
                "metadata": [],
                "collection": collection,
            },
        )
        print(f"    {count} triples loaded.")

    for path in files:
        print(f"  Loading entity contexts from {os.path.basename(path)}...")
        count = 0

        def counting_contexts(p=path):
            nonlocal count
            for ctx in load_entity_contexts_from_file(p):
                count += 1
                yield ctx

        bulk.import_entity_contexts(
            flow=flow,
            contexts=counting_contexts(),
            metadata={
                "id": document_id,
                "metadata": [],
                "collection": collection,
            },
        )
        print(f"    {count} entity contexts loaded.")


def upload_queries(api, dataset, filename, label):
    print(f"Uploading {label} queries...")
    path = os.path.join(DATASETS_DIR, dataset, filename)
    with open(path) as f:
        queries = json.load(f)
    for obj in queries:
        qid = obj.pop("id")
        put_config(api, "query", qid, json.dumps(obj))
    print(f"  {len(queries)} {label} queries uploaded.")


def upload_stars_schema(api):
    print("Uploading stars schema config...")
    path = os.path.join(DATASETS_DIR, "stars", "stars-schema.json")
    with open(path) as f:
        value = f.read()
    put_config(api, "schema", "stars", value)


def load_stars_data(api, url, token):
    print("Loading stars structured data...")
    from trustgraph.cli.load_structured_data import load_structured_data

    input_file = os.path.join(DATASETS_DIR, "stars", "hyg_v42.csv")
    descriptor_file = os.path.join(DATASETS_DIR, "stars", "stars-sdl.json")

    print("  Parsing (dry run)...")
    load_structured_data(
        api_url=url,
        input_file=input_file,
        descriptor_file=descriptor_file,
        parse_only=True,
        token=token,
        workspace=WORKSPACE,
    )

    print("  Loading into TrustGraph...")
    load_structured_data(
        api_url=url,
        input_file=input_file,
        descriptor_file=descriptor_file,
        load=True,
        flow="structured",
        token=token,
        workspace=WORKSPACE,
    )
    print("  Stars data loaded.")


def upload_tools(api):
    print("Uploading tool definitions...")
    tool_files = {
        "solar-system-query": os.path.join(
            DATASETS_DIR, "solar-system", "solar-system-tool.json"
        ),
        "stars-query": os.path.join(
            DATASETS_DIR, "stars", "stars-tool.json"
        ),
    }
    for key, path in tool_files.items():
        with open(path) as f:
            value = f.read()
        put_config(api, "tool", key, value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-u", "--api-url", default=DEFAULT_URL,
        help=f"API URL (default: {DEFAULT_URL})",
    )
    parser.add_argument(
        "-t", "--token", default=DEFAULT_TOKEN,
        help="Auth token (default: $TRUSTGRAPH_TOKEN)",
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
        help="Skip loading knowledge graph data",
    )
    args = parser.parse_args()

    url = args.api_url
    token = args.token

    # Step 1: Create workspace
    if not args.skip_workspace:
        create_workspace(url, token)

    api = Api(url, token=token, workspace=WORKSPACE)

    # Step 2: Start flows
    if not args.skip_flows:
        start_flow(api, "everything", "default", "Default")
        start_flow(api, "structured", "structured", "Structured")

    # Step 3: Verify LLM
    if not args.skip_verify:
        verify_llm(api, "default")

    # Step 4: Upload ontology
    upload_ontology(api)

    # Step 5: Load knowledge graph
    if not args.skip_knowledge:
        load_knowledge(api)

    # Step 6: Upload solar system queries
    upload_queries(api, "solar-system", "solar-system-queries.json", "SPARQL")
    upload_queries(
        api, "solar-system",
        "solar-system-graph-rag-queries.json", "GraphRAG",
    )
    upload_queries(
        api, "solar-system", "solar-system-agent-queries.json", "agent",
    )

    # Step 7: Upload stars schema, load data, and upload queries
    upload_stars_schema(api)
    if not args.skip_knowledge:
        load_stars_data(api, url, token)
    upload_queries(api, "stars", "stars-queries.json", "GraphQL")

    # Step 8: Upload tools
    upload_tools(api)

    print("\nSetup complete.")


if __name__ == "__main__":
    main()
