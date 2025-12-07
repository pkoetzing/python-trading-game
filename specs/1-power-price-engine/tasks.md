# Tasks: Power Price Simulation Engine

**Feature**: Power Price Simulation Engine  
**Branch**: `1-power-price-engine`  
**Date**: 2025-11-22  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Execution Overview

**Total Tasks**: 47 tasks across 5 phases  
**Phase Structure**: Setup → Foundational → User Stories (P1, P2, P3) → Polish  
**Parallelization**: [P] markers indicate parallelizable tasks within each phase  
**Dependencies**: User Story 1 (P1) must complete before User Story 3, 4, 5; User Stories 2-6 can run in parallel

## MVP Scope

**Recommended MVP** (minimum viable product for delivery):
- Phase 1: Setup + dependencies
- Phase 2: Foundational architecture
- Phase 3: User Story 1 (P1 - Launch with defaults)
- Phase 3: User Story 2 (P1 - Volatility control)  
- Phase 3: User Story 6 (P1 - Chart visualization)

**MVP Rationale**: Users can launch simulator with default parameters, adjust volatility, and see real-time prices on a chart. Covers P1 stories; P2/P3 enhancements can follow in subsequent sprints.

---

## Phase 1: Project Setup & Dependencies

**Goals**: Initialize Python project, configure virtual environment, set up pyproject.toml, create directory structure

### Core Setup

- [X] T001 Create project structure per implementation plan
- [X] T002 Initialize pyproject.toml with Python 3.10+ specification
- [X] T003 Add core dependencies to pyproject.toml: numpy, pandas, scipy, streamlit, plotly
- [X] T004 Add dev dependencies: pytest, pytest-cov, black, ruff, mypy
- [X] T005 Create .venv virtual environment and activate for development
- [X] T006 Generate pyproject.toml lock file (uv.lock) for reproducible builds
- [ ] T007 Create README.md with setup instructions and quick start guide
- [X] T008 Create .gitignore for Python project (venv, __pycache__, .pytest_cache, etc.)

---

## Phase 2: Foundational Architecture

**Goals**: Build shared infrastructure, models, and base classes that all user stories depend on

### Data Models & Validation

- [X] T009 Create src/power_simulator/models.py with dataclasses:
  - `SimulationParameters`: max_volatility, mean_reversion_strength, jump_frequency with type hints
  - `PricePoint`: timestamp, price, regime, jump_occurred
  - `SimulationState`: current price, elapsed time, regime, regime switch time, price history
- [X] T010 [P] Create src/power_simulator/parameters.py with validation:
  - Validate max_volatility in [0, 50] range (clamp or reject)
  - Validate mean_reversion_strength in [0.01, 0.5] range
  - Validate jump_frequency in [0, 5] range
  - Provide default values (volatility 15, strength 0.05, frequency 2)
  - Write validation error messages for user feedback
- [X] T011 [P] Create src/power_simulator/regimes.py with:
  - `VolatilityRegime` enum: LOW, MEDIUM, HIGH
  - Configuration: volatility multipliers (0.5, 1.0, 1.5) and jump probability multipliers (1.0, 1.5, 2.0)
  - `RegimeScheduler` class for uniform random regime selection every 30 seconds

### Core Engine Foundation

- [X] T012 Create src/power_simulator/engine.py with `PriceSimulator` class skeleton:
  - `__init__(parameters: SimulationParameters)` constructor
  - `reset()` method to initialize state (price=100, elapsed_time=0)
  - Type hints on all methods and attributes
  - Comprehensive docstrings for all public methods
- [X] T013 Implement `PriceSimulator.get_current_state()` method:
  - Return current price, elapsed time, regime, accumulated prices
  - Include type hints returning `SimulationState`
- [X] T014 Create src/power_simulator/__init__.py module exports:
  - Export `PriceSimulator`, `VolatilityRegime`, `SimulationParameters`, `PricePoint`
  - Allow `from power_simulator import PriceSimulator`

### Test Infrastructure

