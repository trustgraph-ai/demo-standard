# Interaction Ontology Design

## Purpose

This ontology captures the user's journey through a retail AI assistant
interaction and the behavioural signals that emerge from it. While the
retail product ontology models what's being sold and how things fit
together, this ontology models what the user *did*, what they *revealed*,
and what *caused* them to buy, not buy, hesitate, or change course.

The key insight is that an AI-driven conversational retail experience
generates far richer signal than traditional e-commerce clickstream data.
Between "viewed product" and "added to cart", there is a dialogue where
the user asked questions, raised concerns, expressed preferences, and
received explanations. That dialogue is where the decision actually
happened.

## Design Principles

- **Two orthogonal dimensions on every event.** Journey events describe
  *what happened* (searched, viewed, added to cart). Signal events describe
  *what it reveals* (objection, priority, decision). A single event can be
  both, using OWL multiple typing as a natural mixin pattern.
- **The journey is the spine.** A time-ordered sequence of interaction
  events within a session provides the structural backbone. Signals are
  annotations on that spine, not a parallel structure.
- **Not every event carries signal.** A routine product view may reveal
  nothing. A product view where the user says "oh, that has way more VRAM"
  is also a priority signal. The ontology does not force analytical meaning
  onto mundane events.
- **Not every signal maps to one event.** A priority might emerge gradually
  across several interactions. A signal event can link to multiple
  interaction events when the insight spans a sequence.
- **References the retail ontology, does not duplicate it.** Products,
  categories, specifications, and configurations are in the `rt:` namespace.
  This ontology links to them but does not redefine them.

## Namespace

```
@prefix ix: <http://trustgraph.ai/ontology/interaction#> .
@prefix rt: <http://trustgraph.ai/ontology/retail#> .
```

---

## Class Hierarchy

### Core structural classes

```
ix:Session
ix:Journey
ix:Actor
```

A **Session** is a single continuous interaction between a user and the
assistant. It has a start time, an end time (if completed), and a sequence
of events. A session belongs to an **Actor** (the user — anonymised or
identified depending on context).

A **Journey** is a higher-level grouping that spans one or more sessions.
A user might start researching a PC build in one session, come back a day
later to continue, and complete the purchase in a third session. The
journey ties these together into a coherent decision arc.

### Interaction events (what happened)

These describe observable actions in the funnel. They form a time-ordered
sequence within a session.

```
ix:InteractionEvent
  ix:SessionStarted
  ix:Search
  ix:ResultsViewed
  ix:ProductViewed
  ix:ComparisonViewed
  ix:RecommendationReceived
  ix:QuestionAsked
  ix:AnswerReceived
  ix:AddedToCart
  ix:RemovedFromCart
  ix:ComponentSwapped
  ix:BuildValidated
  ix:CollectionReviewed
  ix:CheckoutStarted
  ix:CheckoutCompleted
  ix:SessionEnded
```

**SessionStarted** — The user begins interacting. May carry an initial
intent if the user states one immediately ("I want to build a gaming PC")
or may be intentless (browsing).

**Search** — The user searches or describes what they want. Captures the
query text and any interpreted intent. In a conversational UI this might
be a natural language request rather than a keyword search.

**ResultsViewed** — The assistant presents a set of products or options.
Captures which products were shown and in what order. The gap between what
was shown and what was engaged with is itself a signal.

**ProductViewed** — The user examines a specific product in detail. Captures
which product, how long they spent (dwell time), and what they looked at
(specs, reviews, price, images).

**ComparisonViewed** — The user views two or more products side by side.
Captures the product set and which comparison axes were visible.

**RecommendationReceived** — The assistant proactively suggests a product
or set of products. Captures what was recommended, the stated reasoning,
and which flow triggered it (build suggestion, gift idea, upgrade path).

**QuestionAsked** — The user asks a question during the conversation.
Captures the question text, what it was about (a product, a spec, a
compatibility concern, a general topic), and where in the journey it
occurred. Questions reveal uncertainty and priorities.

