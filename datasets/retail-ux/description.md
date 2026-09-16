# Retail UX

Experience an AI-powered shopping assistant that understands product
compatibility, user intent, and the full decision journey. This dataset
combines a detailed product catalogue with a behavioural interaction
model, enabling intelligent product recommendations and conversation
analysis.

## Product catalogue

Over 150 products across three domains:

- **PC components** — CPUs, GPUs, motherboards, RAM, storage, PSUs,
  cases, and coolers from AMD, Intel, NVIDIA, ASUS, MSI, Corsair, and
  more. Every component carries detailed specifications, compatibility
  data, and performance tier ratings.

- **Electronics and peripherals** — monitors, headsets, keyboards, mice,
  stream decks, webcams, microphones, and speakers for gaming, streaming,
  and content creation setups.

- **Outdoor and camping gear** — tents, sleeping bags, stoves, coolers,
  chairs, first-aid kits, and consumables organised into activity-based
  collections.

## What you can explore

- **Compatibility checking** — products are linked through shared
  specification nodes (CPU sockets, RAM types, form factors, storage
  interfaces). Ask whether components fit together and the system
  traces compatibility through the graph rather than matching strings.

- **Guided PC builds** — walk through a build from CPU selection through
  to case and cooler, with hard constraints (socket match, form factor
  fit, PSU wattage) and soft warnings (RAM speed downclocking,
  bottleneck detection).

- **Shopping conversations** — three specialised assistant prompts handle
  different scenarios: a PC build assistant that guides component
  selection, a checkout assistant that suggests cross-sells, and a
  general shopping assistant that routes to the right flow.

- **User journey analysis** — the interaction ontology captures the full
  decision arc: what users searched for, what they compared, where they
  hesitated, what objections they raised (price, compatibility,
  complexity, trust, timing, need, risk), and how those objections
  were resolved.

- **Behavioural signals** — every interaction event can carry signal
  data revealing user priorities, confidence levels, budget constraints,
  and external influences. A product view is just a view, but a product
  view where the user focuses on VRAM is also a priority signal.

- **Activity-based recommendations** — activities like "Gaming PC" or
  "Camping Trip" define category requirements with priorities
  (essential, recommended, optional), guiding kit assembly.

## What kinds of questions work well

- "Build me a gaming PC for around $1500"
- "Is this motherboard compatible with the Ryzen 7 7800X3D?"
- "Compare the RTX 4070 and RX 7800 XT for 1440p gaming"
- "What camping gear do I need for a weekend trip?"
- "Show me gift-suitable products under $100"
- "Why did user-001 choose the RTX 4070 over the alternative?"
- "What objections came up in abandoned journeys vs completed ones?"

## Features

- Two interconnected knowledge graphs: retail products and user
  interactions
- Compatibility checking via graph traversal through specification nodes
- Hard and soft constraint system for build validation
- Three specialised assistant prompts for different shopping scenarios
- 56 pre-built queries across standard, Graph RAG, and agent modes
- Sample user journeys with full behavioural signal data