- [X] T015 Create tests/conftest.py with pytest fixtures:
  - `default_parameters()` fixture returning SimulationParameters with defaults
  - `numpy_seed()` fixture setting numpy random seed for reproducibility
  - `isolated_simulator()` fixture with fresh PriceSimulator instance
- [X] T016 Create tests/__init__.py for test module discovery
- [X] T017 Create tests/unit/__init__.py for unit test module

---

## Phase 3: User Story 1 - Launch Simulation with Default Parameters (P1)

**Goal**: Users can launch simulator without parameters and see prices generate in real-time

### Core Price Generation

- [ ] T018 [US1] Implement `PriceSimulator.generate_next_price()` method:
  - Accept elapsed_time parameter
  - Calculate mean-reversion component: `(100 - current_price) × strength × dt`
  - Calculate volatility component: `N(0, regime.volatility_mult × max_volatility × 0.5) × sqrt(dt)`
  - Sum components, clamp to [10, 300], update and return new price
  - Write comprehensive docstring explaining mathematics
  - Include type hints (return float, accept float)
  - Handle dt=0.2 as default time step
- [ ] T019 [P] [US1] Implement `PriceSimulator.run_step()` method:
  - Advance elapsed_time by 0.2 seconds
  - Generate next price via `generate_next_price()`
  - Create `PricePoint` and add to history
  - Return `PricePoint` for immediate UI update
  - Ensure execution time <50ms per step
- [ ] T020 [P] [US1] Implement regime switching in `RegimeScheduler`:
  - Every 30 seconds, select uniform random regime from {LOW, MEDIUM, HIGH}
  - Each regime 33% probability (use numpy.random.choice with equal weights)
  - Provide `current_regime()` method returning current regime
  - Provide `update(elapsed_time)` method to trigger regime changes

### Testing

- [X] T021 [US1] Create tests/unit/test_parameters.py:
  - Test valid parameter combinations (5 tests)
  - Test volatility clamping/rejection (3 tests)
  - Test mean-reversion strength bounds (3 tests)
  - Test jump frequency bounds (3 tests)
  - Test default values are correct (1 test)
- [X] T022 [P] [US1] Create tests/unit/test_engine.py with basic generation tests:
  - Test `reset()` sets price to 100 (1 test)
  - Test `generate_next_price()` returns float in [10, 300] (5 tests with different parameters)
  - Test 100 consecutive prices stay in bounds (1 test, SC-002 validation)
  - Test price generation timing (10 iterations, measure <50ms per step)
  - Test mean-reversion pulls price toward 100 over time (1 test with low volatility)
- [X] T023 [P] [US1] Create tests/integration/test_full_simulation.py:
  - Test full 180-second run (900 steps) with default parameters (1 test)
  - Verify exactly 900 price points generated (SC-001)
  - Verify all prices in [10, 300] bounds (SC-002)
  - Verify elapsed_time reaches 180 seconds ±50ms (1 test)

### Streamlit UI - Part 1

- [X] T024 [P] [US1] Create src/ui/app.py Streamlit application:
  - Create `PriceSimulator` instance in `st.session_state`
  - Add sidebar with parameter sliders (volatility, mean-reversion, jump_frequency)
  - Add "Start Simulation" button
  - Add "Stop Simulation" button
  - Initialize with default values displayed in sliders
  - Include type hints (accept streamlit widgets, return None)
  - Write docstrings for all functions
- [X] T025 [P] [US1] Implement real-time price generation loop:
  - Use Streamlit placeholder for dynamic chart updates
  - Generate prices at 0.2-second intervals
  - Update chart every 0.2 seconds (visual latency ≤100ms, SC-007)
  - Display current price in metric widget
  - Show elapsed time counter
  - Support pause/resume via state management
  - Test with 180-second run to verify all 900 points visible
- [X] T026 [US1] Create src/main.py entry point:
  - `if __name__ == "__main__": streamlit.run("src/ui/app.py")`
  - Or use `streamlit run src/ui/app.py` from command line
  - Document launch command in README

### Acceptance Testing

