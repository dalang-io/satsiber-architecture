# Satsiber Data Center Architecture

Architecture documentation for **Satsiber Data Center** Uptime Institute **Tier III** Design Certification submission.

All diagrams are authored in [draw.io](https://app.diagrams.net/) (`.drawio` format) for professional, version-controlled documentation.

## Tier III Design Requirements

| Criteria | Requirement |
|---|---|
| Availability | 99.982% uptime |
| Redundancy | N+1 (power, cooling, network) |
| Concurrent Maintainability | Any capacity component can be removed for maintenance without impacting IT load |
| Distribution Paths | Multiple independent distribution paths serving IT equipment |
| Power | Dual-powered equipment with automatic transfer switches (ATS) |
| Cooling | Redundant cooling units with N+1 capacity |

## Repository Structure

```
satsiber-architecture/
├── diagrams/
│   ├── floor-plan/          # Data center floor plan & room layout
│   ├── electrical/          # Electrical single-line & distribution diagrams
│   ├── network/             # Network topology & cabling diagrams
│   ├── cooling/             # HVAC & cooling system diagrams
│   └── fire-suppression/   # Fire detection & suppression system diagrams
├── docs/                    # Supporting documentation & specifications
└── assets/                  # Images, exports, and reference materials
```

## Diagrams Overview

### 1. Floor Plan (`diagrams/floor-plan/`)
- Data hall layout with hot/cold aisle containment
- Raised floor plan with cable routing
- Room adjacency (UPS room, battery room, generator yard, NOC, staging)
- Equipment placement and rack layout
- Emergency egress paths

### 2. Electrical Distribution (`diagrams/electrical/`)
- Utility feed single-line diagram (dual utility feeds)
- Medium voltage switchgear
- Transformer and ATS configuration
- UPS system topology (N+1 redundant)
- Generator system with automatic transfer
- PDU and rack power distribution (A+B feeds)
- Static Transfer Switch (STS) layout
- Battery system and runtime calculations

### 3. Network Topology (`diagrams/network/`)
- Core/aggregation/access layer topology
- Redundant uplink and cross-connect paths
- Meet-Me Room (MMR) connectivity
- ISP/carrier diverse entry points
- Out-of-band management network
- Physical cabling diagram (structured cabling)
- Firewall and security zone segmentation

### 4. Cooling System (`diagrams/cooling/`)
- CRAC/CRAH unit placement and airflow
- Chilled water piping (primary/secondary loop)
- Hot/cold aisle containment design
- Redundant cooling paths (N+1)
- Condenser and cooling tower layout
- Environmental monitoring sensor placement

### 5. Fire Suppression (`diagrams/fire-suppression/`)
- VESDA (Very Early Smoke Detection Apparatus) layout
- Clean agent suppression system (FM-200 / Novec 1230)
- Fire detection zone mapping
- EPO (Emergency Power Off) integration
- Pre-action sprinkler system (if applicable)

## Certification Submission Checklist

- [ ] Floor plan with equipment layout and dimensions
- [ ] Electrical single-line diagram showing full redundancy path
- [ ] UPS and generator topology with N+1 configuration
- [ ] ATS and STS switching scheme
- [ ] Network topology with redundant paths
- [ ] Cooling system diagram with N+1 capacity
- [ ] Fire suppression system layout
- [ ] Concurrent maintainability narrative for each system
- [ ] Single point of failure analysis
- [ ] Capacity planning documentation

## Tools

- **Diagram Editor**: [draw.io / diagrams.net](https://app.diagrams.net/)
- **Format**: `.drawio` (XML-based, git-friendly)
- **Export**: PDF and PNG exports stored in `assets/`

## References

- [Uptime Institute Tier Standard: Topology](https://uptimeinstitute.com/tiers)
- [TIA-942: Data Center Standards Overview](https://tiaonline.org/)
- [ASHRAE TC 9.9: Thermal Guidelines for Data Processing Environments](https://tc0909.ashraetcs.org/)
