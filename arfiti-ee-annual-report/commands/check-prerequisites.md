---
name: check-prerequisites
description: Check if the legal entity is ready for annual report preparation
---

# Check Annual Report Prerequisites

Quickly verify whether a legal entity is ready to start annual report preparation.

## Usage

```
/arfiti-ee:check-prerequisites
```

## What This Checks

1. **Fiscal periods**: Are all 12 periods for the year closed?
2. **Company classification**: What size category? (Micro/Small/Medium/Large)
3. **Audit requirement**: Is statutory audit or review required?
4. **Trial balance**: Does it balance?
5. **Prior year data**: Are comparative figures available?

## Output

A status report showing:
- Period close status (all 12 periods)
- Company size category with metrics used
- Audit/review requirement
- Trial balance verification
- List of any blockers that must be resolved before starting