**AnswerReceived** — The assistant answers a user question. Captures the
answer content and whether the user's subsequent behaviour suggests the
answer was satisfying (they proceeded) or unsatisfying (they asked again,
changed direction, or abandoned).

**AddedToCart** — The user adds a product to their cart or build. A
commitment signal, though tentative — items can be removed.

**RemovedFromCart** — The user removes a product from their cart or build.
Often an objection signal. May include a stated reason.

**ComponentSwapped** — The user replaces one component with another in a
build. Captures what was removed, what replaced it, and any stated
reasoning. A swap is richer than a remove-then-add because it reveals
a direct preference.

**BuildValidated** — A PC build or configuration is checked for
compatibility. Captures whether it passed or failed, which constraints
were violated, and what the user did next (fixed it, ignored the warning,
abandoned the build).

**CollectionReviewed** — A kit or collection is reviewed for completeness.
Captures which categories were filled, which were missing, and whether
the user addressed the gaps.

**CheckoutStarted** — The user begins the purchase flow. A strong intent
signal.

**CheckoutCompleted** — The purchase is finalised. Captures what was bought,
total spend, and the journey that led here.

**SessionEnded** — The session concludes. May be a natural ending (purchase
complete, user says goodbye) or an abandonment (user stops responding).

### Signal events (what it reveals)

These describe the behavioural or cognitive meaning of what happened.
They can be mixed into interaction events via multiple typing, or stand
alone when the signal emerges from a pattern across events rather than a
single moment.

```
ix:SignalEvent
  ix:DecisionPoint
  ix:Objection
  ix:PrioritySignal
  ix:ConfidenceSignal
  ix:TriggerEvent
  ix:AbandonmentSignal
  ix:SatisfactionSignal
  ix:BudgetSignal
  ix:InfluenceSignal
```

**DecisionPoint** — The user chose between alternatives. Captures the
options considered, what was selected, what was rejected, and any stated
or inferred reasoning. This is the core analytical event — it reveals
preferences in context.

**Objection** — The user expressed a concern or rejection. Captures what
was objected to, the nature of the objection (price, trust, compatibility,
complexity, timing), and whether it was resolved. An objection that gets
resolved is a buying signal. An objection that persists leads to
abandonment or substitution.

**PrioritySignal** — The user revealed what matters to them, explicitly
("I care about noise levels") or implicitly (they asked about VRAM before
asking about price, suggesting performance matters more than cost). Captures
the priority dimension and the strength of the signal.

**ConfidenceSignal** — The user signalled their confidence level in the
decision. High confidence: "yes, add that". Low confidence: "I'm not sure",
"what do you think?", "is that good enough?". Captures whether the user
needs reassurance, more information, or social proof.

**TriggerEvent** — What brought the user here in the first place. "My PC
is slow", "birthday next week", "saw a deal on Reddit", "just curious".
Captures the initiating motivation, which colours the entire journey.
Often surfaces in the first few exchanges.

**AbandonmentSignal** — Indicators that the user is disengaging. Long
pauses, topic changes, declining suggestions, "I'll think about it".
Captures where in the funnel the signal appeared and what preceded it.

**SatisfactionSignal** — Positive indicators: "that's perfect", "exactly
what I needed", accepting a recommendation without further questions.
Captures what satisfied them and at what point in the journey.

