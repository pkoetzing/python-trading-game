"""
Pytest configuration and shared fixtures for power simulator tests.

This module provides:
- default_parameters(): SimulationParameters with sensible defaults
- numpy_seed(): Fixture for reproducible random number generation
- isolated_simulator(): Fresh PriceSimulator instance for each test
"""

import pytest
import numpy as np
from src.power_simulator import PriceSimulator, SimulationParameters


@pytest.fixture
def default_parameters() -> SimulationParameters:
    """Provide default simulation parameters.

    Returns:
        SimulationParameters with default values:
        - max_volatility: 15 EUR/MWh
        - mean_reversion_strength: 0.05 per second
        - jump_frequency: 2 per minute
    """
    return SimulationParameters(
        max_volatility=15.0,
        mean_reversion_strength=0.05,
        jump_frequency=2.0,
    )


@pytest.fixture
def numpy_seed() -> None:
    """Set numpy random seed for reproducible tests.

    Seeds with 42 for deterministic behavior across test runs.
    """
    np.random.seed(42)


@pytest.fixture
def isolated_simulator(default_parameters: SimulationParameters) -> PriceSimulator:
    """Create a fresh PriceSimulator instance for each test.

    Args:
        default_parameters: Fixture providing SimulationParameters

    Returns:
        Initialized PriceSimulator with default parameters
    """
    return PriceSimulator(default_parameters)
