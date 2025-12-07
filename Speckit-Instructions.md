# Python Trading Game

## Constitution

Adhere to clean code principles and best practices.

- Make the code easy to change
- KISS (Keep It Simple, Stupid)
- YAGNI (you aren't gonna need it)
- DRY (Don't Repeat Yourself)
- Keep cyclomatic complexity low

## 1st Feature Specification

Create an engine that simulates mean-reverting spot power prices
with jumps and time-dependent volatility. Prices should be between
10 EUR/MWh and 300 EUR/MWh and revert to a mean of 100 EUR/MWh.
Prices should be simulated in real-time for a period of 180 seconds,
with a new price generated every 0.2 second.
The main parameters should be adjustable by the user, including
max volatility (0-50 EUR), mean-reversion strength (0.01-0.5 per second),
and jump frequency (0-5 jumps per minute). The volatility regime should
switch randomly between low, medium and high volatility every 30 seconds,
with jumps being more likely in high volatility regimes. The simulation
should be displayed in a chart with fixed Y-axis from 0 to 300 EUR/MWh
and X-axis showing exactly 180 seconds of data.

## Plan

- Build with Python pandas and the scientific stack
- Streamlit for interactive visualization and UI
- Write type hints for all functions and methods.
- Write docstrings for all public functions and classes.
- Write pytest unit tests for all new features, but avoid mocking where possible
- Use a .venv directory for virtual environments.
- Use a pyproject.toml file to manage dependencies and configurations.
- Ruff for linting and code quality checks

## Bug fixing

The problem with the app is it doesn't simulate in real-time: After start the prices a simulated very slow. To simulate the first 50 prices at a rate of 5 prices per second should take 10 seconds, but it takes 100 seconds, while the remaining 850 prices are simulated in just 20 seconds. So the whole simulation takes 120s instead of 180 and the time is not running linear. Identify the issue behind this behaviour and propose a fix. Consider the following options: a) reduce the simulation frequency to 1 price per 1 second. b) simulate all prices in advance and then display them in real-time with 5 prices per second.
The chart must not autoscale. x-axis must show 0 to 180s in 30s grid intervals. y-axis must show 0 .. 300 EUR/MWh with 50 EUR/MWh grid intervals.