- [ ] T027 [US1] Manually verify User Story 1 acceptance scenarios:
  - Launch simulator, confirm defaults (vol 15, strength 0.05, freq 2) displayed
  - Confirm prices appear on chart every 0.2 seconds
  - Confirm after 180 seconds, exactly 900 points displayed
  - Confirm Y-axis shows 0-300, X-axis shows 0-180
  - Document results in test log

---

## Phase 4: User Story 2 - Adjust Volatility Parameter (P1)

**Goal**: Users can adjust volatility and see price swings increase/decrease

### Volatility Scaling

- [ ] T028 [P] [US2] Verify volatility regime multiplier implementation:
  - LOW regime applies 0.5x multiplier to user's max_volatility (test with vol=40, expect max swing ~10)
  - MEDIUM regime applies 1.0x multiplier (test with vol=40, expect max swing ~20)
  - HIGH regime applies 1.5x multiplier (test with vol=40, expect max swing ~30)
  - Create unit test with 3 scenarios, each measuring variance over 60-second window
- [ ] T029 [P] [US2] Test volatility boundary enforcement:
  - With volatility=5, run simulation and verify small price swings (max change ~1-2 EUR per step)
  - With volatility=40, run simulation and verify large price swings (max change ~5-10 EUR per step)
  - All prices still bounded [10, 300] even with max volatility 50
  - Create test with 3 volatility levels, measure standard deviation of returns

### UI Enhancement

- [ ] T030 [P] [US2] Add volatility slider UI in Streamlit:
  - Accept values 0-50 EUR in 1 EUR increments
  - Real-time chart update when slider changes
  - Display current volatility regime (LOW/MEDIUM/HIGH)
  - Show regime effective volatility (e.g., "HIGH: 40 EUR × 1.5 = 60 EUR effective")

### Testing

- [ ] T031 [US2] Create tests/unit/test_volatility.py:
  - Test with volatility=0 (minimal noise, SC-003 drift test)
  - Test with volatility=50 (maximum noise)
  - Test with volatility=25 (medium)
  - Each test runs 180 seconds and verifies price bounds maintained (SC-002)
  - Measure standard deviation of price returns
- [ ] T032 [P] [US2] Test mean-reversion effectiveness across volatility levels:
  - Low volatility: 60-second window average should drift less from 100
  - High volatility: 60-second window average should still stay in [80, 120] (SC-003)
  - Create parametrized test with 5 volatility levels

### Acceptance Testing

- [ ] T033 [US2] Manually verify User Story 2 acceptance scenarios:
  - Set volatility=5, run 30 seconds, observe smooth price movements
  - Set volatility=40, run 30 seconds, observe larger price swings
  - Confirm all prices remain in [10, 300] bounds
  - Document visual observations and test results

---

## Phase 5: User Story 6 - Visualize 180 Seconds of Price History (P1)

**Goal**: Users see complete 180-second price chart with fixed axes and real-time updates

### Chart Implementation

- [ ] T034 [P] [US6] Create `ChartBuilder` class in src/ui/charts.py:
  - Accept list of `PricePoint` objects
  - Generate Plotly figure with fixed Y-axis [0, 300]
  - Fixed X-axis [0, 180] seconds
  - Include title, axis labels, grid
  - Use scatter plot with line connector for 900 points
  - Write comprehensive docstring
- [ ] T035 [P] [US6] Implement real-time chart update mechanism:
  - Use `st.plotly_chart()` for Plotly rendering
  - Update chart every time new `PricePoint` added
  - Measure visual latency (should be ≤100ms, SC-007)
  - Use `st.empty()` or `st.container()` for dynamic updates
  - Test with 900 points; verify chart responsiveness

### Streamlit Chart UI

- [ ] T036 [P] [US6] Enhance app.py with chart display:
  - Create large area for chart (2/3 of screen width)
  - Display real-time price metric next to chart
  - Show elapsed time / total time progress
  - Show current regime visually (color-coded: blue=LOW, yellow=MEDIUM, red=HIGH)
  - Responsive layout for different screen sizes

