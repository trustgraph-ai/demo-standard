#!/usr/bin/env python3

"""Lists available datasets by parsing the manifest index."""

import json
import os
import sys


DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")
INDEX_FILE = os.path.join(DATASETS_DIR, "index.json")


def main():
    with open(INDEX_FILE) as f:
        index = json.load(f)

    print(f"{'ID':<20} {'Name':<30} Description")
    print(f"{'─' * 20} {'─' * 30} {'─' * 40}")
    for entry in index:
        desc = entry.get("description", "")
        print(f"{entry['id']:<20} {entry['name']:<30} {desc}")

    print()
    print(f"{len(index)} dataset(s) available.")

    if "--verbose" in sys.argv or "-v" in sys.argv:
        print()
        for entry in index:
            manifest_path = os.path.join(DATASETS_DIR, entry["path"])
            with open(manifest_path) as f:
                manifest = json.load(f)

            print(f"── {manifest['name']} ({manifest['id']}) ──")
            ws = manifest["workspace"]
            print(f"  Workspace:       {ws['id']} ({ws['name']})")

            flows = manifest.get("flows", [])
            if flows:
                flow_strs = [f"{fl['blueprint']}/{fl['id']}" for fl in flows]
                print(f"  Flows:           {', '.join(flow_strs)}")

            if manifest.get("ontology"):
                print(f"  Ontology:        {len(manifest['ontology'])} config(s)")

            knowledge = manifest.get("knowledge", [])
            if knowledge:
                file_count = sum(len(doc["files"]) for doc in knowledge)
                print(
                    f"  Knowledge:       {len(knowledge)} document(s), "
                    f"{file_count} file(s)"
                )

            if manifest.get("queries"):
                print(f"  Queries:         {len(manifest['queries'])} file(s)")

            if manifest.get("tools"):
                print(f"  Tools:           {len(manifest['tools'])} definition(s)")

            if manifest.get("prompts"):
                print(f"  Prompts:         {len(manifest['prompts'])} template(s)")

            if manifest.get("schema"):
                print(f"  Schema:          {len(manifest['schema'])} config(s)")

            if manifest.get("structured_data"):
                print(
                    f"  Structured data: "
                    f"{len(manifest['structured_data'])} load(s)"
                )

            print()


if __name__ == "__main__":
    main()
