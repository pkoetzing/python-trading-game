# Python Trading Game

Realistic power spot price simulator with mean-reversion, jump events, and volatility regimes.

## Features

- **Real-Time Simulation**: Generate 900 price points over 180 seconds (0.2s intervals)
- **Mean-Reversion Dynamics**: Prices revert to 100 EUR/MWh with configurable strength
- **Jump Events**: Rare price jumps with frequency and magnitude scaling by volatility
- **Volatility Regimes**: LOW/MEDIUM/HIGH regimes switching every 30 seconds
- **Interactive UI**: Streamlit dashboard with parameter controls and live price chart
- **Bounded Prices**: Prices constrained to [10, 300] EUR/MWh range

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd python-trading-game
   ```

2. **Create virtual environment** (optional but recommended)

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -e .
   # Or with dev dependencies:
   pip install -e ".[dev]"
   ```

### Running the Simulator

Start the interactive Streamlit application:

```bash
streamlit run src/ui/app.py
```

The application will open in your browser at `http://localhost:8501`

### Using the Simulator

1. **Adjust Parameters** (sidebar):
   - **Maximum Volatility**: 0-50 EUR/MWh (default: 15)
   - **Mean-Reversion Strength**: 0.01-0.5 per second (default: 0.05)
   - **Jump Frequency**: 0-5 per minute (default: 2)

2. **Control Simulation**:
   - Click **▶️ Start** to begin price generation
   - Click **⏸️ Pause** to freeze the simulation
   - Click **🔄 Reset** to start over with current parameters

3. **Monitor Live Data**:
   - Real-time price chart (180-second window)
   - Current price, elapsed time, regime, price points count
   - Jump event counter

## Architecture

### Core Modules

- **`src/power_simulator/`**: Core simulation engine
  - `engine.py`: PriceSimulator class with mean-reversion + jump diffusion
  - `models.py`: Data models (PricePoint, SimulationState, SimulationParameters)
  - `regimes.py`: Volatility regime management (LOW/MEDIUM/HIGH)

- **`src/ui/`**: User interface
  - `app.py`: Streamlit application with dashboard
  - `charts.py`: Plotly chart builder with fixed axes

- **`tests/`**: Comprehensive test suite
  - `unit/`: Parameter validation, price generation, chart building
  - `integration/`: Full 180-second simulation tests

## Price Generation

The simulator uses a discrete-time stochastic model:

```python
P(t+dt) = P(t) + mean_reversion + volatility_shock + jump
```

Where:

- **Mean-Reversion**: `(100 - P(t)) × strength × dt`
- **Volatility Shock**: `N(0, regime.mult × max_vol × sqrt(dt))`
- **Jump**: Poisson process with magnitude `N(0, 0.5 × effective_vol)`
- **Clamping**: Result constrained to [10, 300] EUR/MWh

### Volatility Regimes

| Regime | Volatility Multiplier | Jump Probability Multiplier |
|--------|----------------------|---------------------------|
| LOW    | 0.5x                 | 1.0x                      |
| MEDIUM | 1.0x                 | 1.5x                      |
| HIGH   | 1.5x                 | 2.0x                      |

Regimes switch uniformly at random every 30 seconds.

## Testing

Run all tests:

```bash
pytest tests/
```

Run specific test module:

```bash
pytest tests/unit/test_engine.py -v
```

Run with coverage:

```bash
pytest tests/ --cov=src/power_simulator
```

### Test Coverage

- **40+ tests** including:
  - Parameter validation and clamping
  - Price generation mechanics
  - Mean-reversion behavior
  - Jump event occurrence
  - Full 180-second simulations
  - Chart visualization
  - Visual latency and performance

## Configuration

### Development

Edit `pyproject.toml` to manage dependencies:

```toml
dependencies = [
    "numpy>=1.24.0",
    "pandas>=2.0.0",
    "scipy>=1.10.0",
    "streamlit>=1.28.0",
    "plotly>=5.17.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]
```

## Performance

- **Price Generation**: <50ms per 0.2-second step
- **Chart Rendering**: <100ms visual latency
- **Memory**: ~150MB for full 180-second run
- **CPU**: ≤15% during simulation
