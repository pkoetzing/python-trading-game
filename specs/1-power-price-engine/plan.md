# Implementation Plan: Power Price Simulation Engine

**Branch**: `1-power-price-engine` | **Date**: 2025-11-22 | **Spec**: [spec.md](./spec.md)

**Summary**: Build a mean-reverting power price simulator with stochastic volatility, jump events, and regime switching. Display real-time prices on a Streamlit dashboard. Core algorithm generates 900 price points over 180 seconds with user-configurable parameters for volatility, mean-reversion, and jump frequency. Volatility follows 3 regimes (low/medium/high) switching every 30 seconds with proportional jump probability scaling.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: numpy (stochastic simulation), pandas (data management), scipy (statistical distributions), streamlit (UI/visualization), plotly (charting)  
**Storage**: Local session state (Streamlit cache/session_state) - no persistent DB required  
**Testing**: pytest (unit tests), no mocking frameworks  
**Target Platform**: Desktop application (single-user, local execution)  
**Project Type**: Single application (Python monolith with Streamlit frontend)  
**Performance Goals**: 
  - Generate 900 prices in 180 seconds (5 prices/second = 1 every 0.2s)
  - Real-time visual latency ≤100ms (prices visible within 100ms of generation)
  - CPU ≤15%, Memory ≤150MB during full 180-second run

**Constraints**: 
  - Timing tolerance ±50ms (generate price ±50ms of target 0.2s intervals)
  - All prices must stay within [10, 300] EUR/MWh (hard bounds)
  - Regime switches at 30s ±2s tolerance

**Scale/Scope**: Single 180-second simulation session; ~250 lines of core algorithm, ~150 lines UI/visualization, ~200 lines tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Reviewed**: `/speckit.constitution` principles

✅ **Clean Code Maintainability**: Enforced via clear separation of concerns (simulation logic separate from UI), comprehensive type hints, and docstrings on all public functions.

✅ **KISS Principle**: Single-file Streamlit app avoids unnecessary abstractions. Core simulation uses straightforward stochastic math (normal distribution sampling, array operations).

✅ **YAGNI**: No persistence layer, no database, no user authentication, no multi-session management—only what's needed for single user, single session.

✅ **DRY**: Regime switching logic abstracted into `VolatilityRegime` class; parameter validation shared across all inputs; price boundary enforcement centralized in `PriceSimulator.generate()`.

✅ **Type Hints & Documentation**: All functions include type hints (numpy.ndarray, float, etc.) and docstrings explaining parameters, returns, and mathematical basis.

✅ **Pytest Unit Tests**: Dedicated test suite covering parameter validation, price generation bounds, regime switching mechanics, jump frequency accuracy, mean-reversion convergence, and success criteria SC-001 through SC-010.

**GATE RESULT**: ✅ PASS - No violations; complexity fully justified by domain requirements.

## Project Structure

### Documentation (this feature)

```
specs/1-power-price-engine/
├── spec.md                 # Feature specification (14 FRs, 6 user stories, 10 success criteria)
├── plan.md                 # This file (implementation plan)
├── research.md             # [To be created: technology stack validation, timing mechanisms]
├── data-model.md           # [To be created: data structures, entity definitions]
├── quickstart.md           # [To be created: setup + usage guide]
├── contracts/              # [To be created: API/configuration contracts]
└── checklists/
    └── requirements.md     # Specification quality validation
```

### Source Code (repository root)

```
src/
├── power_simulator/
│   ├── __init__.py
│   ├── engine.py                 # Core PriceSimulator class (price generation algorithm)
│   ├── regimes.py                # VolatilityRegime, RegimeScheduler classes
│   ├── parameters.py             # SimulationParameters validation and defaults
│   └── models.py                 # PricePoint, SimulationState data classes
├── ui/
│   └── app.py                    # Streamlit application (UI, parameters, chart display)
└── main.py                       # Entry point (python main.py launches Streamlit)

tests/
├── unit/
│   ├── test_parameters.py        # Validate input constraints (0-50, 0.01-0.5, 0-5)
│   ├── test_engine.py            # Price generation, bounds enforcement, timing
│   ├── test_regimes.py           # Regime switching, jump probability scaling
│   └── test_success_criteria.py  # SC-001 through SC-010 validation
├── integration/
│   └── test_full_simulation.py   # End-to-end 180-second runs with various parameters
└── conftest.py                   # Pytest fixtures (default parameters, numpy random seed)

pyproject.toml                     # Dependencies: numpy, pandas, scipy, streamlit, plotly, pytest
.venv/                            # Virtual environment
```