### Testing

- [ ] T037 [US6] Create tests/unit/test_charts.py:
  - Test chart creation with 900 sample `PricePoint` objects (1 test)
  - Verify Y-axis fixed at [0, 300] (1 test)
  - Verify X-axis covers [0, 180] (1 test)
  - Test chart update performance (add 100 points, measure update time <100ms) (1 test)
- [ ] T038 [P] [US6] Integration test for full simulation visualization:
  - Run full 180-second simulation
  - Capture chart at multiple intervals (0s, 60s, 120s, 180s)
  - Verify all data points visible and correctly positioned
  - Verify no data loss or chart corruption

### Acceptance Testing

- [ ] T039 [US6] Manually verify User Story 6 acceptance scenarios:
  - Launch simulation, watch prices appear on chart in real-time
  - After 180 seconds, verify full timeline visible (0-180s on X-axis)
  - Confirm Y-axis spans 0-300 EUR/MWh
  - Verify all 900 points visible (no scrolling, fixed window)
  - Measure visual latency (should be <100ms after each price generation)
  - Document results in test log

---

## Phase 6: User Story 3 - Adjust Mean-Reversion Strength (P2)

**Goal**: Users can adjust mean-reversion and observe fast vs. slow reversion

### Mean-Reversion Testing

- [ ] T040 [P] [US3] Test mean-reversion strength variations:
  - Strength=0.01: Apply shock (price jump), observe slow drift back to 100 over 10+ seconds
  - Strength=0.4: Apply same shock, observe fast reversion within 1-2 seconds
  - Strength=0.25: Intermediate behavior
  - Create test injecting artificial price spike, measuring reversion time
- [ ] T041 [P] [US3] Verify 60-second window average (SC-003):
  - With strength=0.01, 60s window average may drift to [70, 130] range
  - With strength=0.4, 60s window average should stay tighter [85, 115]
  - With strength=0.05 (default), verify [80, 120] per SC-003
  - Parametrized test across 5 strength levels

### UI Enhancement

- [ ] T042 [P] [US3] Add mean-reversion strength slider to Streamlit UI:
  - Accept values 0.01-0.5 per second in 0.01 increments
  - Real-time chart update when slider changes
  - Display current reversion time estimate (e.g., "Time to 50% reversion: 5 seconds")

### Testing

- [ ] T043 [US3] Create tests/unit/test_mean_reversion.py:
  - Test reversion pulls price toward 100 (5 tests with different strengths)
  - Test reversion with different starting prices (95, 100, 105, 50, 200)
  - Measure reversion half-life for each strength

### Acceptance Testing

- [ ] T044 [US3] Manually verify User Story 3 acceptance scenarios:
  - Set strength=0.01, observe slow reversion behavior
  - Set strength=0.4, observe rapid reversion
  - Confirm time-averaged price stays reasonable regardless of strength
  - Document observations

---

## Phase 7: User Story 4 - Adjust Jump Frequency (P2)

**Goal**: Users can adjust jump frequency and observe jump occurrence differences

### Jump Implementation & Testing

- [ ] T045 [P] [US4] Implement jump events in engine.py:
  - Calculate jump probability per time step: `frequency × regime.jump_prob_multiplier × (0.2 / 60)`
  - Use Poisson or Bernoulli process for jump occurrence
  - Sample jump magnitude from normal distribution: `N(0, 0.5 × current_volatility)`
  - Apply jump to price, clamp to [10, 300]
  - Flag `jump_occurred=True` in `PricePoint`
  - Write docstring explaining jump process
- [ ] T046 [P] [US4] Test jump frequency accuracy (SC-004):
  - Run 180-second simulation with jump_frequency=0, verify no jumps occur
  - Run simulation with frequency=2/min, verify ~6 jumps (±20%, so 4.8-7.2 acceptable)
  - Run simulation with frequency=5/min, verify ~15 jumps (±20%, so 12-18 acceptable)
  - Parametrized test with 5 frequency levels, each run 180 seconds multiple times
  - Measure frequency across 10 runs, verify ±20% tolerance

