#!/usr/bin/env python3

"""
Generates a realistic risk event dataset in Turtle format for the
TrustGraph Risk Management ontology.

Events are randomly generated across a configurable date range by
combining actors, risks, and assets with weighted probabilities that
reflect realistic threat patterns (e.g. APT groups favour phishing and
privilege escalation; insiders favour data exfiltration and fraud).

Severe events (risk score >= threshold) may trigger an incident response
Process with ordered ProcessSteps, assigned owners, and completion status.
"""

import random
import argparse
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Domain data
# ---------------------------------------------------------------------------

ACTORS = [
    ("actor-insider-fin", "Finance Insider",
     "An employee within the finance department with elevated access to payment systems."),
    ("actor-extern-apt28", "APT-28 Threat Group",
     "State-sponsored advanced persistent threat group targeting critical infrastructure."),
    ("actor-contractor-it", "IT Contractor",
     "Third-party contractor with temporary privileged access to internal systems."),
    ("actor-insider-eng", "Engineering Insider",
     "A software engineer with access to source code repositories and CI/CD pipelines."),
    ("actor-extern-darkside", "DarkSide Ransomware Group",
     "Cybercriminal group specialising in ransomware-as-a-service operations."),
    ("actor-insider-hr", "HR Insider",
     "Human resources employee with access to personnel records and payroll systems."),
    ("actor-extern-unknown", "Unknown External Actor",
     "Unattributed external threat actor identified through anomalous network activity."),
    ("actor-vendor-cloud", "Cloud Service Vendor",
     "Third-party cloud infrastructure provider with shared responsibility for data security."),
    ("actor-extern-lazarus", "Lazarus Group",
     "State-sponsored threat group known for financially motivated cyber operations."),
    ("actor-insider-exec", "Executive Insider",
     "Senior executive with broad access to strategic and financial systems."),
    ("actor-contractor-msp", "Managed Service Provider",
     "External MSP with remote management access to network and endpoint infrastructure."),
    ("actor-extern-fin7", "FIN7 Cybercrime Group",
     "Financially motivated threat group targeting retail and hospitality sectors."),
]

RISKS = [
    ("risk-payroll-fraud", "Payroll Fraud",
     "Manipulation of payroll records to divert funds to unauthorised accounts.", 0.85),
    ("risk-phishing", "Spear Phishing",
     "Targeted email attack using social engineering to harvest credentials.", 0.72),
    ("risk-usb-exfil", "USB Data Exfiltration",
     "Unauthorised transfer of sensitive data via removable storage media.", 0.68),
    ("risk-ransomware", "Ransomware Deployment",
     "Encryption of critical systems and data with demand for payment.", 0.95),
    ("risk-priv-escalation", "Privilege Escalation",
     "Exploitation of vulnerabilities to gain unauthorised elevated access.", 0.78),
    ("risk-supply-chain", "Supply Chain Compromise",
     "Injection of malicious code through a trusted third-party software dependency.", 0.88),
    ("risk-data-leak", "Accidental Data Leak",
     "Unintentional exposure of sensitive data through misconfiguration or human error.", 0.55),
    ("risk-credential-stuffing", "Credential Stuffing",
     "Automated use of stolen credential pairs to gain unauthorised access.", 0.65),
    ("risk-insider-trading", "Insider Trading Data Access",
     "Unauthorised access to material non-public information for financial gain.", 0.91),
    ("risk-cloud-misconfig", "Cloud Misconfiguration",
     "Security gaps arising from improperly configured cloud service settings.", 0.60),
    ("risk-sql-injection", "SQL Injection",
     "Exploitation of input validation flaws to execute arbitrary database queries.", 0.74),
    ("risk-dns-hijack", "DNS Hijacking",
     "Redirection of DNS queries to attacker-controlled infrastructure.", 0.70),
    ("risk-zero-day", "Zero-Day Exploit",
     "Exploitation of a previously unknown vulnerability with no available patch.", 0.93),
    ("risk-brute-force", "Brute Force Authentication",
     "Systematic trial of credential combinations to gain account access.", 0.58),
    ("risk-shadow-it", "Shadow IT",
     "Use of unsanctioned applications or services that bypass security controls.", 0.50),
]

