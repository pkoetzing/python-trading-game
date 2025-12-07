"""
Quick validation script to test the fixed real-time simulation.
"""

import time
from src.power_simulator import PriceSimulator, SimulationParameters


def test_simulation_speed():
    """Verify the simulation runs at the correct speed with timing control."""
    params = SimulationParameters(
        max_volatility=15.0,
        mean_reversion_strength=0.05,
        jump_frequency=2.0,
    )

    simulator = PriceSimulator(params)

    print("Testing real-time simulation with 0.2s timing control...")
    print("=" * 60)

    start_time = time.time()

    # Simulate with timing control (as Streamlit app does)
    for i in range(900):
        step_start = time.perf_counter()

        # Run one step
        price_point = simulator.run_step()

        # Simulate UI rendering (assume ~20ms)
        time.sleep(0.01)

        # Calculate timing control
        step_duration = time.perf_counter() - step_start
        target_time = 0.2
        if step_duration < target_time:
            time.sleep(target_time - step_duration)

        # Print progress at key intervals
        if (i + 1) % 100 == 0:
            elapsed = time.time() - start_time
            sim_time = simulator.get_current_state().elapsed_time
            print(f"Step {i+1:3d}: {elapsed:6.1f}s elapsed, "
                  f"{sim_time:6.1f}s sim time, "
                  f"price: €{price_point.price:.2f}")

    total_time = time.time() - start_time

    print("\n" + "=" * 60)
    print(f"Total execution time: {total_time:.1f}s")
    print(f"Expected time: 180.0s")
    print(f"Status: {'✓ PASS' if 170 <= total_time <= 190 else '✗ FAIL'}")
    print("=" * 60)

    state = simulator.get_current_state()
    print(f"\nFinal state:")
    print(f"  Price points: {len(state.price_history)}")
    print(f"  Simulation time: {state.elapsed_time:.1f}s")
    print(f"  Current price: €{state.current_price:.2f}")
    print(f"  Jumps detected: {sum(1 for p in state.price_history if p.jump_occurred)}")


if __name__ == "__main__":
    test_simulation_speed()