### Jump Visualization

- [ ] T047 [P] [US4] Enhance chart to highlight jumps:
  - Mark jump events on chart (e.g., larger dots or color change)
  - Add legend explaining jump markers
  - Display jump count in UI metric

### Testing

- [ ] T048 [US4] Create tests/unit/test_jumps.py:
  - Test jump_frequency=0: 180-second run, verify exactly 0 jumps
  - Test jump_frequency=5: measure jump count distribution, verify mean ≈15 with tolerance
  - Test jump magnitude scales with volatility (low volatility = small jumps, high = large)
  - Test jumps constrained within [10, 300] bounds

### Acceptance Testing

- [ ] T049 [US4] Manually verify User Story 4 acceptance scenarios:
  - Set jump_frequency=0, run 60 seconds, observe smooth prices, no sudden moves
  - Set jump_frequency=5, run 180 seconds, count approximately 15 jumps
  - Verify jump sizes scale with volatility regime
  - Document jump count observations

---

## Phase 8: User Story 5 - Observe Volatility Regime Changes (P3)

**Goal**: Users see volatility regime switches every 30 seconds with visible behavior changes

### Regime Switching Verification

- [ ] T050 [P] [US5] Test regime switching timing (SC-005):
  - Run 180-second simulation
  - Record regime change times: should be at 0, 30, 60, 90, 120, 150 seconds ±2 seconds tolerance
  - Verify exactly 6 regime periods in 180 seconds
  - Create test measuring timing accuracy
- [ ] T051 [P] [US5] Verify regime selection is uniform random:
  - Run 30+ simulations (180s each = 180 regime periods total)
  - Count occurrences of LOW, MEDIUM, HIGH regimes
  - Verify each appears approximately 33% of time (allow ±10% deviation)
  - Statistical test using chi-square or binomial distribution

### Jump Probability Scaling (SC-006)

- [ ] T052 [P] [US5] Test jump probability scaling by regime:
  - Run multiple simulations in controlled regime (force regime, disable random switches)
  - LOW regime with frequency=3/min: should see ~1 jump per minute
  - HIGH regime with frequency=3/min: should see ~2 jumps per minute (2x multiplier)
  - Verify ratio HIGH:LOW ≈ 2:1 (SC-006)
  - Parametrized test across multiple frequency levels

### UI Enhancement

- [ ] T053 [P] [US5] Enhance Streamlit UI to show regime changes:
  - Display current regime with color background (LOW=blue, MEDIUM=yellow, HIGH=red)
  - Show regime timeline/heatmap at bottom of chart
  - Alert user when regime changes
  - Display "next regime switch in X seconds"

### Testing

- [ ] T054 [US5] Create tests/unit/test_regimes.py:
  - Test uniform random selection produces expected distribution (chi-square test)
  - Test regime timing occurs at correct intervals (30s ±2s)
  - Test jump probability multipliers applied correctly
  - Test regime-dependent price behavior differences
- [ ] T055 [P] [US5] Test volatility regime effect on price behavior:
  - LOW regime: expect tight price clustering
  - HIGH regime: expect wide price swings
  - Measure standard deviation by regime
  - Verify HIGH > MEDIUM > LOW variance

### Acceptance Testing

- [ ] T056 [US5] Manually verify User Story 5 acceptance scenarios:
  - Run 90+ seconds, observe regime switch at 30s and 60s boundaries
  - Confirm price behavior changes with regime (e.g., more jumps in HIGH)
  - Verify regime selection appears random (not all HIGH, not repeated patterns)
  - Document regime sequence and jump counts by regime

---

## Phase 9: Cross-Cutting & Success Criteria Validation

**Goals**: Verify all success criteria, performance requirements, error handling

### Success Criteria Testing

