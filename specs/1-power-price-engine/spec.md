# Feature Specification: Power Price Simulation Engine

**Feature Branch**: `1-power-price-engine`  
**Created**: 2025-11-22  
**Status**: Draft  
**Input**: User description: "Create an engine that simulates mean-reverting spot power prices with jumps and time-dependent volatility. Prices should be between 10 EUR/MWh and 300 EUR/MWh and revert to a mean of 100 EUR/MWh. Prices should be simulated in real-time for a period of 180 seconds, with a new price generated every 0.2 second. The main parameters should be adjustable by the user, including max volatility (0-50 EUR), mean-reversion strength (0.01-0.5 per second), and jump frequency (0-5 jumps per minute). The volatility regime should switch randomly between low, medium and high volatility every 30 seconds, with jumps being more likely in high volatility regimes. The simulation should be displayed in a chart with fixed Y-axis from 0 to 300 EUR/MWh and X-axis showing exactly 180 seconds of data."

## User Scenarios & Testing

### User Story 1 - Launch Simulation with Default Parameters (Priority: P1)

A power trader wants to quickly start observing realistic price movements without worrying about detailed configuration. They launch the simulation engine and immediately see prices updating in real-time on a chart.

**Why this priority**: This is the core MVP value - the user can see the engine working with sensible defaults. Without this, the tool is not functional.

**Independent Test**: Can be fully tested by launching the engine without parameters and verifying prices appear on the chart in real-time for the full 180-second period.

**Acceptance Scenarios**:

1. **Given** the simulation engine is launched, **When** no parameters are provided, **Then** the system uses default values (mean 100 EUR/MWh, volatility 15 EUR, mean-reversion 0.05/s, jump frequency 2/min) and begins generating prices
2. **Given** the simulation is running, **When** 0.2 seconds elapse, **Then** a new price is generated and displayed
3. **Given** the simulation is active, **When** 180 seconds have passed, **Then** the chart displays exactly 180 seconds of price history with 900 data points

---

### User Story 2 - Adjust Volatility Parameter (Priority: P1)

A power trader wants to simulate different market conditions with varying price volatility. They adjust the maximum volatility parameter to test how their trading strategies perform under different market stress levels.

**Why this priority**: User parameter control is essential for the tool's utility. The volatility parameter directly affects price realism and scenario testing.

**Independent Test**: Can be fully tested by setting volatility to different values (low: 5 EUR, medium: 15 EUR, high: 40 EUR) and observing that price swings increase/decrease accordingly while prices remain within bounds.

**Acceptance Scenarios**:

1. **Given** the simulation is configured with max volatility 5 EUR, **When** the simulation runs, **Then** price movements are constrained to small changes per tick
2. **Given** the simulation is configured with max volatility 40 EUR, **When** the simulation runs, **Then** price movements are noticeably larger per tick
3. **Given** any volatility parameter is set, **When** the simulation runs for 180 seconds, **Then** all prices remain within the bounds of 10-300 EUR/MWh

---

### User Story 3 - Adjust Mean-Reversion Strength (Priority: P2)

A trader wants to test how different levels of mean-reversion affect price behavior. They adjust the mean-reversion strength to simulate markets where prices snap back to the mean quickly versus slowly drifting back.

**Why this priority**: This parameter provides valuable scenario testing but is secondary to volatility adjustment. Advanced traders would use this; basic users can rely on defaults.

**Independent Test**: Can be fully tested by setting mean-reversion to low (0.01/s) and high (0.4/s) values and observing that low values allow prices to drift further from the mean while high values pull prices back quickly.

**Acceptance Scenarios**:

1. **Given** mean-reversion strength is set to 0.01/s, **When** a price spike occurs, **Then** the price slowly drifts back toward 100 EUR/MWh over multiple seconds
2. **Given** mean-reversion strength is set to 0.4/s, **When** a price spike occurs, **Then** the price quickly reverts toward 100 EUR/MWh within 1-2 seconds
3. **Given** mean-reversion strength is adjusted, **When** the simulation runs for 180 seconds, **Then** the time-averaged price stays near 100 EUR/MWh

---

### User Story 4 - Adjust Jump Frequency (Priority: P2)

