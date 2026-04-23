"""Core layer — timed interactive yes/no prompt with fallback."""

from __future__ import annotations

import sys
import threading

from .colours import BOLD, CYAN, DIM, WHITE, YELLOW, _c


class Prompter:
    """
    Displays a yes/no question and waits up to *timeout* seconds for a reply.
    If the user does not respond in time the configured *fallback* is returned.

    Cross-platform: uses a background reader thread so it works on both POSIX
    and Windows terminals.
    """

    def __init__(self, timeout: int = 15) -> None:
        self.timeout = timeout

    # ── public ────────────────────────────────────────────────────────────────

    def ask(self, question: str, fallback: str) -> str:
        """
        Print *question*, wait up to *timeout* seconds, then return either the
        user's answer or *fallback* (lowercased + stripped).
        """
        fallback_tag  = _c(YELLOW, f"[default: {fallback}]")
        prompt_line   = (
            f"\n  {_c(BOLD + CYAN, '?')}  {_c(WHITE, question)}\n"
            f"     {_c(DIM, f'Enter yes/no — auto-continues in {self.timeout}s')} "
            f"{fallback_tag}: "
        )

        answer = self._timed_input(prompt_line)

        if answer is None:
            print(_c(YELLOW, f"\n  ⏱  No response — using fallback: '{fallback}'"))
            return fallback.strip().lower()

        return answer.strip().lower()

    # ── private ───────────────────────────────────────────────────────────────

    def _timed_input(self, prompt: str) -> str | None:
        """Block for at most *self.timeout* seconds waiting for stdin input."""
        result: list[str | None] = [None]
        event  = threading.Event()

        def _reader() -> None:
            try:
                sys.stdout.write(prompt)
                sys.stdout.flush()
                line      = sys.stdin.readline()
                result[0] = line.rstrip("\n")
            except Exception:
                pass
            finally:
                event.set()

        thread = threading.Thread(target=_reader, daemon=True)
        thread.start()

        for remaining in range(self.timeout, 0, -1):
            if event.wait(timeout=1):
                break
            sys.stdout.write(f"\r  {_c(DIM, f'  ({remaining}s remaining)…')}    ")
            sys.stdout.flush()

        # Clear the countdown line
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()

        return result[0]
