"""
Power Simulator: Mean-reverting spot price simulation with jumps and volatility regimes.

This package provides a complete simulation engine for generating realistic power
spot prices with the following characteristics:
- Mean-reversion to 100 EUR/MWh
- Stochastic volatility scaled by regime (LOW/MEDIUM/HIGH)
- Random jump events
- Uniform regime switching every 30 seconds
- 900 price points over 180 seconds (0.2 second intervals)

Main classes:
- PriceSimulator: Core engine for price generation
- SimulationParameters: Configuration parameters
- PricePoint: Individual price observation
- VolatilityRegime: Regime enumeration (LOW, MEDIUM, HIGH)
"""

from .engine import PriceSimulator
from .models import (
    SimulationParameters,
    SimulationState,
    PricePoint,
    VolatilityRegime,
)
from .regimes import RegimeScheduler, RegimeConfig, REGIME_CONFIGS

__version__ = "0.1.0"
__all__ = [
    "PriceSimulator",
    "SimulationParameters",
    "SimulationState",
    "PricePoint",
    "VolatilityRegime",
    "RegimeScheduler",
    "RegimeConfig",
    "REGIME_CONFIGS",
]