**Structure Decision**: Single-file application structure with `power_simulator` library + Streamlit UI app. Follows KISS principle—no unnecessary service layers, repositories, or multi-app complexity. All stochastic math centralized in `engine.py`; validation rules in `parameters.py`; regime logic in `regimes.py`. Tests mirror source structure with unit tests covering each module and integration tests validating full 180-second simulations.

## Phase 0: Research (To Be Completed)

**Goals**: Validate technology choices, verify timing mechanisms, confirm numerical stability.

**Tasks**:
1. **Streamlit Real-Time Updates**: Verify Streamlit can push new prices to chart every 0.2 seconds without blocking UI; confirm visual latency ≤100ms via Streamlit placeholders/columns for dynamic chart updates.
2. **NumPy/SciPy Timing**: Confirm `numpy.random.normal()` and `scipy.stats` normal distribution sampling execute in <1ms per sample; verify 900-point generation completes in <5 seconds.
3. **Plotly Real-Time Charting**: Validate plotly.express can dynamically update chart with 900 points; test fixed Y-axis [0, 300] scaling performance.
4. **Threading for Simulation**: Determine if Streamlit's single-threaded model supports real-time price generation; evaluate `threading.Thread` for background price generation with `queue.Queue` for UI synchronization.
5. **Regime Switching Edge Cases**: Verify uniform random regime selection produces expected distribution over 6 regime periods; test 30-second boundary timing with `time.time()`.

**Output**: `research.md` documenting findings, recommended implementation patterns, and identified risks.

## Phase 1: Design & Data Model (To Be Completed)

**Goals**: Define data structures, API contracts, and algorithmic details.

### 1.1 Data Model (`data-model.md`)

**Entities to document**:

- **`SimulationParameters`** (dataclass):
  - `max_volatility: float` (0-50 EUR, default 15)
  - `mean_reversion_strength: float` (0.01-0.5 per second, default 0.05)
  - `jump_frequency: float` (0-5 jumps/min, default 2)
  - Validation: Clamp or reject out-of-range values

- **`VolatilityRegime`** (enum + configuration):
  - `LOW`: volatility_multiplier=0.5, jump_prob_multiplier=1.0
  - `MEDIUM`: volatility_multiplier=1.0, jump_prob_multiplier=1.5
  - `HIGH`: volatility_multiplier=1.5, jump_prob_multiplier=2.0

- **`PricePoint`** (dataclass):
  - `timestamp: float` (seconds, 0.0 to 180.0)
  - `price: float` (EUR/MWh, [10, 300])
  - `regime: VolatilityRegime` (current regime at this point)
  - `jump_occurred: bool` (flag for jump detection)

- **`PriceSimulation`** (state container):
  - `parameters: SimulationParameters`
  - `current_price: float` (current state)
  - `elapsed_time: float` (0 to 180)
  - `regime: VolatilityRegime` (current regime)
  - `regime_switch_time: float` (time of next regime switch)
  - `prices: list[PricePoint]` (accumulated history)

### 1.2 Algorithmic Design

**Core Price Generation Step** (called every 0.2 seconds):

```
next_price = current_price
  + mean_reversion_component  # (100 - current_price) × mean_reversion_strength × 0.2
  + volatility_component       # N(0, regime.volatility_mult × max_volatility × 0.5) × sqrt(0.2)
  + jump_component            # Random jump if Poisson(jump_freq × regime.jump_mult × 0.2/60) triggered
next_price = clamp(next_price, 10, 300)  # Enforce bounds
```

