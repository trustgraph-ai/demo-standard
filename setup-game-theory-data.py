#!/usr/bin/env python3

"""
Sets up the TrustGraph game theory demo workspace with knowledge graph
data, ontology, queries, and tools.
"""

import argparse
import json
import os

import requests
from trustgraph.api import Api, ConfigValue, Triple
import rdflib


DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")

DEFAULT_URL = os.getenv("TRUSTGRAPH_URL", "http://localhost:8888/")
DEFAULT_TOKEN = os.getenv("TRUSTGRAPH_TOKEN", None)

WORKSPACE = "gametheory"

GAME_THEORY_DIR = os.path.join(DATASETS_DIR, "game-theory")

ONTOLOGY_FILES = [
    "game-theory-ontology.ttl",
]

DATA_FILES = [
    "clacton-byelection.ttl",
]

QUERY_FILES = [
    ("game-theory-queries.json", "SPARQL"),
    ("game-theory-graph-rag-queries.json", "GraphRAG"),
    ("game-theory-agent-queries.json", "agent"),
]

TOOL_FILES = {
    "game-theory-query": "game-theory-tool.json",
}


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
                "name": "Game Theory",
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


def load_triples_from_file(path):
    g = rdflib.Graph()
    g.parse(path, format="turtle")
    for s, p, o in g:
        kwargs = {"s": str(s), "p": str(p), "o": str(o)}
        if isinstance(o, rdflib.term.Literal):
            if o.language:
                kwargs["o_language"] = str(o.language)
            elif o.datatype:
                kwargs["o_datatype"] = str(o.datatype)
        yield Triple(**kwargs)


def load_entity_contexts_from_file(path):
    g = rdflib.Graph()
    g.parse(path, format="turtle")
    for s, p, o in g:
        if isinstance(o, rdflib.term.URIRef):
            continue
        yield {"entity": {"t": "i", "i": str(s)}, "context": str(o)}


def load_knowledge(api, flow="default"):
    print("Loading knowledge graph triples and entity contexts...")

    all_files = ONTOLOGY_FILES + DATA_FILES
    document_id = "urn:doc:game-theory"
    collection = "default"

    bulk = api.bulk()

    for filename in all_files:
        path = os.path.join(GAME_THEORY_DIR, filename)
        print(f"  Loading triples from {filename}...")
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

    for filename in all_files:
        path = os.path.join(GAME_THEORY_DIR, filename)
        print(f"  Loading entity contexts from {filename}...")
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


def upload_queries(api):
    for filename, label in QUERY_FILES:
        print(f"Uploading {label} queries...")
        path = os.path.join(GAME_THEORY_DIR, filename)
        with open(path) as f:
            queries = json.load(f)
        for obj in queries:
            qid = obj.pop("id")
            put_config(api, "query", qid, json.dumps(obj))
        print(f"  {len(queries)} {label} queries uploaded.")


def upload_tools(api):
    print("Uploading tool definitions...")
    for key, filename in TOOL_FILES.items():
        path = os.path.join(GAME_THEORY_DIR, filename)
        with open(path) as f:
            value = f.read()
        put_config(api, "tool", key, value)
    print(f"  {len(TOOL_FILES)} tools uploaded.")


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

    if not args.skip_workspace:
        create_workspace(url, token)

    api = Api(url, token=token, workspace=WORKSPACE)

    if not args.skip_flows:
        start_flow(api, "everything", "default", "Default")

    if not args.skip_verify:
        verify_llm(api, "default")

    if not args.skip_knowledge:
        load_knowledge(api)

    upload_queries(api)
    upload_tools(api)

    print("\nSetup complete.")


if __name__ == "__main__":
    main()
