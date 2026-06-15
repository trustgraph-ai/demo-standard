# Retail UX: Conversation Flows

## Overview

This document maps out the conversation flows that a retail AI assistant needs
to support. Each flow represents a different intent pattern with different
data requirements, reasoning steps, and graph traversal strategies.

The key insight is that superficially similar flows ("build a PC" vs "upgrade
my PC") require very different reasoning. Building from scratch is a
constraint satisfaction problem over an open set. Upgrading is a diagnosis
problem anchored to a known configuration.

---

## Flow 1: Build From Scratch

**Trigger:** "I want to build a gaming PC", "help me put together a PC for
video editing"

**What the user brings:** A goal (gaming, editing, streaming), possibly a
budget, possibly a performance target ("I want to play at 1440p").

**What the user does NOT bring:** Any existing components. The slate is blank.

### Reasoning steps

1. **Establish requirements** — What is the primary use case? What resolution
   / framerate / workload? What's the budget? Any brand preferences or
   hard constraints ("must be AMD", "needs Wi-Fi")?

2. **Anchor selection** — Pick the component that most constrains the build.
   For gaming this is typically the GPU (determines performance tier). For
   video editing it might be the CPU. The anchor narrows the search space
   for everything else.

3. **Cascading constraint satisfaction** — From the anchor, resolve
   dependencies in order:
   - GPU choice constrains: minimum PSU wattage, case clearance, PCIe slot
   - CPU choice constrains: motherboard socket, cooler socket, RAM generation
   - Motherboard constrains: RAM type/speed/slots, storage interfaces,
     form factor
   - Form factor constrains: case selection
   - Total power draw constrains: PSU wattage
   - Budget remaining constrains: what tier is available for each slot

4. **Validate the full configuration** — Check all pairwise constraints hold.
   Flag warnings (e.g. RAM speed exceeds motherboard's rated max but will
   run at reduced speed) vs hard incompatibilities (wrong socket).

5. **Present with rationale** — Show the build with per-component reasoning:
   why this GPU at this budget, why this motherboard pairs well, where the
   trade-offs are.

6. **Iterate** — User may want to swap a component ("what if I go AMD
   instead?"), which triggers re-validation of the full build.

### Key graph queries

- Components by type + performance tier + price range
- Compatibility edges: socket, power, form factor, interface
- Performance tier mapping: use case -> minimum component tiers
- "Works well with" soft recommendations (not hard constraints)

### What makes this hard

The search space is combinatorial. A naive approach checks every combination.
The assistant needs to prune early by anchoring on the most constrained
component and propagating constraints outward. Budget allocation across
components is also non-trivial — spending 60% on the GPU is right for gaming
but wrong for a workstation build.

---

## Flow 2: Upgrade an Existing System

**Trigger:** "My PC is slow, what should I upgrade?", "I bought this PC and
want to make it better for gaming"

**What the user brings:** A known (or partially known) existing configuration.
Maybe a specific model ("I have a Dell Inspiron 3020"), maybe vague ("it's
got an i5 and 16GB RAM").

**What the user does NOT bring:** A clear picture of what's bottlenecking
them, or what's compatible with what they already have.

### Reasoning steps

1. **Identify the existing configuration** — What do they have? This might
   require follow-up questions. "Which i5?" matters enormously (10th gen
   vs 13th gen = different socket, different RAM generation, different
   upgrade path). If they name a pre-built model, look up its known specs.

2. **Diagnose the bottleneck** — Given their use case and current config,
   what's the weakest link? This is reasoning over performance tiers
   relative to the workload:
   - Gaming at 1440p with an RTX 3060 and i5-10400: GPU is adequate,
     CPU is the bottleneck
   - Video editing with 8GB RAM: RAM is the bottleneck regardless of
     CPU/GPU
   - General slowness on an old HDD: storage is the bottleneck

3. **Determine upgrade constraints** — This is where it sharply diverges
   from "build from scratch". The existing system imposes hard limits:
   - Motherboard socket is fixed (unless they're replacing the board too)
   - Case size limits GPU length and cooler height
   - PSU wattage may limit GPU upgrades
   - Number of RAM slots and max supported capacity
   - Pre-built systems may have proprietary form factors or power
     connectors

4. **Propose targeted upgrades** — Rank by impact-per-dollar:
   - What gives the biggest performance lift for the least money?
   - What's the minimum upgrade that meaningfully changes the experience?
   - What's the "while you're in there" upgrade (e.g. if you're already
     opening the case to swap the GPU, adding an NVMe drive is trivial)?

5. **Validate against existing system** — Confirm the proposed upgrades are
   physically and electrically compatible with what they're keeping.

6. **Flag upgrade cliffs** — Sometimes the right answer is "your motherboard
   is the limiting factor, and upgrading the motherboard means also
   replacing CPU and RAM, at which point you're building a new system."
   The assistant needs to recognise this and be transparent about it.

### Key graph queries

- Pre-built system -> known component list (if a known model)
- Component -> socket/interface/form factor (to determine constraints)
- Component -> performance tier (to diagnose bottlenecks)
- Components compatible with [existing motherboard socket + RAM type +
  case form factor + PSU wattage]
- Upgrade path analysis: what can this system become without replacing
  the motherboard?

### What makes this hard

The reasoning is anchored to an existing, possibly under-specified system.
The user may not know their exact specs. The assistant needs to ask the right
clarifying questions without being tedious. And the answer might be "you can't
meaningfully upgrade this without replacing the core platform" — which is a
harder conversation than "here's your build."

---

## Flow 3: Gift Recommendation

**Trigger:** "I need a gift for my nephew, he's into gaming", "what's a good
present for someone who does photography?"

**What the user brings:** A recipient profile (relationship, interests, age
bracket) and usually a budget.

**What the user does NOT bring:** A specific product category in mind. The
whole point is discovery.

### Reasoning steps

1. **Profile the recipient** — Age range, interests, what they might already
   have, occasion (birthday, holiday, just because).

2. **Map interests to product categories** — "Into gaming" could mean:
   peripherals, games, streaming gear, components. "Photography" could mean:
   lenses, bags, editing software, prints. The assistant needs to explore
   the space, not jump to a single category.

3. **Filter by budget and gift-appropriateness** — A $500 GPU is a great
   product but an awkward gift unless you know their exact system. A $80
   Stream Deck is a safe, delightful gift for any streamer. Gift logic
   is different from purchase logic.

4. **Present options across categories** — Show 2-3 options from different
   categories so the buyer can react: "he'd love the headset" narrows
   the search; "he already has a good mic" eliminates a category.

5. **Iterate** — Narrow based on feedback, suggest complementary items
   ("the headset pairs well with this mic arm").

### Key graph queries

- Interest/hobby -> product category mapping
- Products by category + price range + gift suitability score
- "Popular gifts" or "highly rated" filtering
- Accessory/complement relationships for bundling

### What makes this hard

The search space is deliberately wide. The assistant needs taste and editorial
judgment, not just constraint satisfaction. "What would a 16-year-old gamer
actually want?" is a soft question that can't be resolved by graph traversal
alone — it needs curated knowledge about what's exciting vs. boring as a gift.

---

## Flow 4: Assemble a Kit / Collection

**Trigger:** "We're going camping for a week, what do we need?", "I'm setting
up a home office from scratch"

**What the user brings:** A scenario (trip type, duration, group size, location)
and possibly a budget.

**What the user does NOT bring:** A parts list. They may not even know all the
categories they need to cover.

### Reasoning steps

1. **Understand the scenario** — Where, when, how long, how many people, what
   conditions? "Car camping in Yosemite in July for 3 people" is very
   different from "backpacking the PCT solo in October."

2. **Generate a category checklist** — What categories of gear are needed?
   Sleep system, cooking, lighting, safety, comfort, navigation, clothing.
   The assistant should know the standard categories for the activity.

3. **Fill each category** — Select products that fit the scenario. A 3-person
   tent for 3 people. A 20F sleeping bag for summer (overkill but safe).
   Prioritise essentials over nice-to-haves.

4. **Cross-check the collection** — Are there gaps? Do quantities match the
   group size? Is the total within budget? Are there weight/volume
   constraints (backpacking vs car camping)?

5. **Organise and present** — Group by category with clear reasoning. Flag
   what's essential vs optional. Show per-category and total spend.

6. **Iterate** — "We already have a tent" removes that item and frees budget.
   "Can we go cheaper on the cooler?" triggers re-selection.

### Key graph queries

- Activity type -> required categories
- Category -> products ranked by suitability for scenario
- Scenario parameters (season, group size) -> product constraints
- Budget allocation across categories (essentials first)

### What makes this hard

Completeness. The assistant needs to know that you need fuel for a camp stove,
that you need a bear canister in Yosemite specifically, that 3 people need 3
sleeping bags but only 1 tent. This is domain knowledge encoded as rules
about what a complete kit looks like for a given activity.

---

## Flow 5: Compare and Decide

**Trigger:** "What's the difference between the RTX 4070 and the RX 7800 XT?",
"which of these two tents is better?"

**What the user brings:** Two or more specific products they're already
considering.

**What the user does NOT bring:** Clarity on which trade-offs matter most
to them.

### Reasoning steps

1. **Identify the products** — Resolve names to specific models. "RTX 4070"
   is unambiguous; "the ASUS motherboard" might not be.

2. **Determine comparison axes** — What matters for this product category?
   GPUs: performance, VRAM, power draw, price, driver ecosystem. Tents:
   weight, packed size, weather rating, ease of setup, durability.

3. **Present structured comparison** — Side-by-side on the relevant axes.
   Highlight meaningful differences, not noise.

4. **Ask what matters** — "Are you more concerned about VRAM for future games,
   or saving $100 now?" The assistant shouldn't just dump specs; it should
   guide toward a decision.

5. **Recommend with reasoning** — "For 1440p gaming today, they're very close.
   The 7800 XT has more VRAM which may matter in 2-3 years. The 4070 uses
   less power and has better ray tracing. If your PSU is only 650W, the
   4070 is the safer choice."

### Key graph queries

- Product -> full specification set
- Product -> performance benchmarks by use case
- Product -> compatibility requirements (for context-aware comparison)
- Product -> reviews/ratings summary

### What makes this hard

Good comparison is editorial, not mechanical. Listing specs side by side is
easy. Knowing that "12GB vs 16GB VRAM is the real differentiator here, not
the 5% benchmark difference" requires understanding what actually matters for
the user's workload.

---

## Cross-cutting Concerns

### Shared data requirements across all flows

- **Product catalog** with structured specs, not just descriptions
- **Category taxonomy** — hierarchical, multi-faceted (a headset is both
  "audio" and "gaming peripheral")
- **Compatibility graph** — typed edges between components with constraint
  semantics
- **Performance tier model** — abstract tiers that map use cases to minimum
  component requirements
- **Price and availability** — current, not stale

### Shared reasoning patterns

- **Clarification** — Knowing when to ask vs when to assume
- **Budget allocation** — Distributing spend across categories intelligently
- **Trade-off articulation** — Explaining why, not just what
- **Iterative refinement** — Gracefully handling "swap this", "remove that",
  "what if I spent more?"
- **Completeness checking** — Knowing when a build/kit is done vs missing
  something

### What the ontology needs to encode

1. **Product types and taxonomy** (Schema.org Product as base)
2. **Specification properties** with typed values and units
3. **Compatibility predicates** — hard constraints (socket match) vs soft
   (works well with)
4. **Performance tiers** — abstract levels that map to use cases
5. **Activity/scenario models** — what categories of product a given activity
   requires
6. **Configuration state** — a partially-complete build with filled and
   unfilled slots
7. **Constraint rules** — SWRL or equivalent for validation logic