**BudgetSignal** — The user revealed budget sensitivity, either by stating
a budget explicitly, reacting to prices ("that's more than I wanted to
spend"), or consistently choosing cheaper options. Captures the budget
level and whether it's a hard constraint or a preference.

**InfluenceSignal** — The user referenced an external influence on their
decision: a review, a friend's recommendation, a YouTube video, a brand
reputation. Captures the influence source and how it affected the decision.

---

## The Mixin Pattern

Any single event instance can carry both interaction and signal types:

```turtle
ex:event-47 a ix:RemovedFromCart, ix:Objection ;
    ix:inSession ex:session-12 ;
    ix:timestamp "2026-06-15T14:23:07Z"^^xsd:dateTime ;
    ix:sequenceIndex 12 ;
    ix:involvedProduct p:nvidia-rtx-4070 ;
    ix:statedReason "too expensive for what I need" ;
    ix:objectionType ix:PriceObjection ;
    ix:revealedPriority ix:PriceSensitivity .
```

This event is simultaneously:
- A journey step (RemovedFromCart — something happened in the funnel)
- A signal (Objection — they rejected something and said why)

The mixin works because InteractionEvent and SignalEvent are independent
class trees with no disjointness axiom. OWL allows an individual to be
an instance of classes from both hierarchies.

### When signals don't align to a single event

Sometimes a priority emerges across several interactions. For example,
the user asks about noise levels on three different products. No single
question is the signal — the pattern is. In this case, the signal event
exists independently and links to multiple interaction events:

```turtle
ex:signal-8 a ix:PrioritySignal ;
    ix:derivedFrom ex:event-23, ex:event-31, ex:event-38 ;
    ix:priorityDimension ix:NoiseLevels ;
    ix:signalStrength "strong" .
```

---

## Property Design

### Session and journey properties

```
ix:hasSession        Journey -> Session
ix:belongsToJourney  Session -> Journey
ix:actor             Session -> Actor
ix:sessionStartTime  Session -> xsd:dateTime
ix:sessionEndTime    Session -> xsd:dateTime
ix:initialIntent     Session -> xsd:string
ix:sessionOutcome    Session -> xsd:string  ("purchase", "abandonment",
                                              "research", "return-visit")
ix:channel           Session -> xsd:string  ("web", "mobile", "in-store-kiosk")
```

### Event sequencing properties

```
ix:inSession         InteractionEvent -> Session
ix:timestamp         InteractionEvent -> xsd:dateTime
ix:sequenceIndex     InteractionEvent -> xsd:integer
ix:previousEvent     InteractionEvent -> InteractionEvent
ix:nextEvent         InteractionEvent -> InteractionEvent
ix:dwellTimeSeconds  InteractionEvent -> xsd:integer
```

Events are ordered within a session by sequenceIndex and linked as a
doubly-linked list via previousEvent/nextEvent for easy traversal.
Dwell time captures how long the user spent on a particular event before
the next one occurred.

### Event content properties (what was involved)

```
# Products and categories
ix:involvedProduct       InteractionEvent -> rt:Product
ix:involvedCategory      InteractionEvent -> rt:ProductCategory
ix:involvedConfiguration InteractionEvent -> rt:Configuration

# Search and query
ix:queryText             ix:Search -> xsd:string
ix:interpretedIntent     ix:Search -> xsd:string

# Results
ix:shownProducts         ix:ResultsViewed -> rt:Product  (multi-valued)
ix:resultCount           ix:ResultsViewed -> xsd:integer
ix:resultPosition        ix:ResultsViewed -> xsd:integer  (position of
                           the product that was subsequently engaged with)

# Recommendations
ix:recommendedProduct    ix:RecommendationReceived -> rt:Product
ix:recommendationReason  ix:RecommendationReceived -> xsd:string
ix:recommendationAccepted ix:RecommendationReceived -> xsd:boolean

# Questions and answers
ix:questionText          ix:QuestionAsked -> xsd:string
ix:questionTopic         ix:QuestionAsked -> xsd:string
ix:answerText            ix:AnswerReceived -> xsd:string
ix:answerSatisfying      ix:AnswerReceived -> xsd:boolean

# Cart and build actions
ix:addedProduct          ix:AddedToCart -> rt:Product
ix:removedProduct        ix:RemovedFromCart -> rt:Product
ix:swappedOut            ix:ComponentSwapped -> rt:Product
ix:swappedIn             ix:ComponentSwapped -> rt:Product

# Validation
ix:validationPassed      ix:BuildValidated -> xsd:boolean
ix:constraintViolated    ix:BuildValidated -> rt:CompatibilityConstraint
ix:userResponse          ix:BuildValidated -> xsd:string  ("fixed",
                           "ignored-warning", "abandoned-build", "swapped")

# Checkout
ix:purchasedProducts     ix:CheckoutCompleted -> rt:Product (multi-valued)
ix:totalSpend            ix:CheckoutCompleted -> xsd:decimal
```

### Signal properties (what it reveals)

```
# Decision points
ix:optionsConsidered     ix:DecisionPoint -> rt:Product  (multi-valued)
ix:selectedOption        ix:DecisionPoint -> rt:Product
ix:rejectedOption        ix:DecisionPoint -> rt:Product  (multi-valued)
ix:decisionReasoning     ix:DecisionPoint -> xsd:string

# Objections
ix:objectionType         ix:Objection -> ix:ObjectionCategory
ix:statedReason          ix:Objection -> xsd:string
ix:objectionResolved     ix:Objection -> xsd:boolean
ix:resolvedBy            ix:Objection -> xsd:string  ("price-match",
                           "explanation", "alternative-offered",
                           "reassurance", "unresolved")

# Priority signals
ix:priorityDimension     ix:PrioritySignal -> xsd:string
ix:signalStrength        ix:PrioritySignal -> xsd:string  ("weak",
                           "moderate", "strong")
ix:revealedPriority      -> xsd:string  (shortcut for use on any event)

# Confidence signals
ix:confidenceLevel       ix:ConfidenceSignal -> xsd:string  ("high",
                           "moderate", "low", "seeking-reassurance")

# Trigger events
ix:triggerType           ix:TriggerEvent -> xsd:string  ("problem",
                           "occasion", "deal", "curiosity", "recommendation")
ix:triggerDescription    ix:TriggerEvent -> xsd:string

# Budget signals
ix:statedBudget          ix:BudgetSignal -> xsd:decimal
ix:budgetConstraintType  ix:BudgetSignal -> xsd:string  ("hard-limit",
                           "preference", "flexible")

# Influence signals
ix:influenceSource       ix:InfluenceSignal -> xsd:string
ix:influenceType         ix:InfluenceSignal -> xsd:string  ("review",
                           "friend", "video", "brand-reputation",
                           "past-experience")

# Cross-referencing signals to events
ix:derivedFrom           ix:SignalEvent -> ix:InteractionEvent
```

### Objection categories (named individuals)

```
ix:PriceObjection        — "too expensive", "over budget"
ix:TrustObjection        — "I don't trust that brand", "the reviews worry me"
ix:CompatibilityObjection — "will it fit?", "is it compatible?"
ix:ComplexityObjection   — "that's too complicated", "I'm not technical"
ix:TimingObjection       — "I'll wait for Black Friday", "not ready yet"
ix:NeedObjection         — "I don't think I need that", "seems like overkill"
ix:RiskObjection         — "what if it doesn't work?", "can I return it?"
```

### Actor properties

```
ix:actorId               ix:Actor -> xsd:string
ix:actorSegment          ix:Actor -> xsd:string  (optional demographic or
                           behavioural segment)
ix:returningUser         ix:Actor -> xsd:boolean
ix:previousJourneyCount  ix:Actor -> xsd:integer
```

---

## How the Journey Flows Map to Events

### Flow 1: Build from scratch

Typical event sequence:
```
SessionStarted (+ TriggerEvent: "I want to build a gaming PC")
  -> Search ("gaming PC, 1440p, $1500 budget") (+ BudgetSignal)
  -> RecommendationReceived (GPU anchor suggestion)
  -> ProductViewed (RTX 4070) (+ PrioritySignal if user focuses on VRAM)
  -> ProductViewed (RX 7800 XT)
  -> ComparisonViewed (RTX 4070 vs RX 7800 XT) (+ DecisionPoint)
  -> AddedToCart (RTX 4070) (+ DecisionPoint: selected over 7800 XT)
  -> RecommendationReceived (compatible motherboard + CPU)
  -> QuestionAsked ("will this bottleneck?") (+ ConfidenceSignal: moderate)
  -> AnswerReceived (no bottleneck explanation)
  -> AddedToCart (CPU, motherboard, RAM, storage, PSU, case)
  -> BuildValidated (pass)
  -> CheckoutStarted
  -> CheckoutCompleted
SessionEnded
```

### Flow 2: Upgrade existing

Typical event sequence:
```
SessionStarted (+ TriggerEvent: "my PC is slow")
  -> QuestionAsked ("I have an i5-10400 and GTX 1660")
  -> AnswerReceived (bottleneck diagnosis)
  -> RecommendationReceived (GPU upgrade: RTX 4070)
  -> QuestionAsked ("will my PSU handle it?") (+ CompatibilityObjection)
  -> AnswerReceived (need PSU upgrade too)
  -> ProductViewed (Corsair RM850x)
  -> QuestionAsked ("what about my motherboard?")
  -> AnswerReceived (upgrade cliff warning) (+ AbandonmentSignal risk)
  -> RemovedFromCart (RTX 4070) (+ Objection: complexity)
  -> Search ("just upgrade GPU, keep everything else")
  -> RecommendationReceived (lower-power GPU that fits existing PSU)
  -> AddedToCart
  -> CheckoutCompleted
SessionEnded
```

### Flow 3: Gift recommendation

Typical event sequence:
```
SessionStarted (+ TriggerEvent: "nephew's birthday")
  -> Search ("gift for 16-year-old gamer, under $100") (+ BudgetSignal)
  -> ResultsViewed (3 products across categories)
  -> ProductViewed (Stream Deck)
  -> QuestionAsked ("does he need anything else for this to work?")
    (+ ConfidenceSignal: seeking reassurance)
  -> AnswerReceived ("no, it's self-contained, works via USB")
    (+ SatisfactionSignal)
  -> AddedToCart (Stream Deck)
  -> CheckoutCompleted
SessionEnded
```

---

## What This Ontology Enables

### For the business

- **Funnel analysis with *why*** — not just "60% drop off at cart" but
  "35% of cart abandonments followed a price objection on GPUs"
- **Objection mapping** — which products generate which objections, and
  which objections get resolved vs lead to abandonment
- **Priority discovery** — what do customers in segment X actually care
  about, based on what they ask and what they trade off
- **Recommendation effectiveness** — which AI recommendations get accepted,
  which get questioned, which get rejected, and why
- **Decision pattern clustering** — group users by how they decide, not
  just what they buy

### For the AI assistant

- **Adaptive conversation** — if the user has shown price sensitivity
  (BudgetSignal), lead with value options
- **Objection anticipation** — if similar users commonly object on
  compatibility, address it proactively
- **Confidence calibration** — a decisive user doesn't need reassurance;
  an uncertain user needs explanation, not more options
- **Cross-session continuity** — the journey model lets the assistant
  remember "you were looking at the 7800 XT last week"

### For analysis

- **Graph queries across both ontologies** — "show me all DecisionPoints
  where the user chose a product with lower performance tier and stated
  a price-related reason" traverses both the interaction graph and the
  product graph
- **Temporal patterns** — how long do users deliberate on high-value
  components vs low-value ones? Does dwell time predict purchase?
- **Conversion attribution** — which assistant answers preceded a
  SatisfactionSignal followed by AddedToCart?

---

## Relationship to the Retail Ontology

This ontology **imports** the retail ontology by reference. It does not
subclass or modify retail classes. The link points are:

| This ontology | Links to | Retail ontology |
|---|---|---|
| `ix:involvedProduct` | -> | `rt:Product` (and subclasses) |
| `ix:involvedCategory` | -> | `rt:ProductCategory` |
| `ix:involvedConfiguration` | -> | `rt:Configuration` |
| `ix:constraintViolated` | -> | `rt:CompatibilityConstraint` |

The interaction graph sits alongside the product graph. Queries can
traverse both: "find all Objections about products in the GPU category
where the objection type was PriceObjection and the product price
exceeded the user's stated budget."

---

## Next Steps

1. **Write the interaction ontology in Turtle** — classes, properties,
   objection category individuals
2. **Create sample journey data** — encode the three example journeys
   above as instance data to validate the model
3. **Define query templates** — the graph queries that power funnel
   analysis, objection mapping, and priority discovery
4. **Consider extraction rules** — how the AI identifies signal events
   from conversational text in real time