ASSETS = [
    ("asset-treasury", "Treasury Funds",
     "Corporate treasury accounts holding operating capital and reserves."),
    ("asset-source-code", "Source Code Repository",
     "Internal Git repositories containing proprietary application source code."),
    ("asset-customer-db", "Customer Database",
     "Production database containing customer PII, account details, and transaction history."),
    ("asset-email-system", "Corporate Email System",
     "Enterprise email platform used for internal and external communications."),
    ("asset-erp", "ERP System",
     "Enterprise resource planning system managing finance, HR, and operations."),
    ("asset-cicd", "CI/CD Pipeline",
     "Continuous integration and deployment infrastructure for software delivery."),
    ("asset-cloud-infra", "Cloud Infrastructure",
     "Production cloud environment hosting customer-facing applications and services."),
    ("asset-hr-records", "HR Personnel Records",
     "Employee personal data including salaries, performance reviews, and benefits."),
    ("asset-trading-platform", "Trading Platform",
     "Internal electronic trading platform with access to market-sensitive data."),
    ("asset-vpn", "VPN Gateway",
     "Remote access VPN infrastructure providing encrypted connectivity to internal network."),
    ("asset-api-gateway", "API Gateway",
     "Public-facing API gateway routing external requests to internal microservices."),
    ("asset-backup-system", "Backup System",
     "Enterprise backup and disaster recovery infrastructure."),
    ("asset-dns-infra", "DNS Infrastructure",
     "Internal and external DNS servers managing domain resolution."),
    ("asset-payment-processor", "Payment Processor",
     "Integration with third-party payment processing for customer transactions."),
]

# Weighted mapping: actor -> [(risk_id, weight), ...]
# This makes the generated data more realistic — certain actors favour
# certain attack techniques.
ACTOR_RISK_WEIGHTS = {
    "actor-insider-fin":      [("risk-payroll-fraud", 5), ("risk-insider-trading", 4),
                               ("risk-data-leak", 3), ("risk-shadow-it", 1)],
    "actor-extern-apt28":     [("risk-phishing", 5), ("risk-priv-escalation", 4),
                               ("risk-zero-day", 4), ("risk-credential-stuffing", 2),
                               ("risk-dns-hijack", 2)],
    "actor-contractor-it":    [("risk-priv-escalation", 4), ("risk-usb-exfil", 3),
                               ("risk-cloud-misconfig", 3), ("risk-shadow-it", 2)],
    "actor-insider-eng":      [("risk-usb-exfil", 4), ("risk-supply-chain", 3),
                               ("risk-data-leak", 3), ("risk-shadow-it", 2)],
    "actor-extern-darkside":  [("risk-ransomware", 6), ("risk-phishing", 2),
                               ("risk-credential-stuffing", 2)],
    "actor-insider-hr":       [("risk-data-leak", 5), ("risk-payroll-fraud", 3),
                               ("risk-shadow-it", 2)],
    "actor-extern-unknown":   [("risk-credential-stuffing", 4), ("risk-brute-force", 4),
                               ("risk-sql-injection", 3), ("risk-dns-hijack", 2),
                               ("risk-supply-chain", 2)],
    "actor-vendor-cloud":     [("risk-cloud-misconfig", 6), ("risk-data-leak", 3),
                               ("risk-supply-chain", 2)],
    "actor-extern-lazarus":   [("risk-ransomware", 4), ("risk-zero-day", 4),
                               ("risk-phishing", 3), ("risk-supply-chain", 2)],
    "actor-insider-exec":     [("risk-insider-trading", 5), ("risk-data-leak", 3),
                               ("risk-shadow-it", 2)],
    "actor-contractor-msp":   [("risk-priv-escalation", 4), ("risk-cloud-misconfig", 4),
                               ("risk-credential-stuffing", 3), ("risk-supply-chain", 2)],
    "actor-extern-fin7":      [("risk-sql-injection", 4), ("risk-phishing", 4),
                               ("risk-credential-stuffing", 3), ("risk-brute-force", 2)],
}

