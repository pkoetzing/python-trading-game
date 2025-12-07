"""
Volatility regime management for power price simulation.

This module handles regime switching and provides configuration for each regime's
impact on price generation (volatility multipliers and jump probability multipliers).
"""

import numpy as np

from .models import VolatilityRegime


class RegimeConfig:
    """Configuration for a volatility regime.

    Attributes:
        volatility_multiplier: Multiplier applied to max_volatility
        (0.5 for LOW, 1.0 for MEDIUM, 1.5 for HIGH)
        jump_probability_multiplier: Multiplier applied to jump_frequency
        (1.0 for LOW, 1.5 for MEDIUM, 2.0 for HIGH)
    """

    def __init__(
            self, volatility_multiplier: float,
            jump_probability_multiplier: float) -> None:
        self.volatility_multiplier = volatility_multiplier
        self.jump_probability_multiplier = jump_probability_multiplier


# Regime configuration mapping
REGIME_CONFIGS: dict[VolatilityRegime, RegimeConfig] = {
    VolatilityRegime.LOW: RegimeConfig(
        volatility_multiplier=0.5, jump_probability_multiplier=1.0),
    VolatilityRegime.MEDIUM: RegimeConfig(
        volatility_multiplier=1.0, jump_probability_multiplier=1.5),
    VolatilityRegime.HIGH: RegimeConfig(
        volatility_multiplier=1.5, jump_probability_multiplier=2.0),
}


class RegimeScheduler:
    """Manages volatility regime switching for the simulation.

    Regimes switch uniformly at random every 30 seconds.
    Each regime (LOW, MEDIUM, HIGH)
    has equal 33% probability of selection.
    """

    REGIME_SWITCH_INTERVAL: float = 30.0  # seconds

    def __init__(self) -> None:
        """Initialize regime scheduler with random starting regime."""
        self.current_regime = self._select_random_regime()
        self.last_switch_time = 0.0

    def _select_random_regime(self) -> VolatilityRegime:
        """Select a random regime with uniform probability (33% each).

        Returns:
            Randomly selected VolatilityRegime (LOW, MEDIUM, or HIGH)
        """
        regimes = list(VolatilityRegime)
        # Use randint to select index instead of choice
        # to avoid numpy string issues
        idx = np.random.randint(0, len(regimes))
        return regimes[idx]

    def update(self, elapsed_time: float) -> VolatilityRegime:
        """Update regime if switch interval has elapsed.

        Checks if 30 seconds have passed since last regime switch.
        If so, selects a new random regime and updates last_switch_time.

        Args:
            elapsed_time: Current elapsed time in seconds

        Returns:
            Current regime (updated or unchanged)
        """
        if elapsed_time - self.last_switch_time >= self.REGIME_SWITCH_INTERVAL:
            self.current_regime = self._select_random_regime()
            self.last_switch_time = elapsed_time

        return self.current_regime

    def get_regime(self) -> VolatilityRegime:
        """Get the current regime without updating.

        Returns:
            Current VolatilityRegime
        """
        return self.current_regime

    def get_config(
            self, regime: VolatilityRegime | None = None) -> RegimeConfig:
        """Get configuration for a specific regime.

        Args:
            regime: VolatilityRegime to get config for
                (defaults to current regime)

        Returns:
            RegimeConfig with volatility and jump probability multipliers
        """
        if regime is None:
            regime = self.current_regime
        return REGIME_CONFIGS[regime]