- [ ] T057 Create tests/unit/test_success_criteria.py validating SC-001 through SC-010:
  - **SC-001**: 900 points in 180s ±50ms → measure timing across 10 runs
  - **SC-002**: All prices [10, 300] → verify across 100 random parameter combinations
  - **SC-003**: 60s window average [80, 120] → run 180s, sample 10 windows, verify
  - **SC-004**: Jump frequency ±20% → run with freq=2, freq=5, measure accuracy
  - **SC-005**: Regime switches 30s ±2s → run 180s, measure 6 switch times
  - **SC-006**: HIGH regime 2x more jumps than LOW → controlled regime test
  - **SC-007**: Chart latency ≤100ms → measure UI update time for each price
  - **SC-008**: 95% valid parameters initialize → test 100 random valid combinations
  - **SC-009**: Invalid input rejected ≤100ms → test boundary inputs, measure response time
  - **SC-010**: CPU ≤15%, memory ≤150MB → profile full 180s run
- [ ] T058 Create tests/integration/test_success_criteria_e2e.py:
  - Run full 180-second simulations with 10 different random parameter combinations
  - Verify all success criteria met across all runs
  - Generate report with pass/fail for each SC

### Parameter Validation & Error Handling

- [ ] T059 [P] Test invalid parameter edge cases:
  - Volatility -1 (should clamp to 0 or reject with error message ≤100ms)
  - Volatility 51 (should clamp to 50 or reject)
  - Mean-reversion 0 (should clamp to 0.01)
  - Mean-reversion 0.6 (should clamp to 0.5)
  - Jump frequency -0.5 (should clamp to 0)
  - Jump frequency 10 (should clamp to 5)
- [ ] T060 [P] Create comprehensive error handling tests:
  - Test invalid parameter rejection messages are clear and under 100ms response
  - Test simulation handles edge cases gracefully
  - Test recovery from error states

### Performance Profiling

- [ ] T061 Profile full 180-second run:
  - Measure CPU usage (should be ≤15%)
  - Measure memory usage (should be ≤150MB)
  - Measure per-step timing (should be <50ms per 0.2s generation)
  - Create performance report with baseline metrics
- [ ] T062 [P] Profile chart rendering:
  - Measure Plotly chart generation time with 900 points
  - Measure chart update time each iteration
  - Verify visual latency ≤100ms (SC-007)

### Code Quality

- [ ] T063 Run linting checks:
  - Run ruff on all src/ and tests/ code
  - Fix all linting warnings
  - Enforce code style consistency
- [ ] T064 Run type checking:
  - Run mypy on all src/ code
  - Verify all functions have type hints
  - Fix type errors
- [ ] T065 Calculate test coverage:
  - Run `pytest --cov=src/power_simulator tests/`
  - Target: ≥80% code coverage
  - Document coverage report

### Documentation & Code Review

- [ ] T066 Update README.md with:
  - Setup instructions (venv, pip install)
  - Usage guide (how to launch Streamlit app)
  - Parameter explanation and ranges
  - Features list (user stories 1-5)
  - Performance expectations
- [ ] T067 Code review checklist:
  - Verify all functions have docstrings
  - Verify all type hints are present
  - Verify compliance with constitution principles (KISS, YAGNI, DRY)
  - Verify cyclomatic complexity is low (<10 per function)
  - Verify no mocking frameworks used in tests
  - Verify error messages are clear

---

## Phase 10: Polish & Final Validation

**Goals**: Final testing, documentation, demo readiness

### End-to-End Testing

- [ ] T068 Perform manual end-to-end testing:
  - Launch application with `streamlit run src/ui/app.py`
  - Run through all 6 user story acceptance scenarios
  - Verify all sliders work correctly
  - Verify start/stop controls function
  - Test parameter changes during simulation
  - Document all test results
- [ ] T069 Final performance validation:
  - Run 5 consecutive 180-second simulations
  - Verify performance stable (no memory leaks, no slowdown)
  - Capture performance metrics

### Documentation

- [ ] T070 Create QUICKSTART.md with:
  - One-minute setup guide
  - Example usage scenarios
  - Expected output screenshots/descriptions
  - Troubleshooting tips
- [ ] T071 Create API documentation:
  - Document all public classes and methods
  - Include parameter descriptions and ranges
  - Include usage examples
  - Generate or update in docstrings

