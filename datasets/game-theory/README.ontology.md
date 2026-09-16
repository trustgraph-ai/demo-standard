Game Theory Ontology for TrustGraph.ai

This ontology provides a formal semantic schema (in OWL/RDF) for representing, modeling, and resolving Game Theory scenarios within a Knowledge Graph.

Unlike flat relational schemas, this ontology is built natively for semantic graph traversal. It supports both simultaneous games (using matrix outcomes) and sequential games with uncertainty (using decision trees with chance nodes, governed by Nature).
📂 Architecture Overview

The ontology maps the core mathematical concepts of game theory into five primary Class structures:

                  [gt:Game]
                      │
              (gt:hasRootNode)
                      │
              [gt:DecisionNode] ────(gt:belongsToPlayer)────► [gt:Player]
               /             \
       (gt:hasAction)   (gt:hasAction)
             /                 \
     [gt:Action]             [gt:Action]
          │                       │
   (gt:leadsToNode)        (gt:leadsToNode)
          │                       │
   [gt:ChanceNode]          [gt:OutcomeNode]
    /            \                │
(Action)       (Action)      (gt:hasPayoff)
  [p=0.7]       [p=0.3]           │
   ...            ...         [gt:Payoff] ──(gt:forPlayer)──► [gt:Player]

1. Key Classes

    gt:Game: The root container representing the overall conflict or interactive scenario.

    gt:Player: A rational (or boundedly rational) decision-maker or stakeholder in the game.

    gt:Node: The abstract base class representing any state in a sequential game tree.

        gt:DecisionNode: A point where a specific player must actively choose a strategy.

        gt:ChanceNode: A point representing environmental uncertainty (Nature's turn) where subsequent actions occur according to explicit probabilities.

        gt:OutcomeNode: A terminal leaf node representing the end-state of a path of play.

    gt:Action: A directed edge connecting one state (Node) to the next, representing a decision made by a player or a chance event.

    gt:Payoff: The relative reward or utility allocated to a specific player at an outcome state.

🤖 Why This Works Flawlessly in TrustGraph.ai

    Self-Describing (LLM Optimization): Every class, object property, and data property is richly decorated with rdfs:label and rdfs:comment. When TrustGraph's RAG pipeline parses a natural language scenario (e.g., "Nigel Farage Clacton By-election"), the LLM reads the ontology definitions as built-in instructions, ensuring accurate semantic entity extraction.

    Dynamic Tree Traversals via SPARQL: Because the tree structure is represented as triples, calculating Expected Value (EV) or running Backward Induction can be initiated directly via a SPARQL query traversing the directed gt:hasAction and gt:leadsToNode properties.

    Validatable with SHACL: Graph schemas can be strict. You can easily write SHACL (Shapes Constraint Language) shapes against this ontology to validate that the sum of the gt:hasProbability values originating from any gt:ChanceNode equals exactly 1.0.

🚀 Getting Started
1. Import the Ontology

Upload the gametheory.ttl ontology file into your TrustGraph.ai workspace. This registers the gt: namespace and exposes the semantic contracts to the graph reasoner.
2. Sample SPARQL Queries
Finding the Path to All Terminal Outcomes and Their Payoffs

To trace every sequence of events from a game's starting node to its ending payoffs:
Code snippet

PREFIX gt: <http://trustgraph.ai/schemas/gametheory#>

SELECT ?actionLabel ?nodeType ?player ?payoffValue
WHERE {
  ?game a gt:Game ;
        gt:hasRootNode ?root .
        
  ?root gt:hasAction ?action .
  ?action gt:actionLabel ?actionLabel ;
          gt:leadsToNode ?nextNode .
          
  ?nextNode a ?nodeType .
  
  OPTIONAL {
    ?nextNode gt:belongsToPlayer ?player .
  }
  
  OPTIONAL {
    ?nextNode gt:hasPayoff ?payoff .
    ?payoff gt:utilityValue ?payoffValue .
  }
}

Calculating Expected Values on Chance Nodes

To extract the raw data needed by your UI to solve the tree's probabilities:
Code snippet

PREFIX gt: <http://trustgraph.ai/schemas/gametheory#>

SELECT ?chanceNode ?actionLabel ?probability ?outcomeNode ?payoffPlayer ?payoffValue
WHERE {
  ?chanceNode a gt:ChanceNode ;
              gt:hasAction ?action .
              
  ?action gt:hasProbability ?probability ;
          gt:actionLabel ?actionLabel ;
          gt:leadsToNode ?outcomeNode .
          
  ?outcomeNode a gt:OutcomeNode ;
               gt:hasPayoff ?payoff .
               
  ?payoff gt:forPlayer ?payoffPlayer ;
          gt:utilityValue ?payoffValue .
}

🛠️ Extending the Schema

The ontology is designed to be modular. You can extend it to support:

    Information Sets: For games of imperfect information (where a player doesn't know which node they are currently at) by adding a gt:InformationSet class grouping multiple gt:DecisionNode instances.

    Cooperative Coalition Structures: Mapping groups of gt:Player entities into joint alliances.