**Regime Switching** (every 30 seconds):
- At t=0, 30, 60, 90, 120, 150: Select new regime uniformly at random from {LOW, MEDIUM, HIGH}
- Jump probability at regime switch time: `base_freq × regime.jump_prob_multiplier × (0.2/60)` per tick

### 1.3 API Contracts (`contracts/`)

Create OpenAPI-style specs for:
- **`/api/simulate`** (POST): Accept `SimulationParameters`, return stream of 900 `PricePoint` objects
- **`/api/validate-params`** (POST): Accept `SimulationParameters`, return validation result with error messages

### 1.4 Quick Start Guide (`quickstart.md`)

Document:
- Setup: `python -m venv .venv; source .venv/bin/activate; pip install -r requirements.txt`
- Launch: `streamlit run src/ui/app.py`
- Default behavior: Launch with no parameters, see prices generate in real-time
- Parameter adjustment: Sliders in sidebar for volatility, mean-reversion, jump frequency

### 1.5 Agent Context Update

After design is complete, run `.specify/scripts/powershell/update-agent-context.ps1` to register new technology dependencies (numpy, scipy, streamlit, plotly) in agent-specific context files.

## Phase 2: Implementation Roadmap

(Detailed breakdown to be created by `/speckit.tasks` command)

**Suggested Sprint Breakdown** (P1 features first, P2/P3 secondary):

**Sprint 1 (P1 Core - Days 1-2)**:
- `power_simulator/parameters.py`: Input validation, defaults
- `power_simulator/engine.py`: Basic price generation (mean-reversion + volatility only)
- `tests/unit/test_parameters.py`: Validate all parameter constraints
- `tests/unit/test_engine.py`: Bounds testing, price generation rate

**Sprint 2 (P1 Visualization - Days 3-4)**:
- `power_simulator/regimes.py`: Volatility regime switching with uniform random selection
- `ui/app.py`: Streamlit UI with parameter sliders, start/stop controls
- `tests/integration/test_full_simulation.py`: End-to-end 180-second runs
- Chart display (Plotly) with fixed axes

**Sprint 3 (P2/P3 Features - Days 5-6)**:
- `power_simulator/engine.py`: Add jump events with normal distribution magnitude
- `tests/unit/test_regimes.py`: Jump probability scaling validation
- Polish: Error handling, performance optimization, code review

**Sprint 4 (Testing & Validation - Days 7-8)**:
- Comprehensive test coverage (success criteria SC-001 through SC-010)
- Performance profiling (CPU, memory, latency)
- Documentation and code cleanup

## Success Validation Checklist

After implementation, validate against all 10 success criteria:

- [ ] **SC-001**: Generate 900 points in 180s ±50ms
- [ ] **SC-002**: All prices in [10, 300] EUR/MWh 100% of time
- [ ] **SC-003**: Mean-reversion keeps 60s window average in [80, 120]
- [ ] **SC-004**: Jump frequency ±20% of target
- [ ] **SC-005**: Regime switches at 30s ±2s
- [ ] **SC-006**: High regime 2x jumps vs low regime
- [ ] **SC-007**: Chart visual latency ≤100ms
- [ ] **SC-008**: 95% parameter combinations initialize successfully
- [ ] **SC-009**: Invalid input rejected in ≤100ms with clear message
- [ ] **SC-010**: CPU ≤15%, memory ≤150MB during run

## Risk & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Streamlit UI blocking on price generation | Medium | High | Use threading + queue.Queue for async price generation |
| Numpy/Plotly performance at 900 points | Low | Medium | Profile early; use Plotly scattergl if needed |
| Timing drift (0.2s intervals not exact) | Medium | Low | Use `time.time()` for drift detection; ±50ms tolerance acceptable |
| Jump magnitude clipping at bounds causes bias | Medium | Medium | Implement rejection sampling or careful bound clipping logic |
| Regime random selection not truly uniform | Low | Low | Use `numpy.random.choice()` for guaranteed uniform distribution |

---

**Status**: 📋 Ready for Phase 0 Research  
**Next Step**: Complete `/research.md`, then proceed to Phase 1 design documents  
**Approval**: Pending team review
