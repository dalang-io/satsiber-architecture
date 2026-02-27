# Uptime Institute Tier III - Design Requirements

## Overview

Tier III: Concurrently Maintainable Site Infrastructure

A Tier III data center allows any planned maintenance activity to take place without disrupting IT operations. Planned activities include preventive and corrective maintenance, repair, and component replacement.

## Key Requirements

### 1. Redundancy
- **N+1** redundancy for all capacity components (power, cooling)
- Multiple independent distribution paths serving IT equipment
- Only one distribution path required to serve the IT load at any time

### 2. Power
- Dual utility feeds (preferred but not mandatory)
- Diesel generator backup with N+1 configuration
- UPS systems in N+1 configuration
- Automatic Transfer Switches (ATS) for seamless failover
- Static Transfer Switches (STS) for critical loads
- Dual-corded IT equipment with A+B power feeds
- PDU redundancy per rack

### 3. Cooling
- N+1 CRAH/CRAC unit redundancy
- Chilled water system with N+1 chillers
- Redundant pumps (primary and secondary loops)
- Hot/cold aisle containment recommended
- Environmental monitoring (temperature, humidity, leak detection)

### 4. Network
- Diverse carrier entry points
- Redundant border routers and firewalls
- Redundant core switching (L3)
- Dual-homed server connectivity
- Out-of-band management network
- Meet-Me Room (MMR) with diverse paths

### 5. Fire Suppression
- Very Early Smoke Detection Apparatus (VESDA)
- Clean agent suppression (FM-200 or Novec 1230) for IT spaces
- Pre-action sprinkler for non-IT areas
- Emergency Power Off (EPO) integration
- Building Management System (BMS) integration

### 6. Physical Security
- Multi-layer access control
- CCTV surveillance with retention
- Mantrap entry for data hall
- 24/7 on-site security personnel

### 7. Concurrent Maintainability
- Every capacity component must be removable/serviceable without impacting IT load
- Maintenance bypass paths for UPS, cooling, and power distribution
- Isolation valves for chilled water systems
- Redundant control systems

## Single Point of Failure Analysis

Each system must be analyzed to ensure no single component failure can impact IT operations:

| System | Component | Redundancy | SPOF Mitigation |
|--------|-----------|-----------|-----------------|
| Power | Utility Feed | Dual Feed | Generator backup |
| Power | UPS | N+1 | Automatic bypass |
| Power | Generator | N+1 | Auto-start, ATS |
| Cooling | Chiller | N+1 | Auto-failover |
| Cooling | CRAH | N+1 | Redundant units |
| Network | Core Switch | 2N | Cross-connect |
| Network | ISP | Dual carrier | BGP failover |
| Fire | VESDA | Zoned | Redundant panels |
