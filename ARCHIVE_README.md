# Starlight v0.1.0 - Legacy Architecture (ARCHIVED)

**⚠️ This branch is archived and should not be modified.**

This branch preserves the original Starlight codebase before the architecture
refactor that introduced the modular component system.

## What This Contains

- Original monolithic Chart class
- Complete ChartWheel drawing system
- Legacy test suite (tests_old/)
- Rich terminal presentation layer

## Why Archived?

This code was replaced by the new modular architecture in v0.2.0+, which
provides:

- Protocol-based component system
- Immutable data models
- Layer-based visualization
- Comprehensive dignity calculations

## How to Access

```bash
# View this archive
git checkout archive/v0.1.0-legacy

# Or checkout the tagged version
git checkout v0.1.0
