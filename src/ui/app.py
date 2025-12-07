"""
Streamlit application for power price simulation.

This app provides a real-time visualization of simulated power spot prices
with mean-reversion, jumps, and volatility regimes. Users can control
parameters and watch prices evolve over 180 seconds with live updates.
"""

import time

import altair as alt
import pandas as pd
import streamlit as st

from power_simulator import (
    PriceSimulator,
    SimulationParameters,
    VolatilityRegime,
)


def initialize_session_state() -> None:
    """Initialize Streamlit session state with simulator and parameters."""
    if "simulator" not in st.session_state:
        default_params = SimulationParameters(
            max_volatility=15.0,
            mean_reversion_strength=0.05,
            jump_frequency=2.0,
        )
        st.session_state.simulator = PriceSimulator(default_params)
        st.session_state.is_running = False
        st.session_state.start_time = None
        st.session_state.paused_elapsed = 0.0
        st.session_state.params_locked = False


def format_regime_display(regime: VolatilityRegime) -> str:
    """Format regime for display with emoji indicator.

    Args:
        regime: VolatilityRegime value

    Returns:
        Formatted string with regime name and emoji
    """
    emoji_map = {
        VolatilityRegime.LOW: "🔵",
        VolatilityRegime.MEDIUM: "🟡",
        VolatilityRegime.HIGH: "🔴",
    }
    return f"{emoji_map.get(regime, '')} {regime.value}"


