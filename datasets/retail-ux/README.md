# Retail UX Dataset

Dataset for an AI-driven retail shopping assistant. Comprises two
complementary ontologies:

1. **Retail product ontology** — models products, specifications,
   compatibility constraints, and configuration workflows.
2. **Interaction ontology** — models user journeys, decision events, and
   the behavioural signals that reveal why users buy, hesitate, or abandon.

The retail ontology is the terrain (what's being sold and how things fit
together). The interaction ontology is the map of how people move through
it (what they did, what they revealed, and what caused them to convert or
not).

## Files

### Ontologies (load into ontology endpoint)

| File | Description |
|------|-------------|
| `retail-ontology.ttl` | Retail product ontology — classes and properties for products, specifications, compatibility constraints, configurations, activities, and categories. Pure OWL, no instances. |
| `interaction-ontology.ttl` | Interaction and journey ontology — classes and properties for actors, sessions, journeys, interaction events, and signal events. Uses a mixin pattern where any interaction event can simultaneously carry signal types via OWL multiple typing. Pure OWL, no instances. |

### Instance data (load into data endpoint)

| File | Description |
|------|-------------|
| `retail-vocabulary.ttl` | Retail reference data: specification values (socket types, RAM types, form factors, storage interfaces, performance tiers, efficiency ratings), product categories, activity templates, and compatibility constraints (hard and soft). |
| `retail-products-pc.ttl` | 14 PC components (2 CPUs, 2 GPUs, 2 motherboards, 2 RAM kits, 2 SSDs, 2 PSUs, 2 cases) plus brand entities. |
| `retail-products-electronics.ttl` | 5 electronics accessories (stream deck, headset, chest mount, microphone, webcam) plus brand entities. |
| `retail-products-camping.ttl` | 12 outdoor gear items (3 sleep, 4 cooking/food, 3 lighting/safety, 2 comfort) plus brand entities. Includes one consumable (propane fuel). |
| `interaction-vocabulary.ttl` | Interaction reference data: 7 objection category individuals (price, trust, compatibility, complexity, timing, need, risk). |
| `interaction-sample-data.ttl` | 3 sample user journeys with 45 events demonstrating the full event and signal model. |

### Design documents

| File | Description |
|------|-------------|
| `flows.md` | Conversation flow specifications for the five supported user journeys: build from scratch, upgrade existing, gift recommendation, kit assembly, and compare-and-decide. |
| `ontology-design.md` | Retail ontology design rationale covering class hierarchy, property design, constraint model, and how each flow traverses the graph. |
| `interaction-ontology-design.md` | Interaction ontology design rationale covering the mixin pattern, event and signal class hierarchies, property design, and example journey event sequences. |

### Query templates

| File | Queries | Description |
|------|---------|-------------|
| `retail-queries.json` | 14 | SPARQL queries for the retail product ontology — product listing, category filtering, compatibility checks (socket, RAM, GPU clearance, PSU wattage), bottleneck detection, sales, gift filtering, product relationships, full build combinations, constraint catalog. |
| `interaction-queries.json` | 12 | SPARQL queries for the interaction ontology — journey listing, event sequences, objection analysis, decision points, budget signals, recommendation effectiveness, priority signals, conversion funnel, objection resolution rates, spend breakdown, trigger types, mixin pattern demonstration. |
| `retail-agent-queries.json` | 10 | Natural language agent test queries for retail — budget PC build, GPU selection, motherboard compatibility, case fit, PSU sizing, gift recommendation, camping essentials, bottleneck check, sale items, upgrade path. |
| `retail-graph-rag-queries.json` | 6 | Graph-RAG queries for retail — compatibility model explanation, GPU comparison, catalog overview, constraint system, outdoor gear summary, product relationships. |
| `interaction-agent-queries.json` | 6 | Natural language agent test queries for interaction — journey trace, objection patterns, abandoned vs completed, recommendation impact, budget influence, upgrade journey signals. |
| `interaction-graph-rag-queries.json` | 6 | Graph-RAG queries for interaction — journey model explanation, mixin pattern, objection categories, journey summaries, signal types, cross-ontology linking. |

### Tool definitions

| File | Description |
|------|-------------|
| `retail-tool.json` | Tool definition for querying the retail product knowledge base — products, specifications, compatibility, pricing, and kit assembly. |
| `interaction-tool.json` | Tool definition for querying the interaction journey knowledge base — user journeys, decision events, objections, behavioural signals, and conversion analysis. |

## Namespaces

### Retail ontology

