"""Unit tests for PriceSimulator engine."""

import time
import pytest
import numpy as np
from src.power_simulator import (
    PriceSimulator,
    SimulationParameters,
    VolatilityRegime,
)


class TestEngineInitialization:
    """Test PriceSimulator initialization and reset."""

    def test_init_sets_defaults(self, default_parameters) -> None:
        """Test that initialization sets correct default state."""
        sim = PriceSimulator(default_parameters)
        state = sim.get_current_state()

        assert state.current_price == 100.0
        assert state.elapsed_time == 0.0
        assert state.regime == VolatilityRegime.MEDIUM
        assert len(state.price_history) == 0

    def test_reset_clears_state(self, default_parameters) -> None:
        """Test that reset() returns simulator to initial state."""
        sim = PriceSimulator(default_parameters)

        # Run a few steps
        for _ in range(5):
            sim.run_step()

        state = sim.get_current_state()
        assert state.elapsed_time > 0.0
        assert len(state.price_history) > 0

        # Reset
        sim.reset()
        state = sim.get_current_state()

        assert state.current_price == 100.0
        assert state.elapsed_time == 0.0
        assert len(state.price_history) == 0


class TestPriceGeneration:
    """Test price generation mechanics."""

    def test_generate_next_price_returns_float(self, isolated_simulator) -> None:
        """Test that generate_next_price returns a float."""
        price = isolated_simulator.generate_next_price()
        assert isinstance(price, float)

    def test_price_within_bounds(self, isolated_simulator) -> None:
        """Test that generated prices stay within [10, 300] range."""
        for _ in range(100):
            price = isolated_simulator.generate_next_price()
            assert 10.0 <= price <= 300.0

    def test_price_clamping_high_volatility(self, default_parameters) -> None:
        """Test that prices clamp correctly even with high volatility."""
        # Use very high volatility to force extreme prices
        params = SimulationParameters(
            max_volatility=50.0,
            mean_reversion_strength=0.01,  # Weak reversion
            jump_frequency=5.0,  # Frequent jumps
        )
        sim = PriceSimulator(params)
        sim.state.current_price = 290.0  # Near max

        for _ in range(10):
            price = sim.generate_next_price()
            assert 10.0 <= price <= 300.0, f"Price {price} out of bounds"

    def test_mean_reversion_pull(self, default_parameters) -> None:
        """Test that mean-reversion pulls price toward 100.

        With strong mean-reversion and low volatility, price should drift
        toward 100 EUR/MWh over time.
        """
        params = SimulationParameters(
            max_volatility=0.5,  # Minimal noise
            mean_reversion_strength=0.2,  # Strong reversion
            jump_frequency=0.0,  # No jumps
        )
        sim = PriceSimulator(params)
        sim.state.current_price = 50.0

        # Generate 10 prices starting from 50
        prices = [50.0]
        for _ in range(10):
            price = sim.generate_next_price()
            prices.append(price)

        # Last price should be higher than first (pulled toward 100)
        assert prices[-1] > prices[0]
        # Trend should be monotonic toward 100 (allow some noise)
        assert prices[-1] < 100.0  # Should not overshoot


class TestRunStep:
    """Test run_step() method."""

    def test_run_step_advances_time(self, isolated_simulator) -> None:
        """Test that run_step() advances elapsed time by 0.2 seconds."""
        price_point = isolated_simulator.run_step()

        assert price_point.timestamp == 0.2
        assert isolated_simulator.get_current_state().elapsed_time == 0.2

    def test_run_step_returns_price_point(self, isolated_simulator) -> None:
        """Test that run_step() returns a valid PricePoint."""
        price_point = isolated_simulator.run_step()

        assert price_point.timestamp > 0.0
        assert 10.0 <= price_point.price <= 300.0
        assert price_point.regime in [
            VolatilityRegime.LOW,
            VolatilityRegime.MEDIUM,
            VolatilityRegime.HIGH,
        ]
        assert isinstance(price_point.jump_occurred, bool)

    def test_run_step_adds_to_history(self, isolated_simulator) -> None:
        """Test that run_step() adds to price history."""
        isolated_simulator.run_step()

        state = isolated_simulator.get_current_state()
        assert len(state.price_history) == 1

        isolated_simulator.run_step()

        state = isolated_simulator.get_current_state()
        assert len(state.price_history) == 2

    def test_run_step_timing(self, isolated_simulator) -> None:
        """Test that run_step() completes within timing budget (<50ms).

        SC-001 requires ±50ms tolerance on 180-second duration.
        Each step should be <50ms to accumulate timing budget.
        """
        start = time.time()
        isolated_simulator.run_step()
        elapsed = time.time() - start

        # Allow generous margin; actual should be much faster
        assert elapsed < 0.05, f"run_step took {elapsed:.4f}s, should be <50ms"

    def test_run_step_sequence(self, isolated_simulator) -> None:
        """Test that consecutive run_step() calls produce valid sequence."""
        for i in range(10):
            price_point = isolated_simulator.run_step()

            # Each timestamp should be 0.2 * (i+1)
            expected_time = 0.2 * (i + 1)
            assert abs(price_point.timestamp - expected_time) < 0.001


class TestBoundaryConditions:
    """Test behavior at price boundaries."""

    def test_price_at_minimum_bound(self, default_parameters) -> None:
        """Test behavior when price hits minimum (10 EUR/MWh)."""
        sim = PriceSimulator(default_parameters)
        sim.state.current_price = 10.0

        for _ in range(5):
            price = sim.generate_next_price()
            assert price >= 10.0

    def test_price_at_maximum_bound(self, default_parameters) -> None:
        """Test behavior when price hits maximum (300 EUR/MWh)."""
        sim = PriceSimulator(default_parameters)
        sim.state.current_price = 300.0

        for _ in range(5):
            price = sim.generate_next_price()
            assert price <= 300.0

    def test_mean_reversion_at_bounds(self, default_parameters) -> None:
        """Test that mean-reversion pulls prices away from bounds."""
        params = SimulationParameters(
            max_volatility=5.0,
            mean_reversion_strength=0.2,
            jump_frequency=0.0,
        )

        # Test from low bound
        sim = PriceSimulator(params)
        sim.state.current_price = 10.0
        price1 = sim.generate_next_price()
        assert price1 >= 10.0  # Should not go lower (mean reversion pulls up)

        # Test from high bound
        sim.state.current_price = 300.0
        price2 = sim.generate_next_price()
        assert price2 <= 300.0  # Should not go higher (mean reversion pulls down)
