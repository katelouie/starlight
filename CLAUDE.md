# Claude Development Instructions for Starlight

## Environment Setup Requirements

**CRITICAL: Always run these commands before executing any Python code that uses Swiss Ephemeris:**

```bash
source ~/.zshrc
pyenv activate starlight
```

## Required Environment Commands

### Before running Python files:
```bash
source ~/.zshrc && pyenv activate starlight && python [file]
```

### Before running tests:
```bash
source ~/.zshrc && pyenv activate starlight && python tests/test_chart_generation.py
source ~/.zshrc && pyenv activate starlight && python tests/moon_phase_tester.py
```

### Before running examples:
```bash
source ~/.zshrc && pyenv activate starlight && python examples/usage.py
```

## Why This Matters

The Swiss Ephemeris dependency (`pyswisseph`) requires specific environment setup:
- The `starlight` pyenv environment contains the correct Python version and dependencies
- Swiss Ephemeris data files are configured for this specific environment
- Without proper activation, imports will fail or calculations will be incorrect

## Development Workflow

1. **Always** use the environment activation commands above
2. Never run bare `python` commands for this project
3. If a command fails with import errors, check that the environment is activated
4. The project uses Swiss Ephemeris data in `data/swisseph/ephe/` which requires proper path configuration

## Test Files That Require Environment

- `tests/test_chart_generation.py` - Main chart drawing tests
- `tests/moon_phase_tester.py` - Moon phase visualization tests  
- `tests/test_chart.py` - Chart calculation tests
- `examples/usage.py` - Usage examples
- Any file that imports from `starlight.*` modules

## Quick Commands

```bash
# Run main chart tests
source ~/.zshrc && pyenv activate starlight && python tests/test_chart_generation.py

# Run moon phase tests  
source ~/.zshrc && pyenv activate starlight && python tests/moon_phase_tester.py

# Run usage example
source ~/.zshrc && pyenv activate starlight && python examples/usage.py
```