def main() -> None:
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Power Price Simulator",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("⚡ Power Spot Price Simulator")
    st.markdown("""
    Real-time spot price simulation with mean-reversion, jumps,
    and volatility regimes.
    """)

    initialize_session_state()

    # Sidebar controls
    st.sidebar.header("⚙️ Simulation Controls")

    # Parameter sliders
    st.sidebar.subheader("Price Parameters")

    # Disable sliders if simulation is running
    disabled = st.session_state.is_running

    max_volatility = st.sidebar.slider(
        "Maximum Volatility (EUR/MWh)",
        min_value=0,
        max_value=50,
        value=15,
        step=1,
        help="Scales the maximum price volatility. "
        "Higher = more price swings.",
        disabled=disabled,
        )

    mean_reversion = st.sidebar.slider(
        "Mean-Reversion Strength (per second)",
        min_value=0.01,
        max_value=0.5,
        value=0.05,
        step=0.01,
        format="%.2f",
        help="How strongly prices are pulled toward 100 EUR/MWh. "
        "Higher = faster reversion.",
        disabled=disabled,
        )

    jump_frequency = st.sidebar.slider(
        "Jump Frequency (per minute)",
        min_value=0.0,
        max_value=10.0,
        value=2.0,
        step=0.5,
        help="Average frequency of rare jump events. Higher = more jumps.",
        disabled=disabled,
    )

    # Update simulator with new parameters
    new_params = SimulationParameters(
        max_volatility=float(max_volatility),
        mean_reversion_strength=float(mean_reversion),
        jump_frequency=float(jump_frequency),
    )

    # Only reset if parameters changed
    if (new_params.max_volatility
            != st.session_state.simulator.parameters.max_volatility or
            new_params.mean_reversion_strength
            != st.session_state.simulator.parameters.mean_reversion_strength or
            new_params.jump_frequency
            != st.session_state.simulator.parameters.jump_frequency):
        st.session_state.simulator = PriceSimulator(new_params)
        st.session_state.is_running = False
        st.session_state.paused_elapsed = 0.0

    # Control buttons
    st.sidebar.subheader("Controls")
    col1, col2, col3 = st.sidebar.columns(3)

    with col1:
        if st.button("▶️ Start", width='stretch'):
            if not st.session_state.is_running:
                st.session_state.is_running = True
                st.session_state.start_time = time.time()
                if st.session_state.paused_elapsed > 0:
                    # Resume from pause - adjust start time
                    st.session_state.start_time -= (
                        st.session_state.paused_elapsed)

    with col2:
        if st.button("⏸️ Pause", width='stretch'):
            if st.session_state.is_running:
                st.session_state.is_running = False
                st.session_state.paused_elapsed = (
                    st.session_state.simulator
                    .get_current_state().elapsed_time)

    with col3:
        if st.button("🔄 Reset", width='stretch'):
            st.session_state.simulator.reset()
            st.session_state.is_running = False
            st.session_state.start_time = None
            st.session_state.paused_elapsed = 0.0

    # Main content area
    col_chart, col_info = st.columns([3, 1])

    # Prepare data for chart
    sim_state = st.session_state.simulator.get_current_state()
    price_data = pd.DataFrame({
        "Time": [p.timestamp for p in sim_state.price_history],
        "Price": [p.price for p in sim_state.price_history]
    })

    # Display chart with fixed axes using Altair
    with col_chart:
        chart = alt.Chart(price_data).mark_line(color="#0064C8").encode(
            x=alt.X(
                "Time",
                scale=alt.Scale(domain=[0, 180]),
                axis=alt.Axis(
                    values=[0, 30, 60, 90, 120, 150, 180],
                    title="Time (seconds)",
                    grid=True
                )
            ),
            y=alt.Y(
                "Price",
                scale=alt.Scale(domain=[0, 300]),
                axis=alt.Axis(
                    values=[0, 50, 100, 150, 200, 250, 300],
                    title="Price (EUR/MWh)",
                    grid=True
                )
            )
        ).properties(
            height=500
        )
        st.altair_chart(chart, use_container_width=True)

    # Display metrics - using keys to prevent flickering
    with col_info:
        # st.subheader("📊 Current Status")

        sim_state = st.session_state.simulator.get_current_state()

        # Current price
        st.metric(
            "Current Price",
            f"€{sim_state.current_price:.2f}",
            delta=None,
        )

        # Elapsed time / Progress
        elapsed = sim_state.elapsed_time
        progress = min(elapsed / 180.0, 1.0)
        st.progress(progress)
        st.caption(f"{elapsed:.1f}s / 180s")

        # Current regime with color coding
        regime = sim_state.regime
        regime_colors = {
            VolatilityRegime.LOW: "🔵",
            VolatilityRegime.MEDIUM: "🟡",
            VolatilityRegime.HIGH: "🔴",
        }
        st.markdown(
            f"**Regime:** {regime_colors.get(regime)} {regime.value}"
        )

        # Price points count
        st.metric(
            "Price Points",
            len(sim_state.price_history),
        )

        # Jump count
        jump_count = sum(
            1 for p in sim_state.price_history
            if p.jump_occurred
        )
        st.metric(
            "Jumps Detected",
            jump_count,
        )

    # Real-time simulation loop with explicit timing control
    if st.session_state.is_running:
        sim_state = st.session_state.simulator.get_current_state()

        if sim_state.elapsed_time < 180.0:
            # Measure execution time for timing control
            step_start = time.perf_counter()

            # Generate next price point
            _ = st.session_state.simulator.run_step()

            # Timing control: sleep to achieve 0.2s per step
            step_duration = time.perf_counter() - step_start
            target_time = 0.2  # 0.2 seconds per price point
            if step_duration < target_time:
                time.sleep(target_time - step_duration)

            # Trigger rerun to continue simulation
            st.rerun()
        else:
            # Simulation complete
            st.session_state.is_running = False
            st.success("✅ Simulation Complete! 180 seconds done.")

    # Footer
    st.sidebar.divider()
    st.sidebar.markdown("""
    ### ℹ️ About
    - **Price Range:** 10 - 300 EUR/MWh
    - **Mean Price:** 100 EUR/MWh (target for reversion)
    - **Regimes:** LOW (0.5x vol), MEDIUM (1.0x vol), HIGH (1.5x vol)
    - **Switches:** Every 30 seconds (random selection)
    - **Jumps:** Rare events with magnitude scaling by volatility
    """)


if __name__ == "__main__":
    main()