# Weighted mapping: risk -> [(asset_id, weight), ...]
RISK_ASSET_WEIGHTS = {
    "risk-payroll-fraud":       [("asset-treasury", 5), ("asset-erp", 4),
                                 ("asset-payment-processor", 2)],
    "risk-phishing":            [("asset-email-system", 5), ("asset-source-code", 2),
                                 ("asset-vpn", 2), ("asset-cloud-infra", 1)],
    "risk-usb-exfil":           [("asset-source-code", 5), ("asset-customer-db", 3),
                                 ("asset-hr-records", 2)],
    "risk-ransomware":          [("asset-erp", 4), ("asset-customer-db", 4),
                                 ("asset-cloud-infra", 3), ("asset-backup-system", 3)],
    "risk-priv-escalation":     [("asset-cloud-infra", 4), ("asset-vpn", 4),
                                 ("asset-cicd", 3), ("asset-source-code", 2)],
    "risk-supply-chain":        [("asset-cicd", 5), ("asset-source-code", 4),
                                 ("asset-cloud-infra", 2)],
    "risk-data-leak":           [("asset-hr-records", 4), ("asset-customer-db", 4),
                                 ("asset-source-code", 2), ("asset-treasury", 1)],
    "risk-credential-stuffing": [("asset-vpn", 5), ("asset-email-system", 3),
                                 ("asset-api-gateway", 3)],
    "risk-insider-trading":     [("asset-trading-platform", 5), ("asset-treasury", 3),
                                 ("asset-erp", 2)],
    "risk-cloud-misconfig":     [("asset-cloud-infra", 5), ("asset-customer-db", 3),
                                 ("asset-api-gateway", 2)],
    "risk-sql-injection":       [("asset-customer-db", 5), ("asset-api-gateway", 4),
                                 ("asset-payment-processor", 3)],
    "risk-dns-hijack":          [("asset-dns-infra", 5), ("asset-email-system", 3),
                                 ("asset-api-gateway", 2)],
    "risk-zero-day":            [("asset-cloud-infra", 4), ("asset-vpn", 4),
                                 ("asset-cicd", 3), ("asset-api-gateway", 2)],
    "risk-brute-force":         [("asset-vpn", 5), ("asset-email-system", 3),
                                 ("asset-api-gateway", 3)],
    "risk-shadow-it":           [("asset-cloud-infra", 4), ("asset-source-code", 3),
                                 ("asset-customer-db", 2)],
}

