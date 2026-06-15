# Retail UX Ontology Design

## Design Principles

- **Schema.org as base vocabulary** where it fits — Product, Offer, Brand.
  Extend rather than reinvent.
- **Separate the product catalog from the compatibility model.** Products
  have specs. Compatibility is a relationship between specs, not between
  products directly.
- **Specs are first-class entities, not just key-value pairs.** A CPU socket
  is a named thing in the graph that both CPUs and motherboards link to.
  This is what makes constraint propagation work — you traverse the graph
  through shared spec nodes rather than string-matching attribute values.
- **Soft vs hard constraints are distinct edge types.** "Requires AM5 socket"
  is a hard constraint. "Works well with" is a soft recommendation. The
  ontology must distinguish these so the AI can tell the user which
  trade-offs are negotiable.
- **Activity models are separate from products.** A camping trip is not a
  product — it's a template that defines what categories of product are
  needed. This keeps the ontology general: the same product catalog serves
  gift-finding, kit-building, and comparison flows.

## Namespace

```
@prefix rt:   <http://trustgraph.ai/ontology/retail#> .
@prefix schema: <https://schema.org/> .
```

We extend Schema.org rather than importing it wholesale. The `rt:` namespace
covers everything specific to our compatibility and configuration model.

---

## Class Hierarchy

### Products

```
schema:Product
  rt:Component              — a product that fills a slot in a configuration
    rt:CPU
    rt:GPU
    rt:Motherboard
    rt:RAM
    rt:Storage
    rt:PSU
    rt:Case
    rt:Cooling
  rt:Accessory              — a product that complements but isn't required
  rt:Consumable             — a product that gets used up (fuel, batteries)
  rt:GearItem               — a standalone product for kit/collection use
```

Products inherit schema:Product properties (name, description, brand, image,
offers). The subclasses under rt:Component carry compatibility semantics.
rt:GearItem, rt:Accessory and rt:Consumable do not — they participate in
collections but not in constraint satisfaction.

### Specifications (the shared constraint nodes)

```
rt:Specification            — abstract base for all spec values
  rt:SocketType             — e.g. AM5, LGA1700
  rt:RAMType                — e.g. DDR4, DDR5
  rt:FormFactor             — e.g. ATX, mATX, ITX
  rt:StorageInterface       — e.g. NVMe, SATA
  rt:PerformanceTier        — e.g. entry, mid, high, enthusiast
```

These are **named individuals**, not free-text values. A socket type is an
entity in the graph:

```
rt:AM5 a rt:SocketType ; rdfs:label "AM5" .
```

Both a CPU and a motherboard link to the same `rt:AM5` node. Compatibility
is then a graph traversal: "find motherboards that share a socket node with
this CPU."

### Configuration

```
rt:Configuration            — a partially or fully defined build
  rt:PCBuild                — a PC configuration with component slots
  rt:Collection             — a kit/collection grouped by category

rt:Slot                     — an unfilled position in a configuration
rt:FilledSlot               — a slot with a product assigned
```

A configuration is a first-class entity that tracks state as the user builds
it. Slots represent the positions to fill (CPU slot, GPU slot, etc. for a PC;
sleep system, cooking, safety etc. for a camping kit).

### Activities and Scenarios

```
rt:Activity                 — a use case that drives product selection
  rt:GamingPC
  rt:WorkstationPC
  rt:CampingTrip
  rt:HomeOffice

rt:CategoryRequirement      — a category that an activity needs filled
```

An activity has a set of category requirements. A camping trip requires
sleep, cooking, lighting, safety. A gaming PC requires CPU, GPU, motherboard,
RAM, storage, PSU, case. This is the template that the "assemble a kit" flow
uses.

---

## Property Design

### Product properties (extending Schema.org)

```
# Inherited from schema:Product
schema:name                 xsd:string
schema:description          xsd:string
schema:brand                -> schema:Brand
schema:offers               -> schema:Offer (with schema:price, schema:priceCurrency)
schema:image                xsd:anyURI

# Our extensions
rt:category                 -> rt:ProductCategory
rt:subcategory              -> rt:ProductCategory
rt:rating                   xsd:decimal
rt:reviewCount              xsd:integer
rt:inStock                  xsd:boolean
rt:stockCount               xsd:integer
rt:tags                     xsd:string          (multi-valued)
```

### Compatibility properties (the core of the model)

```
# Hard constraints — these must match or the build is invalid
rt:hasSocket                -> rt:SocketType       (domain: CPU, Motherboard, Cooling)
rt:hasRAMType               -> rt:RAMType          (domain: Motherboard, RAM)
rt:hasFormFactor            -> rt:FormFactor        (domain: Motherboard, Case)
rt:hasStorageInterface      -> rt:StorageInterface  (domain: Storage, Motherboard)

# Numeric constraints — validated by rules
rt:powerDraw                xsd:integer            (watts, domain: CPU, GPU)
rt:psuWattage               xsd:integer            (watts, domain: PSU)
rt:maxGPULength             xsd:integer            (mm, domain: Case)
rt:gpuLength                xsd:integer            (mm, domain: GPU)
rt:maxRAMSlots              xsd:integer            (domain: Motherboard)
rt:maxRAMSpeed              xsd:integer            (MHz, domain: Motherboard)
rt:ramSpeed                 xsd:integer            (MHz, domain: RAM)
rt:ramModules               xsd:integer            (domain: RAM — sticks in the kit)

# Performance properties
rt:performanceTier          -> rt:PerformanceTier   (domain: Component)
rt:performanceScore         xsd:integer             (domain: Component — for bottleneck analysis)
```

### Relationship properties

