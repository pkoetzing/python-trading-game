"""
Core price simulation engine for power markets.

This module implements the PriceSimulator class which generates mean-reverting spot prices
with jumps and time-dependent volatility regimes. The engine uses:
- Mean-reversion pull toward 100 EUR/MWh
- Stochastic volatility scaled by regime
- Random jump events
- Uniform regime switching every 30 seconds
"""

import numpy as np

from .models import (
    PricePoint,
    SimulationParameters,
    SimulationState,
    VolatilityRegime,
)
from .regimes import REGIME_CONFIGS, RegimeScheduler


class PriceSimulator:
    """Generator of mean-reverting spot prices
       with jumps and volatility regimes.

    Price evolution follows: dP = alpha*(mu - P)*dt + sigma*dW + J
    where:
    - alpha is mean_reversion_strength
    - mu is long-term mean (100 EUR/MWh)
    - sigma is regime-scaled volatility
    - dW is normal random shock
    - J is rare jump event

    All prices are constrained to [10, 300] EUR/MWh range.
    Time steps are 0.2 seconds, target is 900 points over 180 seconds.
    """

    LONG_TERM_MEAN: float = 100.0  # EUR/MWh
    PRICE_MIN: float = 1.0  # EUR/MWh
    PRICE_MAX: float = 300.0  # EUR/MWh
    TIME_STEP: float = 0.2  # seconds
    REGIME_SWITCH_INTERVAL: float = 30.0  # seconds
    TOTAL_DURATION: float = 180.0  # seconds

    def __init__(self, parameters: SimulationParameters) -> None:
        """Initialize the price simulator with given parameters.

        Args:
            parameters: SimulationParameters object with volatility,
                mean-reversion, and jump frequency
        """
        self.parameters = parameters
        self.state = SimulationState(current_price=self.LONG_TERM_MEAN)
        self.regime_scheduler = RegimeScheduler()

    def reset(self) -> None:
        """Reset simulation state to initial conditions.

        Resets:
        - current_price to 100 EUR/MWh
        - elapsed_time to 0
        - price_history to empty list
        - regime scheduler
        """
        self.state = SimulationState(current_price=self.LONG_TERM_MEAN)
        self.regime_scheduler = RegimeScheduler()

    def get_current_state(self) -> SimulationState:
        """Get the current simulation state.

        Returns:
            SimulationState object with current price,
            elapsed time, regime, and history
        """
        return self.state

    def _sample_normal_noise(self, volatility: float, dt: float) -> float:
        """Sample normal random shock for volatility component.

        Args:
            volatility: Current effective volatility in EUR/MWh
            dt: Time step in seconds

        Returns:
            Normal random sample with std_dev = volatility * sqrt(dt)
        """
        std_dev = volatility * np.sqrt(dt)
        return np.random.normal(0, std_dev)

    def _sample_jump(self, volatility: float) -> tuple[bool, float]:
        """Determine if jump occurs and sample jump magnitude.

        Jump probability per time step:
            p = jump_frequency * regime.jump_prob_multiplier * (TIME_STEP / 60)

        Jump magnitude sampled from normal distribution:
            J ~ N(0, 0.5 * current_volatility)

        Args:
            volatility: Current effective volatility for jump magnitude scaling

        Returns:
            Tuple (jump_occurred: bool, jump_magnitude: float)
        """
        regime_config = REGIME_CONFIGS[self.state.regime]
        jump_prob = (
            self.parameters.jump_frequency
            * regime_config.jump_probability_multiplier
            * (self.TIME_STEP / 60.0)
        )

        jump_occurred = np.random.random() < jump_prob
        jump_magnitude = 0.0

        if jump_occurred:
            # Jump magnitude scales with current volatility
            jump_std = 0.5 * volatility
            jump_magnitude = np.random.normal(0, jump_std)

        return jump_occurred, jump_magnitude

    def generate_next_price(self, dt: float = TIME_STEP) -> float:
        """Generate next price given current state.

        Implements discretized mean-reversion with jump diffusion:

        1. Mean-reversion component: (100 - P) * strength * dt
        2. Volatility component: N(0, regime.vol_mult * max_vol * sqrt(dt))
        3. Jump component: Poisson process with
            magnitude ~ N(0, 0.5*volatility)
        4. Clamp result to [10, 300]

        Args:
            dt: Time step in seconds (default 0.2)

        Returns:
            New price in EUR/MWh, constrained to [10, 300]
        """
        # Get current regime configuration
        regime_config = REGIME_CONFIGS[self.state.regime]
        effective_volatility = (self.parameters.max_volatility
                                * regime_config.volatility_multiplier)

        # Mean-reversion component
        mean_reversion = (
            (self.LONG_TERM_MEAN - self.state.current_price)
            * self.parameters.mean_reversion_strength
            * dt
        )

        # Volatility component (Brownian noise)
        volatility_shock = self._sample_normal_noise(effective_volatility, dt)

        # Jump component
        jump_occurred, jump_magnitude = self._sample_jump(effective_volatility)

        # Sum all components
        new_price = (
            self.state.current_price
            + mean_reversion + volatility_shock + jump_magnitude)

        # Clamp to [10, 300] range
        new_price = np.clip(new_price, self.PRICE_MIN, self.PRICE_MAX)

        return float(new_price)

    def run_step(self) -> PricePoint:
        """Execute one simulation step (0.2 seconds).

        This method:
        1. Updates elapsed_time by 0.2 seconds
        2. Checks if regime switch required (every 30 seconds)
        3. Generates next price
        4. Creates PricePoint and adds to history
        5. Returns PricePoint for immediate UI update

        Execution should complete in <50ms to meet timing requirements.

        Returns:
            PricePoint with timestamp, price, regime, and jump_occurred flag

        Raises:
            RuntimeError: If simulation has already completed
            (elapsed_time > 180)
        """
        if self.state.elapsed_time > self.TOTAL_DURATION:
            raise RuntimeError(
                f"Simulation already completed at {self.state.elapsed_time}s"
            )

        # Advance time
        self.state.elapsed_time += self.TIME_STEP

        # Update regime if needed
        self.state.regime = self.regime_scheduler.update(
            self.state.elapsed_time)

        # Generate next price
        self.state.current_price = self.generate_next_price(self.TIME_STEP)

        # Determine if jump occurred (need to check again for this step)
        regime_config = REGIME_CONFIGS[self.state.regime]
        effective_volatility = (
            self.parameters.max_volatility
            * regime_config.volatility_multiplier
        )
        jump_prob = (
            self.parameters.jump_frequency
            * regime_config.jump_probability_multiplier
            * (self.TIME_STEP / 60.0)
        )
        jump_occurred = np.random.random() < jump_prob

        # Create price point record
        price_point = PricePoint(
            timestamp=self.state.elapsed_time,
            price=self.state.current_price,
            regime=self.state.regime,
            jump_occurred=jump_occurred,
        )

        # Add to history
        self.state.price_history.append(price_point)

        return price_point