# Event label templates per risk type for natural-sounding descriptions
EVENT_TEMPLATES = {
    "risk-payroll-fraud": [
        "Payroll diversion detected — {actor} modified payment routing",
        "Suspicious payroll amendment flagged for {actor}",
        "Ghost employee record created by {actor}",
        "Unauthorised bonus disbursement initiated by {actor}",
    ],
    "risk-phishing": [
        "Spear phishing campaign by {actor} targeting executives",
        "Credential harvesting email from {actor} detected",
        "Phishing link clicked by employee — attributed to {actor}",
        "Whaling attack by {actor} impersonating CFO",
    ],
    "risk-usb-exfil": [
        "USB device connected to restricted workstation by {actor}",
        "Large file transfer to removable media by {actor}",
        "Data exfiltration via USB detected — {actor}",
        "Unauthorised removable storage use by {actor}",
    ],
    "risk-ransomware": [
        "Ransomware payload delivered by {actor}",
        "File encryption detected on critical systems — {actor}",
        "Ransomware lateral movement by {actor}",
        "Ransom note deployed across network by {actor}",
    ],
    "risk-priv-escalation": [
        "Account escalated to domain admin by {actor}",
        "Privilege escalation via unpatched service — {actor}",
        "Unauthorised role elevation detected for {actor}",
        "Kernel exploit used for privilege escalation by {actor}",
    ],
    "risk-supply-chain": [
        "Malicious dependency injected by {actor}",
        "Compromised package detected in build pipeline — {actor}",
        "Supply chain attack via trojanised update — {actor}",
        "Third-party library backdoor introduced by {actor}",
    ],
    "risk-data-leak": [
        "Sensitive data exposed via public link by {actor}",
        "Accidental data share to external recipients by {actor}",
        "Misconfigured permissions led to data exposure — {actor}",
        "Unencrypted PII transmitted by {actor}",
    ],
    "risk-credential-stuffing": [
        "Credential stuffing attack on authentication endpoint — {actor}",
        "Automated login attempts detected from {actor}",
        "Breached credential reuse detected — {actor}",
        "High-volume authentication failures from {actor}",
    ],
    "risk-insider-trading": [
        "Unauthorised access to pre-earnings data by {actor}",
        "Material non-public information accessed by {actor}",
        "Suspicious query of financial forecasts by {actor}",
        "Restricted trading data downloaded by {actor}",
    ],
    "risk-cloud-misconfig": [
        "Cloud storage bucket left publicly accessible — {actor}",
        "IAM policy overly permissive after change by {actor}",
        "Security group misconfiguration by {actor}",
        "Cloud logging disabled by {actor}",
    ],
    "risk-sql-injection": [
        "SQL injection attempt on customer portal — {actor}",
        "Database exfiltration via injection attack — {actor}",
        "Malicious SQL payload detected from {actor}",
        "Automated SQL injection scan from {actor}",
    ],
    "risk-dns-hijack": [
        "DNS records modified to redirect traffic — {actor}",
        "DNS hijacking detected on external domains — {actor}",
        "Rogue DNS responses observed — {actor}",
        "DNS cache poisoning attempt by {actor}",
    ],
    "risk-zero-day": [
        "Zero-day exploit used to compromise perimeter — {actor}",
        "Unpatched vulnerability exploited by {actor}",
        "Novel exploit chain executed by {actor}",
        "Zero-day remote code execution by {actor}",
    ],
    "risk-brute-force": [
        "Brute force attack on VPN gateway — {actor}",
        "Sustained password spraying from {actor}",
        "Authentication brute force detected — {actor}",
        "Distributed login attack from {actor}",
    ],
    "risk-shadow-it": [
        "Unsanctioned SaaS application deployed by {actor}",
        "Shadow IT cloud instance discovered — {actor}",
        "Unapproved tool usage detected for {actor}",
        "Data uploaded to personal cloud storage by {actor}",
    ],
}


# Severity threshold — only events with risk score at or above this get a
# mitigation process attached.
SEVERITY_THRESHOLD = 0.75

# Probability that a qualifying severe event actually gets a process.
# Not every severe event has been triaged yet.
PROCESS_PROBABILITY = 0.6

# People / teams who can own processes and steps
INVOKERS = [
    "CISO Office",
    "SOC Lead",
    "VP Engineering",
    "Head of Risk",
    "Incident Commander",
]

STEP_OWNERS = [
    "SOC Tier-2 Analyst",
    "Forensics Team",
    "IT Operations",
    "Legal & Compliance",
    "Network Security",
    "Identity & Access Team",
    "DevSecOps",
    "HR Investigations",
    "External Counsel",
    "Crisis Communications",
]