```
# Soft relationships (recommendations, not constraints)
rt:worksWellWith            -> schema:Product       (symmetric)
rt:similarTo                -> schema:Product       (symmetric)
rt:alternativeTo            -> schema:Product       (symmetric)
rt:isAccessoryFor           -> schema:Product
rt:upgradeFrom              -> schema:Product       (domain: Component — "replaces this in an upgrade path")

# Configuration relationships
rt:hasSlot                  -> rt:Slot              (domain: Configuration)
rt:slotType                 xsd:string              (domain: Slot — "cpu", "gpu", etc.)
rt:filledBy                 -> schema:Product       (domain: Slot)
rt:forActivity              -> rt:Activity          (domain: Configuration)
rt:budget                   xsd:decimal             (domain: Configuration)
```

### Activity and scenario properties

```
rt:requiresCategory         -> rt:ProductCategory   (domain: Activity)
rt:categoryPriority         xsd:string              (domain: CategoryRequirement — "essential" | "recommended" | "optional")
rt:scenarioSeason           xsd:string              (domain: Activity)
rt:scenarioGroupSize        xsd:integer             (domain: Activity)
rt:scenarioLocation         xsd:string              (domain: Activity)
```

---

## Constraint Rules

These express the validation logic currently hardcoded in the demo's
`buildCompatibility.ts`. In the ontology they would be SWRL rules or
equivalent; here they're expressed as natural-language specifications
for the rule set.

### Hard constraints (build is invalid if violated)

| Rule | Condition |
|------|-----------|
| Socket match | CPU.hasSocket = Motherboard.hasSocket |
| RAM type match | RAM.hasRAMType = Motherboard.hasRAMType |
| Form factor fit | Motherboard.hasFormFactor in Case.supportedFormFactors |
| Storage interface | Storage.hasStorageInterface in Motherboard.supportedStorageInterfaces |
| GPU clearance | GPU.gpuLength <= Case.maxGPULength |
| PSU capacity | sum(Component.powerDraw) <= PSU.psuWattage |
| RAM slot count | RAM.ramModules <= Motherboard.maxRAMSlots |

### Soft constraints (warnings, not blockers)

| Rule | Condition |
|------|-----------|
| RAM speed cap | RAM.ramSpeed > Motherboard.maxRAMSpeed -> warning: will downclock |
| PSU headroom | sum(Component.powerDraw) > PSU.psuWattage * 0.8 -> warning: low headroom |
| Bottleneck | abs(CPU.performanceScore - GPU.performanceScore) > threshold -> warning: bottleneck |
| PSU for GPU | GPU.minPSU > PSU.psuWattage -> warning (some GPUs specify a minimum) |

### Upgrade-specific rules

| Rule | Condition |
|------|-----------|
| Socket lock-in | existing Motherboard.hasSocket constrains CPU upgrade candidates |
| RAM gen lock-in | existing Motherboard.hasRAMType constrains RAM upgrade candidates |
| PSU budget | new GPU.powerDraw + existing other.powerDraw <= existing PSU.psuWattage |
| Upgrade cliff | if bottleneck requires motherboard swap, flag that CPU + RAM must also change |

---

## How the Flows Use the Ontology

| Flow | Primary traversal pattern |
|------|--------------------------|
| **Build from scratch** | Activity -> required slots -> candidates per slot filtered by budget and tier -> constraint validation across all filled slots |
| **Upgrade existing** | Existing config -> identify fixed specs (socket, form factor, PSU) -> find candidates compatible with fixed specs -> diagnose bottleneck via performance scores |
| **Gift recommendation** | Interest tags -> product categories -> products filtered by price + rating + gift suitability |
| **Kit assembly** | Activity + scenario params -> required categories with priorities -> products per category filtered by scenario constraints (season, group size) -> completeness check |
| **Compare and decide** | Two or more products -> shared spec properties -> structured diff -> contextual recommendation based on user's stated priorities |

---

## What Schema.org Gives Us for Free

| Schema.org type/property | What we use it for |
|---|---|
| `schema:Product` | Base class for all products |
| `schema:Offer` / `schema:price` | Pricing, availability |
| `schema:Brand` | Brand entities |
| `schema:isAccessoryOrSparePartFor` | Accessory relationships (maps to our rt:isAccessoryFor) |
| `schema:isSimilarTo` | Similar product relationships |
| `schema:additionalProperty` | Fallback for specs we haven't formally modelled |
| `schema:image` | Product images |
| `schema:Review` / `schema:aggregateRating` | Ratings and reviews |

## What We Add

| Our addition | Why Schema.org doesn't cover it |
|---|---|
| `rt:Specification` class hierarchy | Schema.org has no typed spec values — it's all strings in additionalProperty |
| `rt:hasSocket`, `rt:hasRAMType`, etc. | No compatibility predicates in Schema.org |
| `rt:Configuration` / `rt:Slot` | No concept of partial product assembly |
| `rt:Activity` / `rt:CategoryRequirement` | No activity-driven product selection |
| `rt:performanceTier` / `rt:performanceScore` | No performance modelling |
| Constraint rules | Schema.org is descriptive, not prescriptive — it doesn't validate |

---

## Next Steps

1. **Write the ontology in Turtle** — classes, properties, named individuals
   for spec values (socket types, RAM types, form factors, performance tiers)
2. **Populate with product data** — the 31 products from the demo, encoded
   as graph entities with typed spec links
3. **Write the constraint rules** — SWRL or as a separate rules document
   that the AI can reference
4. **Write query templates** — the graph queries each flow needs
5. **Write agent tool definitions** — the tools the AI uses to search
   products, validate builds, and manage configurations