A trader wants to simulate market conditions with different levels of sudden price shocks. They adjust the jump frequency parameter to test scenarios ranging from calm markets (rare jumps) to turbulent markets (frequent jumps).

**Why this priority**: Jump frequency affects market realism but is less critical than core simulation. It's a refinement parameter for advanced scenario testing.

**Independent Test**: Can be fully tested by comparing simulations with jump frequency 0/min (no jumps) and 5/min (frequent jumps) and observing the difference in sudden price movements.

**Acceptance Scenarios**:

1. **Given** jump frequency is set to 0 jumps/minute, **When** the simulation runs, **Then** no sudden price jumps occur and movement is smooth
2. **Given** jump frequency is set to 5 jumps/minute, **When** the simulation runs for 180 seconds, **Then** approximately 15 jumps occur (±5 tolerance)
3. **Given** jump frequency is set to any value, **When** a jump occurs, **Then** the jump magnitude is proportional to volatility and constrained within price bounds

---

### User Story 5 - Observe Volatility Regime Changes (Priority: P3)

A trader wants to understand how market volatility regimes affect price dynamics. They run the simulation and observe the price behavior switching between different volatility levels to see realistic regime-switching behavior.

**Why this priority**: This is a realistic market feature but not essential for basic simulation. It's a P3 enhancement that makes the simulation more realistic for advanced analysis.

**Independent Test**: Can be fully tested by running the simulation for at least 90 seconds and observing that price volatility changes noticeably at 30-second intervals, with more jumps during high-volatility regimes.

**Acceptance Scenarios**:

1. **Given** the simulation has been running for more than 30 seconds, **When** the volatility regime switches, **Then** the price behavior changes noticeably (either smoother or more volatile)
2. **Given** the system is in a high-volatility regime, **When** jumps can occur, **Then** jump probability is higher than in low-volatility regimes
3. **Given** the simulation runs for 180 seconds, **When** volatility regime changes occur, **Then** they happen at approximately 30-second intervals

---

### User Story 6 - Visualize 180 Seconds of Price History (Priority: P1)

A trader wants to see the complete price history on a fixed chart to understand the full price trajectory. The chart always shows exactly 180 seconds of data with a properly scaled Y-axis showing the full price range.

**Why this priority**: The visualization is core to the tool's usability. Without a proper chart, the simulation data is meaningless to the user.

**Independent Test**: Can be fully tested by verifying the chart displays 180 seconds of data on X-axis (0-180s), has Y-axis from 0-300 EUR/MWh, and all 900 data points are visible and properly scaled.

**Acceptance Scenarios**:

1. **Given** the simulation is running, **When** prices are generated, **Then** they appear on a real-time updating chart
2. **Given** the chart is displayed, **When** 180 seconds have elapsed, **Then** the X-axis shows the full 180-second window without scrolling or missing data
3. **Given** the chart is displayed, **When** any price is shown, **Then** the Y-axis is fixed from 0 to 300 EUR/MWh and prices are properly scaled

---

### Edge Cases

- What happens when user sets volatility outside the allowed range (0-50 EUR)? System should clamp or reject invalid input.
- How does the system handle zero jump frequency? Simulation should run without any jumps.
- What happens if mean-reversion is set to maximum (0.5/s)? Prices should revert very rapidly to the mean.
- How does system behave when jump occurs exactly at price boundary (10 or 300 EUR)? Jump should be constrained to keep price within bounds.
- What if the simulation is paused and resumed? Should resume from the current state without data loss or time gaps.

## Clarifications

### Session 2025-11-22

- Q: How should the initial price (at time 0) be determined? → A: Always start at exactly 100 EUR/MWh
- Q: How should volatility be applied across the three regimes? → A: Fixed multipliers (Low: 0.5x, Medium: 1.0x, High: 1.5x of max_volatility)
- Q: How should jump magnitude be calculated and distributed? → A: Normal distribution with mean=0, std_dev = 0.5 × current_volatility
- Q: What should be the relative jump probabilities across the three volatility regimes? → A: Proportional to regime volatility multiplier (Low: 1x, Medium: 1.5x, High: 2x the base jump frequency)
- Q: How should the three volatility regimes be selected and ordered during the 180-second simulation? → A: Uniform random selection with equal probability (each regime has 33% chance at each 30-second boundary)