# Playbook steps per risk type.  Each tuple is (label, typical owner pool).
# The generator picks owners from the pool randomly.
PLAYBOOKS = {
    "risk-ransomware": [
        ("Isolate affected hosts from the network", ["IT Operations", "Network Security"]),
        ("Capture forensic disk images", ["Forensics Team"]),
        ("Identify ransomware variant and IOCs", ["SOC Tier-2 Analyst", "Forensics Team"]),
        ("Notify legal and executive leadership", ["Legal & Compliance", "Crisis Communications"]),
        ("Restore systems from verified backups", ["IT Operations", "DevSecOps"]),
        ("Conduct post-incident review", ["SOC Tier-2 Analyst", "Forensics Team"]),
    ],
    "risk-zero-day": [
        ("Activate emergency patching protocol", ["DevSecOps", "IT Operations"]),
        ("Deploy compensating network controls", ["Network Security"]),
        ("Hunt for indicators of compromise across estate", ["SOC Tier-2 Analyst", "Forensics Team"]),
        ("Engage vendor for patch ETA", ["DevSecOps"]),
        ("Validate patch deployment and close", ["IT Operations", "DevSecOps"]),
    ],
    "risk-insider-trading": [
        ("Preserve access logs and query history", ["Forensics Team", "SOC Tier-2 Analyst"]),
        ("Restrict subject's system access", ["Identity & Access Team"]),
        ("Brief legal and compliance on findings", ["Legal & Compliance"]),
        ("Coordinate with HR for disciplinary review", ["HR Investigations"]),
        ("File regulatory disclosure if required", ["Legal & Compliance", "External Counsel"]),
    ],
    "risk-supply-chain": [
        ("Quarantine compromised packages and artifacts", ["DevSecOps"]),
        ("Audit dependency tree for additional exposure", ["DevSecOps", "SOC Tier-2 Analyst"]),
        ("Roll back to last known-good build", ["IT Operations", "DevSecOps"]),
        ("Notify downstream consumers", ["Crisis Communications", "Legal & Compliance"]),
        ("Harden build pipeline controls", ["DevSecOps"]),
    ],
    "risk-payroll-fraud": [
        ("Freeze affected payroll accounts", ["IT Operations"]),
        ("Review payroll change audit trail", ["Forensics Team", "SOC Tier-2 Analyst"]),
        ("Coordinate with HR and legal", ["HR Investigations", "Legal & Compliance"]),
        ("Recover diverted funds", ["Legal & Compliance", "External Counsel"]),
    ],
    "risk-priv-escalation": [
        ("Revoke escalated privileges immediately", ["Identity & Access Team"]),
        ("Analyse exploitation method", ["SOC Tier-2 Analyst", "Forensics Team"]),
        ("Patch or mitigate underlying vulnerability", ["DevSecOps", "IT Operations"]),
        ("Review access logs for lateral movement", ["SOC Tier-2 Analyst"]),
    ],
    "risk-phishing": [
        ("Block sender domains and quarantine messages", ["Network Security", "IT Operations"]),
        ("Reset credentials for affected users", ["Identity & Access Team"]),
        ("Scan endpoints for payload execution", ["SOC Tier-2 Analyst"]),
        ("Issue employee awareness notification", ["Crisis Communications"]),
    ],
}

# Fallback playbook for severe risks without a specific one
DEFAULT_PLAYBOOK = [
    ("Triage and confirm incident severity", ["SOC Tier-2 Analyst"]),
    ("Contain affected systems", ["IT Operations", "Network Security"]),
    ("Collect and preserve evidence", ["Forensics Team"]),
    ("Notify stakeholders and begin remediation", ["Crisis Communications", "Legal & Compliance"]),
]

PROCESS_STATUSES = ["open", "in-progress", "resolved"]


def weighted_choice(items_with_weights):
    items, weights = zip(*items_with_weights)
    return random.choices(items, weights=weights, k=1)[0]


def pick_assets(risk_id, min_assets=1, max_assets=3):
    asset_weights = RISK_ASSET_WEIGHTS.get(risk_id, [])
    if not asset_weights:
        return [random.choice(ASSETS)[0]]
    n = random.choices(
        range(min_assets, max_assets + 1),
        weights=[6, 3, 1][:max_assets - min_assets + 1],
        k=1,
    )[0]
    chosen = set()
    for _ in range(n):
        asset_id = weighted_choice(asset_weights)
        chosen.add(asset_id)
    return list(chosen) or [weighted_choice(asset_weights)]


