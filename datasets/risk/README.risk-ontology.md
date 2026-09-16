TrustGraph Risk Management Ontology

This ontology provides a streamlined, Event-centric data model for Enterprise Risk Management (ERM) inside trustgraph.ai. It maps real-world occurrences by linking the threat actor, the specific risk mechanism, and the impacted corporate assets through a central event hub.
The Model Architecture

Instead of mapping complex, changing properties directly onto graph edges, this ontology uses an Event Hub pattern. Every observation is recorded as a unique tg:Event node that points outward to its contextual components.

       [ tg:Actor ]
            ^
            | tg:hasActor
            |
       [ tg:Event ] ------------> [ tg:Risk ] (with tg:riskScore)
            |      tg:hasRisk
            |
            | tg:impactsAsset
            v
       [ tg:Asset ] (1 or more)

Core Classes (Nodes)

    Event (tg:Event): The central hub capturing a specific risk occurrence, anomaly, or observation.

    Actor (tg:Actor): The internal or external entity bringing about the risk (e.g., an insider, a threat group, a system admin).

    Risk (tg:Risk): The vulnerability, threat event, or mechanism of harm (e.g., Payroll Fraud, USB Exfiltration). Holds the tg:riskScore.

    Asset (tg:Asset): The corporate resource, system, or entity at stake (e.g., Treasury Funds, Source Code, Database).

Design Optimizations
1. Simple, Flat Triples

By avoiding complex RDF-star or deep blank-node reification frameworks for standard tracking, this schema ensures rapid rendering, low query complexity, and out-of-the-box compatibility with the trustgraph.ai visual UI graph engine.
2. High-Speed Temporal Filtering

To maximize retrieval performance over massive datasets, the tg:Event class utilizes two distinct time properties:

    tg:timestamp (xsd:dateTime): Used for fine-grained sequencing, UI timeline plotting, and detailed forensics.

    tg:eventDate (xsd:date): A coarse, optimized property containing only the calendar date (YYYY-MM-DD).

    Performance Tip: Always structure your SPARQL queries to filter on tg:eventDate first. This allows the graph database to leverage primary index range scans and instantly prune irrelevant data partitions before evaluating structural graph relationships.

Sample SPARQL Query

To retrieve all high-risk events affecting assets within a specific date range, utilize the optimized tg:eventDate index filter like this:
Code snippet

PREFIX tg: <http://trustgraph.ai/ontology/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?event ?date ?actorLabel ?riskLabel ?assetLabel ?score
WHERE {
  # Coarse First-Pass Filter (High-speed index pruning)
  ?event tg:eventDate ?date .
  FILTER(?date >= "2026-07-01"^^xsd:date && ?date <= "2026-07-15"^^xsd:date)
  
  # Graph Traversal
  ?event tg:hasActor ?actor ;
         tg:hasRisk ?risk ;
         tg:impactsAsset ?asset .
  
  # Pull Attributes & Labels
  ?risk tg:riskScore ?score .
  ?actor rdfs:label ?actorLabel .
  ?risk rdfs:label ?riskLabel .
  ?asset rdfs:label ?assetLabel .
  
  # Secondary Attribute Filter
  FILTER(?score > 0.7)
}
ORDER BY DESC(?score)

