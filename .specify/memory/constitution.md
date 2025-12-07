# Python Trading Game Constitution

## Core Principles

### I. Clean Code Maintainability

Every line of code MUST be written with long-term maintainability as the primary concern. Code is read far more often than it is written. All implementations MUST prioritize:

- Clarity over cleverness
- Explicit intent through descriptive naming
- Modular design enabling easy refactoring
- Low cyclomatic complexity (single responsibility per function)

### II. KISS - Keep It Simple, Stupid

Simplicity is non-negotiable. Every feature implementation MUST:

- Use the simplest approach that solves the problem
- Avoid over-engineering or building for hypothetical future needs
- Resist feature creep that doesn't directly serve the current requirement
- Prefer standard library and well-known patterns over custom solutions

### III. YAGNI - You Aren't Gonna Need It

Do not implement features, abstractions, or generalizations that are not immediately required. All development MUST:

- Focus on solving the present requirement
- Avoid premature optimization or abstraction
- Add features only when demanded by actual use cases
- Defer complexity until justified by real requirements

### IV. DRY - Don't Repeat Yourself

Code duplication is a liability. All code MUST:

- Extract common logic into reusable functions or modules
- Eliminate copy-paste code through refactoring
- Maintain single source of truth for all business logic
- Use parameterization rather than duplication

### V. Type Safety and Documentation

All Python code MUST include:

- Complete type hints on all function parameters and return types
- Comprehensive docstrings for all public functions and classes
- Clear documentation of module purpose and public API
- Type hints MUST be validated with mypy or equivalent tooling

### VI. Test-Driven Development (NON-NEGOTIABLE)

Testing is fundamental to code quality. All development MUST follow:

- Red-Green-Refactor cycle: tests written first, then implementation
- Pytest unit tests for all new features and functions
- Minimum practical test coverage for critical paths
- Tests serve as executable documentation of expected behavior

## Development Standards

### Virtual Environment and Dependencies

All development MUST use:

- `.venv` directory for isolated Python virtual environments
- `pyproject.toml` for centralized dependency and configuration management
- Explicit version pinning for reproducible builds
- Clear separation between production and development dependencies

### Code Quality Gates

All code contributions MUST pass:

- Linting checks (ruff or equivalent)
- Type checking (mypy)
- All unit tests with passing status
- Code review verification of principle adherence

## Development Workflow

Code review MUST verify:

- Adherence to all Core Principles
- Cyclomatic complexity justified and explained if elevated
- Test coverage for all code paths
- Proper type hints and documentation
- No violations of KISS or YAGNI principles

Pull requests MUST include:

- Description of what changed and why
- Reference to principle alignment
- Test coverage verification
- Any breaking changes clearly documented

## Governance

This Constitution supersedes all other development practices and guidelines. Amendments to this document require:

1. Written proposal explaining the change and rationale
2. Documentation of impact on existing code
3. Community consensus through review
4. Version increment following semantic versioning

**Version**: 1.0.0 | **Ratified**: 2025-11-22 | **Last Amended**: 2025-11-22