def generate_events(n_events, start_date, end_date, seed=None):
    if seed is not None:
        random.seed(seed)

    actor_lookup = {a[0]: a[1] for a in ACTORS}
    risk_lookup = {r[0]: r for r in RISKS}

    total_seconds = int((end_date - start_date).total_seconds())
    timestamps = sorted(
        start_date + timedelta(seconds=random.randint(0, total_seconds))
        for _ in range(n_events)
    )

    events = []
    for i, ts in enumerate(timestamps, start=1):
        actor_id = random.choice(ACTORS)[0]

        risk_weights = ACTOR_RISK_WEIGHTS.get(actor_id)
        if risk_weights:
            risk_id = weighted_choice(risk_weights)
        else:
            risk_id = random.choice(RISKS)[0]

        asset_ids = pick_assets(risk_id)

        templates = EVENT_TEMPLATES.get(risk_id, ["{actor} triggered a risk event"])
        label = random.choice(templates).format(actor=actor_lookup[actor_id])

        events.append({
            "id": i,
            "timestamp": ts,
            "actor_id": actor_id,
            "risk_id": risk_id,
            "asset_ids": asset_ids,
            "label": label,
        })

    return events


def generate_processes(events):
    risk_scores = {r[0]: r[3] for r in RISKS}
    processes = []
    proc_id = 0

    for ev in events:
        score = risk_scores.get(ev["risk_id"], 0)
        if score < SEVERITY_THRESHOLD:
            continue
        if random.random() > PROCESS_PROBABILITY:
            continue

        proc_id += 1
        risk_id = ev["risk_id"]
        playbook = PLAYBOOKS.get(risk_id, DEFAULT_PLAYBOOK)

        invoker = random.choice(INVOKERS)
        status = random.choices(
            PROCESS_STATUSES, weights=[1, 3, 2], k=1
        )[0]

        steps = []
        for step_num, (step_label, owner_pool) in enumerate(playbook, start=1):
            owner = random.choice(owner_pool)
            if status == "resolved":
                complete = True
            elif status == "in-progress":
                complete = step_num <= len(playbook) // 2
            else:
                complete = False
            steps.append({
                "number": step_num,
                "label": step_label,
                "owner": owner,
                "complete": complete,
            })

        processes.append({
            "id": proc_id,
            "event_id": ev["id"],
            "label": f"IR-{proc_id:04d}: Response to {ev['label'][:60]}",
            "invoker": invoker,
            "status": status,
            "assigned_to": invoker,
            "steps": steps,
        })

    return processes


