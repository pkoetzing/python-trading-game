"""Entry point for power simulator application."""

import subprocess
import sys


def main() -> None:
    """Run the Streamlit application."""
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "src/ui/app.py",
            "--server.port=8502",
        ],
        check=False,
    )


if __name__ == "__main__":
    main()
