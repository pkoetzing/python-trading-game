"""
Test script to validate real-time simulation timing behavior.

This script runs a standalone simulation (without Streamlit UI) to measure
the actual timing of the engine and validate that it completes in ~180s
with linear progression.
"""

import time

from src.power_simulator import PriceSimulator, SimulationParameters


def measure_simulation_timing():
    """Run simulation and measure timing at various intervals."""
    params = SimulationParameters(
        max_volatility=15.0,
        mean_reversion_strength=0.05,
        jump_frequency=2.0,
    )

    simulator = PriceSimulator(params)

    print("Starting simulation timing test...")
    print("=" * 60)

    # Test iterations: measure timing at specific points
    test_steps = [50, 100, 250, 500, 750, 900]
    timing_samples = {}

    start_time = time.perf_counter()
    step_times = []

    for i in range(900):
        step_start = time.perf_counter()
        simulator.run_step()
        step_duration = time.perf_counter() - step_start

        step_times.append(step_duration)

        # Record timing at test steps
        if (i + 1) in test_steps:
            elapsed = time.perf_counter() - start_time
            sim_time = simulator.get_current_state().elapsed_time
            timing_samples[i + 1] = {
                "wall_clock": elapsed,
                "sim_time": sim_time,
                "step_duration": step_duration,
            }

    total_time = time.perf_counter() - start_time

    print(f"\n{'Step':<8} {'Wall Time (s)':<15} {'Sim Time (s)':<15} "
          f"{'Step Dur (ms)':<15}")
    print("-" * 60)

    for step, data in timing_samples.items():
        dur_ms = data['step_duration'] * 1000
        print(f"{step:<8} {data['wall_clock']:<15.3f} "
              f"{data['sim_time']:<15.3f} "
              f"{dur_ms:<15.2f}")

    print("\n" + "=" * 60)
    print(f"Total simulation time: {total_time:.2f}s (target: 180s)")
    print(f"Expected simulation time: {900 * 0.2:.2f}s (900 steps x 0.2s)")
    avg_dur = (sum(step_times) / len(step_times)) * 1000
    min_dur = min(step_times) * 1000
    max_dur = max(step_times) * 1000
    print(f"Average step duration: {avg_dur:.2f}ms")
    print(f"Min step duration: {min_dur:.2f}ms")
    print(f"Max step duration: {max_dur:.2f}ms")

    # Check linearity
    print("\n" + "=" * 60)
    print("Timing Linearity Analysis:")
    print("-" * 60)

    expected_vs_actual = []
    for step, data in timing_samples.items():
        expected_time = step * 0.2
        actual_time = data["wall_clock"]
        deviation = actual_time - expected_time
        percentage = (deviation / expected_time) * 100
        expected_vs_actual.append((step, expected_time, actual_time,
                                   deviation, percentage))
        print(f"Step {step:3d}: Expected {expected_time:7.1f}s, "
              f"Got {actual_time:7.2f}s, "
              f"Deviation {deviation:+6.2f}s ({percentage:+6.1f}%)")

    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("-" * 60)
    max_deviation = max(abs(dev) for _, _, _, dev, _ in expected_vs_actual)
    avg_deviation = sum(abs(dev) for _, _, _, dev, _ in expected_vs_actual
                        ) / len(expected_vs_actual)

    print(f"Max deviation: {max_deviation:.2f}s")
    print(f"Average deviation: {avg_deviation:.2f}s")

    # Specification compliance
    print("\n" + "=" * 60)
    print("Specification Compliance Check (SC-001, FR-014, SC-007):")
    print("-" * 60)

    # SC-001: Total time within ±10s of 180s
    time_ok = 170 <= total_time <= 190
    print(f"SC-001 (180s ±10s): {total_time:.2f}s "
          f"{'✓ PASS' if time_ok else '✗ FAIL'}")

    # FR-014: Per-step latency <=50ms (avg)
    avg_step = sum(step_times) / len(step_times)
    latency_ok = avg_step <= 0.05
    latency_ms = avg_step * 1000
    print(f"FR-014 (<=50ms avg latency): {latency_ms:.2f}ms "
          f"{'✓ PASS' if latency_ok else '✗ FAIL'}")

    # SC-007: Max timing variance acceptable
    max_step = max(step_times)
    variance_ok = max_step <= 0.1  # Allow 100ms max per step
    max_step_ms = max_step * 1000
    print(f"SC-007 (<=100ms max per step): {max_step_ms:.2f}ms "
          f"{'✓ PASS' if variance_ok else '✗ FAIL'}")

    # Linearity check
    linearity_ok = avg_deviation <= 1.0  # Allow 1s average deviation
    print(f"Linearity (≤1s avg deviation): {avg_deviation:.2f}s "
          f"{'✓ PASS' if linearity_ok else '✗ FAIL'}")

    overall = time_ok and latency_ok and variance_ok and linearity_ok
    print("\n" + "=" * 60)
    result_msg = "✓ ALL TESTS PASSED" if overall else "✗ SOME TESTS FAILED"
    print(f"Overall: {result_msg}")
    print("=" * 60)

    return overall


if __name__ == "__main__":
    success = measure_simulation_timing()
    exit(0 if success else 1)