def emit_turtle(events, processes, out):
    out.write("\n")
    out.write("@prefix tg: <http://trustgraph.ai/ontology/> .\n")
    out.write("@prefix d: <http://trustgraph.ai/data/risk/> .\n")
    out.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
    out.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n")
    out.write("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n")
    out.write("\n")

    out.write("### ==========================================\n")
    out.write("###   ACTORS\n")
    out.write("### ==========================================\n\n")
    for actor_id, label, comment in ACTORS:
        out.write(f'd:{actor_id} a tg:Actor ;\n')
        out.write(f'    rdfs:label "{label}" ;\n')
        out.write(f'    rdfs:comment "{comment}" .\n\n')

    out.write("### ==========================================\n")
    out.write("###   RISKS\n")
    out.write("### ==========================================\n\n")
    for risk_id, label, comment, score in RISKS:
        out.write(f'd:{risk_id} a tg:Risk ;\n')
        out.write(f'    rdfs:label "{label}" ;\n')
        out.write(f'    rdfs:comment "{comment}" ;\n')
        out.write(f'    tg:riskScore "{score}"^^xsd:float .\n\n')

    out.write("### ==========================================\n")
    out.write("###   ASSETS\n")
    out.write("### ==========================================\n\n")
    for asset_id, label, comment in ASSETS:
        out.write(f'd:{asset_id} a tg:Asset ;\n')
        out.write(f'    rdfs:label "{label}" ;\n')
        out.write(f'    rdfs:comment "{comment}" .\n\n')

    out.write("### ==========================================\n")
    out.write("###   EVENTS\n")
    out.write("### ==========================================\n\n")
    for ev in events:
        eid = f"event-{ev['id']:04d}"
        ts = ev["timestamp"]
        ts_str = ts.strftime("%Y-%m-%dT%H:%M:%S")
        date_str = ts.strftime("%Y-%m-%d")
        label = ev["label"].replace('"', '\\"')

        out.write(f'd:{eid} a tg:Event ;\n')
        out.write(f'    rdfs:label "{label}" ;\n')
        out.write(f'    tg:timestamp "{ts_str}"^^xsd:dateTime ;\n')
        out.write(f'    tg:eventDate "{date_str}"^^xsd:date ;\n')
        out.write(f'    tg:hasActor d:{ev["actor_id"]} ;\n')
        out.write(f'    tg:hasRisk d:{ev["risk_id"]} ;\n')

        for j, asset_id in enumerate(ev["asset_ids"]):
            sep = " ." if j == len(ev["asset_ids"]) - 1 else " ;"
            out.write(f'    tg:impactsAsset d:{asset_id}{sep}\n')

        out.write("\n")

    if not processes:
        return

    out.write("### ==========================================\n")
    out.write("###   PROCESSES & STEPS\n")
    out.write("### ==========================================\n\n")

    for proc in processes:
        pid = f"process-{proc['id']:04d}"
        eid = f"event-{proc['event_id']:04d}"
        label = proc["label"].replace('"', '\\"')

        out.write(f'd:{pid} a tg:Process ;\n')
        out.write(f'    rdfs:label "{label}" ;\n')
        out.write(f'    tg:mitigatesEvent d:{eid} ;\n')
        out.write(f'    tg:invokedBy "{proc["invoker"]}" ;\n')
        out.write(f'    tg:processStatus "{proc["status"]}" ;\n')
        out.write(f'    tg:assignedTo "{proc["assigned_to"]}" ;\n')

        for j, step in enumerate(proc["steps"]):
            sid = f"{pid}-step-{step['number']:02d}"
            sep = " ." if j == len(proc["steps"]) - 1 else " ;"
            out.write(f'    tg:hasStep d:{sid}{sep}\n')

        out.write("\n")

        for step in proc["steps"]:
            sid = f"{pid}-step-{step['number']:02d}"
            step_label = step["label"].replace('"', '\\"')
            complete = "true" if step["complete"] else "false"

            out.write(f'd:{sid} a tg:ProcessStep ;\n')
            out.write(f'    rdfs:label "{step_label}" ;\n')
            out.write(f'    tg:stepNumber {step["number"]} ;\n')
            out.write(f'    tg:isComplete "{complete}"^^xsd:boolean ;\n')
            out.write(f'    tg:assignedTo "{step["owner"]}" .\n\n')


def main():
    parser = argparse.ArgumentParser(
        description="Generate risk event data in Turtle format"
    )
    parser.add_argument(
        "-n", "--num-events", type=int, default=200,
        help="Number of events to generate (default: 200)",
    )
    parser.add_argument(
        "--start-date", type=str, default="2026-01-01",
        help="Start date YYYY-MM-DD (default: 2026-01-01)",
    )
    parser.add_argument(
        "--end-date", type=str, default="2026-07-13",
        help="End date YYYY-MM-DD (default: 2026-07-13)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "-o", "--output", type=str, default="risk-data.ttl",
        help="Output file path (default: risk-data.ttl)",
    )
    args = parser.parse_args()

    start = datetime.strptime(args.start_date, "%Y-%m-%d")
    end = datetime.strptime(args.end_date, "%Y-%m-%d")

    events = generate_events(args.num_events, start, end, seed=args.seed)
    processes = generate_processes(events)

    with open(args.output, "w") as f:
        emit_turtle(events, processes, f)

    n_steps = sum(len(p["steps"]) for p in processes)
    print(f"Generated {len(events)} events, {len(processes)} processes, "
          f"{n_steps} steps -> {args.output}")


if __name__ == "__main__":
    main()