## Requirements

### Functional Requirements

- **FR-001**: System MUST simulate power prices that always start at exactly 100 EUR/MWh
- **FR-002**: System MUST generate a new price every 0.2 seconds for exactly 180 seconds (900 total data points)
- **FR-003**: System MUST constrain all prices to the range [10, 300] EUR/MWh at all times
- **FR-004**: System MUST implement mean-reversion to 100 EUR/MWh with user-adjustable strength (0.01-0.5 per second)
- **FR-005**: System MUST implement stochastic volatility with user-adjustable maximum volatility (0-50 EUR); volatility is applied via regime multipliers (Low: 0.5x, Medium: 1.0x, High: 1.5x)
- **FR-006**: System MUST implement random jump events with user-adjustable frequency (0-5 jumps per minute); jump magnitude follows normal distribution (mean=0, std_dev = 0.5 × current_volatility); jump probability scales with regime (Low: 1x, Medium: 1.5x, High: 2x)
- **FR-007**: System MUST implement time-dependent volatility with three regimes (low, medium, high) that switch every 30 seconds using uniform random selection (each regime has equal 33% probability at each 30-second boundary)
- **FR-008**: System MUST increase jump probability during high-volatility regimes compared to low-volatility regimes
- **FR-009**: System MUST display prices on a real-time updating chart with X-axis showing 0-180 seconds and fixed Y-axis from 0-300 EUR/MWh
- **FR-010**: System MUST allow user to configure all parameters before simulation starts (volatility, mean-reversion, jump frequency)
- **FR-011**: System MUST provide sensible default values for all adjustable parameters if user does not specify them
- **FR-012**: System MUST validate all user input parameters and reject values outside allowed ranges
- **FR-013**: System MUST support starting and stopping the simulation
- **FR-014**: System MUST achieve real-time price generation with minimal latency (≤50ms between target and actual generation time)

### Key Entities

- **PriceSimulation**: Represents the state of a running simulation, containing current price, time elapsed, volatility regime, and parameter configuration
- **VolatilityRegime**: Defines low, medium, or high volatility characteristics with specific multipliers (Low: 0.5x volatility and 1.0x jump probability, Medium: 1.0x volatility and 1.5x jump probability, High: 1.5x volatility and 2.0x jump probability); switches every 30 seconds via uniform random selection
- **PricePoint**: A single price value with its associated timestamp; 900 instances created per simulation (one every 0.2 seconds)
- **SimulationParameters**: Contains user-adjustable settings: max_volatility, mean_reversion_strength, jump_frequency, with validation rules

## Success Criteria

### Measurable Outcomes

- **SC-001**: Simulation generates exactly 900 price points over 180 seconds (one every 0.2 seconds ±50ms tolerance)
- **SC-002**: All generated prices remain within [10, 300] EUR/MWh bounds 100% of the time
- **SC-003**: Mean-reversion pulls prices toward 100 EUR/MWh; average price over any 60-second window stays within [80, 120] EUR/MWh
- **SC-004**: Jump frequency matches user specification ±20% (e.g., 2/min target results in 1.6-2.4 jumps per minute over long simulation)
- **SC-005**: Volatility regime switches occur at 30-second intervals with ±2 second tolerance
- **SC-006**: High-volatility regimes produce 2x more jumps than low-volatility regimes
- **SC-007**: Chart updates in real-time with visual latency ≤100ms between price generation and display
- **SC-008**: 95% of user-provided valid parameter combinations successfully initialize simulation
- **SC-009**: Invalid parameter input is rejected with clear error message within 100ms
- **SC-010**: Simulation maintains consistent performance (CPU usage ≤15%, memory ≤150MB) throughout 180-second run

## Assumptions

- User has a display capable of showing matplotlib or similar plotting library
- Python 3.10+ is available in the execution environment
- Random number generation using numpy.random is acceptable
- Real-time simulation means best-effort scheduling; minor timing deviations ±50ms are acceptable
- "Mean of 100 EUR/MWh" means the long-term average should gravitate toward 100, not that all prices average to exactly 100
- Jump sizes follow a distribution proportional to current volatility (not fixed magnitude)
- User prefers a desktop application over web-based solution (GUI using matplotlib or similar)
