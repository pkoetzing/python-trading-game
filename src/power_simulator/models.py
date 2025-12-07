"""
Data models for power price simulation.

This module defines the core dataclasses used throughout the simulation:
- SimulationParameters: Configuration for the price simulator
- PricePoint: Individual price data point with metadata
- SimulationState: Complete state of the ongoing simulation
"""

from dataclasses import dataclass, field
from enum import Enum


class VolatilityRegime(str, Enum):
    """Enumeration of volatility regimes affecting price behavior.

    Each regime has:
    - volatility_multiplier: Scales max_volatility parameter
        (e.g., 0.5x, 1.0x, 1.5x)
    - jump_probability_multiplier: Scales jump frequency
        (e.g., 1.0x, 1.5x, 2.0x)
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class SimulationParameters:
    """Configuration parameters for the price simulation engine.

    Attributes:
        max_volatility: Maximum volatility in EUR/MWh, range [0, 50].
            Default 15.
        mean_reversion_strength: Strength of mean reversion pull,
            range [0.01, 0.5] per second. Default 0.05.
        jump_frequency: Average jump events per minute, range [0, 5].
            Default 2.
    """

    max_volatility: float = 15.0
    mean_reversion_strength: float = 0.05
    jump_frequency: float = 2.0

    def __post_init__(self) -> None:
        """Validate parameters are within acceptable ranges."""
        self.max_volatility = max(0.0, min(50.0, self.max_volatility))
        self.mean_reversion_strength = max(
            0.01, min(0.5, self.mean_reversion_strength))
        self.jump_frequency = max(0.0, min(5.0, self.jump_frequency))


@dataclass
class PricePoint:
    """Single price observation with metadata.

    Attributes:
        timestamp: Elapsed time in seconds since simulation start.
        price: Current spot price in EUR/MWh, range [10, 300].
        regime: Current volatility regime (LOW, MEDIUM, HIGH).
        jump_occurred: Whether a jump event occurred in this step.
    """

    timestamp: float
    price: float
    regime: VolatilityRegime
    jump_occurred: bool = False


@dataclass
class SimulationState:
    """Complete state of an ongoing price simulation.

    Attributes:
        current_price: Current spot price in EUR/MWh.
        elapsed_time: Time elapsed in seconds (increments by 0.2s per step).
        regime: Current volatility regime.
        regime_switch_time: Time when regime was last switched (seconds).
        price_history: List of all PricePoint observations so far.
    """

    current_price: float = 100.0
    elapsed_time: float = 0.0
    regime: VolatilityRegime = VolatilityRegime.MEDIUM
    regime_switch_time: float = 0.0
    price_history: list[PricePoint] = field(default_factory=list)
