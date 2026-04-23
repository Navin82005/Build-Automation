"""ANSI colour constants and the _c() helper used across the package."""

RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
CYAN    = "\033[96m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
RED     = "\033[91m"
MAGENTA = "\033[95m"
WHITE   = "\033[97m"
BLUE    = "\033[94m"


def _c(colour: str, text: str) -> str:
    """Wrap *text* in an ANSI escape sequence that resets afterwards."""
    return f"{colour}{text}{RESET}"