| Prefix | URI | Purpose |
|--------|-----|---------|
| `rt:` | `http://trustgraph.ai/ontology/retail#` | Retail classes, properties, and vocabulary individuals |
| `p:` | `http://trustgraph.ai/data/retail/product/` | Product instances |
| `b:` | `http://trustgraph.ai/data/retail/brand/` | Brand instances |
| `schema:` | `https://schema.org/` | Schema.org base vocabulary |

### Interaction ontology

| Prefix | URI | Purpose |
|--------|-----|---------|
| `ix:` | `http://trustgraph.ai/ontology/interaction#` | Interaction classes, properties, and vocabulary individuals |
| `actor:` | `http://trustgraph.ai/data/interaction/actor/` | User/actor instances |
| `j:` | `http://trustgraph.ai/data/interaction/journey/` | Journey instances |
| `sess:` | `http://trustgraph.ai/data/interaction/session/` | Session instances |
| `ev:` | `http://trustgraph.ai/data/interaction/event/` | Event instances |
| `sig:` | `http://trustgraph.ai/data/interaction/signal/` | Standalone signal instances |

## Key design decisions

### Retail ontology

**Specifications are first-class graph nodes.** A CPU socket type like `rt:AM5`
is a named entity that both CPUs and motherboards link to. Compatibility
checking is a graph traversal through shared specification nodes, not a string
comparison on attribute values.

**Hard vs soft constraints are distinct.** Hard constraints (e.g. socket
mismatch) block a build. Soft constraints (e.g. RAM speed exceeding
motherboard maximum) produce warnings. Both are encoded as named individuals
with rule expressions and user-facing messages.

**Products extend Schema.org.** The `rt:Product` class is a subclass of
`schema:Product`, so product data is interoperable with Schema.org tooling
while carrying the additional specification and compatibility semantics
needed for AI-driven configuration.

**Activity templates drive kit assembly.** Activities like `rt:GamingPCBuild`
and `rt:CampingTrip` define which product categories are required and at what
priority, providing the AI with a completeness checklist for any given
scenario.

### Interaction ontology

**Two orthogonal dimensions on every event.** Interaction events describe
*what happened* (searched, viewed, added to cart). Signal events describe
*what it reveals* (objection, priority, decision). A single event can carry
types from both hierarchies via OWL multiple typing — the mixin pattern.

**The journey is the spine.** A time-ordered sequence of interaction events
within a session provides the structural backbone. Signals are annotations
on that spine, not a parallel structure.

**Not every event carries signal.** A routine product view is just a
`ProductViewed`. A product view where the user focuses on VRAM is also a
`PrioritySignal`. The ontology does not force analytical meaning onto
mundane events.

**Objection categories predict outcomes.** Seven objection types (price,
trust, compatibility, complexity, timing, need, risk) classify why users
hesitate or reject. Tracking resolution status reveals which objections
the assistant can overcome and which lead to abandonment.

**The two ontologies link but do not merge.** The interaction ontology
references retail types (`rt:Product`, `rt:ProductCategory`,
`rt:Configuration`, `rt:CompatibilityConstraint`) but does not subclass or
modify them. Queries can traverse both graphs.

## Product summary

| Category | Count | Types |
|----------|-------|-------|
| PC components | 14 | CPU, GPU, Motherboard, RAM, Storage, PSU, Case |
| Electronics | 5 | Streaming tools, audio, video |
| Outdoor gear | 12 | Sleep system, cooking, lighting/safety, comfort |
| **Total** | **31** | |

## Sample journey summary

| Journey | Actor | Events | Outcome | Key signals |
|---------|-------|--------|---------|-------------|
| 1440p Gaming PC Build | user-001 (first-time builder) | 17 | Purchase ($1,644) | Budget preference, VRAM priority, GPU decision point, high confidence batch add |
| PC Upgrade | user-002 (upgrader) | 17 + 1 signal | Purchase ($500) | Problem trigger, compatibility objection, upgrade cliff, complexity/price objection, downscaled purchase |
| Gift for Nephew | user-003 (gift buyer) | 11 | Purchase ($80) | Occasion trigger, hard budget, risk objection resolved by reassurance, fast confident decision |

## Triple counts

| File | Triples |
|------|---------|
| `retail-ontology.ttl` | 494 |
| `retail-vocabulary.ttl` | 390 |
| `retail-products-pc.ttl` | 349 |
| `retail-products-electronics.ttl` | 111 |
| `retail-products-camping.ttl` | 214 |
| `interaction-ontology.ttl` | 456 |
| `interaction-vocabulary.ttl` | 21 |
| `interaction-sample-data.ttl` | 660 |
| **Total** | **2,695** |
