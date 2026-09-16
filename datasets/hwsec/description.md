# Hardware Security

Dive into the security analysis of real-world IoT and embedded devices.
This dataset contains detailed hardware teardowns and vulnerability
assessments for three consumer products, drawn from peer-reviewed
security research.

## Devices analysed

- **Amazon Echo Dot (3rd Gen)** — unencrypted user data on flash storage,
  physical extraction via test pads, secure boot chain analysis
- **Master Lock Bluetooth Padlock** — REST API vulnerabilities, guest
  access escalation, brute-force attack surface, BLE information leakage
- **Eufy Smart Home (Homebase 2 + Video Doorbell)** — weak WPA2 key
  derivation (crackable in 20 seconds), cleartext commands, media
  encryption flaws, home network pivot risk

## What you can explore

- **Hardware decomposition** — browse the full hierarchy from system
  level down through subsystems, components, sub-components, and
  individual elements like registers and fuse rows.

- **Vulnerability analysis** — find vulnerabilities ranked by CVSS score,
  filter for unpatched or exploitable issues, and trace which
  countermeasures exist (and which are still unimplemented).

- **Attack surface mapping** — identify remotely exploitable interfaces,
  unauthenticated access points, and physical debug ports. See how
  attack surfaces map to MITRE ATT&CK and CAPEC techniques.

- **Threat modelling** — review adversary profiles with likelihood and
  impact ratings. Understand attack chains that cross trust boundaries,
  such as pivoting from a Wi-Fi vulnerability to media decryption.

- **Countermeasure gap analysis** — compare deployed defences against
  recommended mitigations. Find where security gaps remain and what
  it would cost to close them.

- **Firmware and trust boundaries** — check for unsigned firmware,
  missing compiler hardening flags, and trust boundaries with known
  bypasses.

## What kinds of questions work well

- "Which vulnerabilities have no countermeasure?"
- "What are the remotely exploitable attack surfaces?"
- "Show the hardware decomposition of the Echo Dot"
- "Which devices have unlocked debug interfaces?"
- "What is the highest-impact threat scenario across all devices?"
- "Compare the security posture of the three devices"

## Features

- 24 pre-built SPARQL queries covering decomposition, vulnerabilities,
  attack surfaces, firmware, trust boundaries, and threat models
- Knowledge graph tool for natural language security questions
- Full alignment with industry standards: CVE, CWE, CVSS, MITRE
  ATT&CK, CAPEC, and D3FEND