### Final Validation Against Spec

- [ ] T072 Final spec compliance review:
  - Verify all 14 functional requirements (FR-001 through FR-014) are implemented
  - Verify all 6 user stories have acceptance criteria met
  - Verify all 10 success criteria pass
  - Create compliance checklist document

### Demo Readiness

- [ ] T073 Prepare demo script:
  - Default parameters demo (30 seconds)
  - Volatility adjustment demo (30 seconds, volatile market)
  - Mean-reversion demo (60 seconds, low reversion to show drift)
  - Jump frequency demo (60 seconds, high jumps)
  - Clean code walkthrough (10 minutes showing key functions)

### Ready for Merge

- [ ] T074 Final commit and code review:
  - All tests passing (100% success rate)
  - All linting passing (zero ruff violations)
  - All type checking passing (zero mypy errors)
  - Coverage ≥80%
  - All documentation complete
  - Code review approved
- [ ] T075 Merge feature branch to main:
  - Create pull request with feature description
  - Document changes in CHANGELOG
  - Tag release version
  - Update main branch README with new feature

---

## Dependency Graph & Execution Order

### User Story Completion Order

```
Phase 1 (Setup) → Phase 2 (Foundation)
                        ↓
                 Phase 3 (US1, US2, US6)
                 /            |      \
            Phase 6 (US3)  Phase 7(US4)  Phase 8(US5)
                 \            |      /
                        Phase 9 (Cross-Cutting)
                             ↓
                        Phase 10 (Polish)
```

**Critical Path**: Setup → Foundation → US1 → US6 (chart visualization) → Validation

**Parallel Execution Opportunities**:
- US2 (volatility) and US6 (chart) can run in parallel after US1 completes
- US3 (mean-reversion) and US4 (jumps) and US5 (regimes) can run in parallel after foundation
- All unit tests within a story can run in parallel
- All parameter validation tests can run in parallel

### MVP Fast-Track (Days 1-3)

To deliver MVP in 3 days, execute:
1. **Day 1**: Tasks T001-T017 (Setup + Foundation) in parallel
2. **Day 1-2**: Tasks T018-T027 (US1 core + testing) sequentially
3. **Day 2**: Tasks T028-T033 (US2 enhancement) in parallel with T034-T039 (US6 chart) in parallel
4. **Day 3**: Tasks T057-T062 (success criteria + performance) and T063-T067 (code quality)
5. **Day 3 Evening**: T068-T072 (final validation)

**Estimated Timeline**: 3 days MVP, +2 days for P2/P3 features, +1 day polish = 6 days total

---

## Task Parallelization Summary

**Parallelizable within Phase 3 (P1 Core)**:
- T010 (parameter validation) || T011 (regimes) || T012-T013 (engine foundation)
- T022 (unit tests) || T023 (integration tests)
- T024-T025 (Streamlit UI) can run with T018-T019 (core generation)

**Parallelizable within Phase 4 (US2)**:
- T028 || T029 (volatility testing)
- T030 (UI enhancement) || T031-T032 (tests)

**Parallelizable within Phase 5 (US6)**:
- T034 (chart builder) || T035 (chart updates)
- T036 (UI enhancement) || T037-T038 (tests)

**Parallelizable within Phase 9**:
- T057 || T058 (success criteria)
- T059 || T060 (error handling)
- T061 || T062 (performance profiling)
- T063 || T064 || T065 (code quality checks)

---

**Total Estimated Effort**:
- Setup & Foundation: 1 day
- P1 Features (US1, US2, US6): 2 days
- P2/P3 Features (US3, US4, US5): 1.5 days
- Testing & Validation: 1 day
- Polish & Documentation: 0.5 days
- **Total: ~6 days single-developer equivalent** (can be parallelized to 3-4 calendar days with 2 developers)

---

**Status**: ✅ All 75 tasks defined and ready for execution  
**Next Step**: Begin Phase 1 Setup tasks  
**Branch**: `1-power-price-engine`
