"""Unit tests for SimulationParameters validation and defaults."""

import pytest
from src.power_simulator import SimulationParameters


class TestParameterValidation:
    """Test parameter validation and clamping."""

    def test_default_values(self) -> None:
        """Test that default parameters are initialized correctly."""
        params = SimulationParameters()

        assert params.max_volatility == 15.0
        assert params.mean_reversion_strength == 0.05
        assert params.jump_frequency == 2.0

    def test_volatility_clamping_negative(self) -> None:
        """Test that negative volatility is clamped to 0."""
        params = SimulationParameters(max_volatility=-5.0)
        assert params.max_volatility == 0.0

    def test_volatility_clamping_too_high(self) -> None:
        """Test that volatility > 50 is clamped to 50."""
        params = SimulationParameters(max_volatility=75.0)
        assert params.max_volatility == 50.0

    def test_volatility_valid_range(self) -> None:
        """Test that valid volatility values are preserved."""
        for vol in [0.0, 15.0, 25.0, 50.0]:
            params = SimulationParameters(max_volatility=vol)
            assert params.max_volatility == vol

    def test_mean_reversion_clamping_low(self) -> None:
        """Test that mean-reversion < 0.01 is clamped to 0.01."""
        params = SimulationParameters(mean_reversion_strength=0.001)
        assert params.mean_reversion_strength == 0.01

    def test_mean_reversion_clamping_high(self) -> None:
        """Test that mean-reversion > 0.5 is clamped to 0.5."""
        params = SimulationParameters(mean_reversion_strength=0.75)
        assert params.mean_reversion_strength == 0.5

    def test_mean_reversion_valid_range(self) -> None:
        """Test that valid mean-reversion values are preserved."""
        for strength in [0.01, 0.05, 0.1, 0.5]:
            params = SimulationParameters(mean_reversion_strength=strength)
            assert params.mean_reversion_strength == strength

    def test_jump_frequency_clamping_negative(self) -> None:
        """Test that negative jump frequency is clamped to 0."""
        params = SimulationParameters(jump_frequency=-1.0)
        assert params.jump_frequency == 0.0

    def test_jump_frequency_clamping_high(self) -> None:
        """Test that jump frequency > 5 is clamped to 5."""
        params = SimulationParameters(jump_frequency=10.0)
        assert params.jump_frequency == 5.0

    def test_jump_frequency_valid_range(self) -> None:
        """Test that valid jump frequency values are preserved."""
        for freq in [0.0, 1.0, 2.0, 5.0]:
            params = SimulationParameters(jump_frequency=freq)
            assert params.jump_frequency == freq

    def test_multiple_parameters_invalid(self) -> None:
        """Test clamping of multiple parameters simultaneously."""
        params = SimulationParameters(
            max_volatility=100.0,
            mean_reversion_strength=0.001,
            jump_frequency=-1.0,
        )

        assert params.max_volatility == 50.0
        assert params.mean_reversion_strength == 0.01
        assert params.jump_frequency == 0.0
