
# Demo data

## Solar system

Create a workspace and start the default processing flow:

```
tg-create-workspace --workspace-id solarsystem --name 'Solar system'
tg-start-flow -w solarsystem -n everything -i default -d Default
tg-show-flows -w solarsystem
```

Verify the workspace is running by sending a simple LLM prompt:

```
tg-invoke-llm -w solarsystem '' '2+2'
```

Upload the ontology definition as a config item:

```
cat datasets/solar-system/solar-system-ontology.json | \
  tg-put-config-item -w solarsystem --type ontology \
      --key solar-system-ontology --stdin
```

Load the ontology and data as knowledge graph triples:

```
tg-load-knowledge -w solarsystem -i urn:doc:solar-system \
    datasets/solar-system/solar-system-ontology.ttl \
    datasets/solar-system/solar-system-data.ttl
```

Upload SPARQL queries as config items:

```
jq -c '.[]' datasets/solar-system/solar-system-queries.json | \
  while read -r obj; \
  do \
    echo $obj; \
    id=$(echo "$obj" | jq -r '.id'); \
    echo $id; \
    echo "$obj" | jq -c 'del(.id)' | tg-put-config-item -w solarsystem --type query --key "$id" --stdin; \
  done
```

Upload GraphRAG queries as config items:

```
jq -c '.[]' datasets/solar-system/solar-system-graph-rag-queries.json | \
  while read -r obj; \
  do \
    echo $obj; \
    id=$(echo "$obj" | jq -r '.id'); \
    echo $id; \
    echo "$obj" | jq -c 'del(.id)' | tg-put-config-item -w solarsystem --type query --key "$id" --stdin; \
  done
```

Upload agent queries as config items:

```
jq -c '.[]' datasets/solar-system/solar-system-agent-queries.json | \
  while read -r obj; \
  do \
    echo $obj; \
    id=$(echo "$obj" | jq -r '.id'); \
    echo $id; \
    echo "$obj" | jq -c 'del(.id)' | tg-put-config-item -w solarsystem --type query --key "$id" --stdin; \
  done
```

## Stars

Using the solarsystem workspace

```
tg-start-flow -w solarsystem -n structured -i structured -d Structured
tg-show-flows -w solarsystem
```

Verify the workspace is running by sending a simple LLM prompt:

```
tg-invoke-llm -w solarsystem -f structured '' '2+2'
```

Upload the schema definition as a config item:

```
cat datasets/stars/stars-schema.json | \
  tg-put-config-item -w solarsystem --type schema \
      --key stars --stdin
```

Load the CSV data:

```
tg-load-structured-data -w solarsystem \
    -i datasets/stars/hyg_v42.csv --parse-only \
    --descriptor datasets/stars/stars-sdl.json

tg-load-structured-data -w solarsystem \
    -i datasets/stars/hyg_v42.csv \
    --descriptor datasets/stars/stars-sdl.json --load \
    -f structured
```

Query:

```
tg-invoke-rows-query -w solarsystem -f structured -q '
  query {
    stars(limit: 40) {
      proper spect dist mag lum con
    }
  }'
```

Upload queries as config items:

```
jq -c '.[]' datasets/stars/stars-queries.json | \
  while read -r obj; \
  do \
    echo $obj; \
    id=$(echo "$obj" | jq -r '.id'); \
    echo $id; \
    echo "$obj" | jq -c 'del(.id)' | tg-put-config-item -w solarsystem --type query --key "$id" --stdin; \
  done
```

## Tools

```
tg-put-config-item -w solarsystem --type tool --key solar-system-query \
  --stdin < solar-system-tool.json

tg-put-config-item -w solarsystem --type tool --key stars-query \
  --stdin < stars-tool.json
```
