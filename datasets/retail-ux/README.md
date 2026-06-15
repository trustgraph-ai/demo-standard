# Retail UX Dataset

Dataset for an AI-driven retail shopping assistant. Provides an OWL ontology,
reference vocabulary, and product catalog covering PC components, electronics,
and outdoor gear. Designed to support conversational flows where an AI helps
customers build compatible systems, upgrade existing equipment, assemble
activity kits, find gifts, and compare products.

## Files

### Ontology

| File | Description |
|------|-------------|
| `retail-ontology.ttl` | Pure OWL ontology — classes and properties only. Load into the ontology endpoint separately from instance data. |

### Instance data

| File | Description |
|------|-------------|
| `retail-vocabulary.ttl` | Reference data: specification values (socket types, RAM types, form factors, storage interfaces, performance tiers, efficiency ratings), product categories, activity templates, and compatibility constraints (hard and soft). |
| `retail-products-pc.ttl` | 14 PC components (2 CPUs, 2 GPUs, 2 motherboards, 2 RAM kits, 2 SSDs, 2 PSUs, 2 cases) plus brand entities. |
| `retail-products-electronics.ttl` | 5 electronics accessories (stream deck, headset, chest mount, microphone, webcam) plus brand entities. |
| `retail-products-camping.ttl` | 12 outdoor gear items (3 sleep, 4 cooking/food, 3 lighting/safety, 2 comfort) plus brand entities. Includes one consumable (propane fuel). |

### Design documents

| File | Description |
|------|-------------|
| `flows.md` | Conversation flow specifications for the five supported user journeys: build from scratch, upgrade existing, gift recommendation, kit assembly, and compare-and-decide. |
| `ontology-design.md` | Ontology design rationale covering class hierarchy, property design, constraint model, and how each flow traverses the graph. |

## Namespaces

| Prefix | URI | Purpose |
|--------|-----|---------|
| `rt:` | `http://trustgraph.ai/ontology/retail#` | Ontology classes, properties, and vocabulary individuals |
| `p:` | `http://trustgraph.ai/data/retail/product/` | Product instances |
| `b:` | `http://trustgraph.ai/data/retail/brand/` | Brand instances |
| `schema:` | `https://schema.org/` | Schema.org base vocabulary |

## Key design decisions

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

## Product summary

| Category | Count | Types |
|----------|-------|-------|
| PC components | 14 | CPU, GPU, Motherboard, RAM, Storage, PSU, Case |
| Electronics | 5 | Streaming tools, audio, video |
| Outdoor gear | 12 | Sleep system, cooking, lighting/safety, comfort |
| **Total** | **31** | |

## Triple counts

| File | Triples |
|------|---------|
| `retail-ontology.ttl` | 494 |
| `retail-vocabulary.ttl` | 228 |
| `retail-products-pc.ttl` | 349 |
| `retail-products-electronics.ttl` | 111 |
| `retail-products-camping.ttl` | 214 |
| **Total** | **1,396** |
