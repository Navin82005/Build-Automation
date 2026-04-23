"""Core layer — pretty, structured CLI logger."""

from __future__ import annotations

from datetime import datetime

from .colours import BLUE, BOLD, CYAN, DIM, GREEN, RED, WHITE, YELLOW, RESET, _c


class Logger:
    """Centralised, colour-coded CLI logger with banners, sections, and progress bars."""

    WIDTH = 72

    # ── timestamps ────────────────────────────────────────────────────────────

    @staticmethod
    def _ts() -> str:
        return datetime.now().strftime("%H:%M:%S")

    # ── structural ────────────────────────────────────────────────────────────

    @classmethod
    def banner(cls, showTime: bool = True) -> None:
        bar   = "═" * cls.WIDTH
        title = "BUILD  AUTOMATION"
        pad   = (cls.WIDTH - len(title)) // 2
        print(f"\n{_c(CYAN, bar)}")
        print(_c(CYAN, "║") + " " * pad + _c(BOLD + WHITE, title) + " " * pad + _c(CYAN, "║"))
        print(f"{_c(CYAN, bar)}\n")

    @classmethod
    def section(cls, title: str, showTime: bool = True) -> None:
        bar = "─" * cls.WIDTH
        print(f"\n{_c(BLUE, bar)}")
        print(f"  {_c(BOLD + CYAN, '▶  ' + title.upper())}")
        print(f"{_c(BLUE, bar)}")

    @classmethod
    def separator(cls, showTime: bool = True) -> None:
        print(f"\n  {_c(DIM, '·' * (cls.WIDTH - 4))}")

    @classmethod
    def result_box(cls, items: dict[str, str], showTime: bool = True) -> None:
        bar = "─" * cls.WIDTH
        print(f"\n{_c(GREEN, bar)}")
        print(f"  {_c(BOLD + GREEN, 'BUILD RESULT')}")
        print(f"{_c(GREEN, bar)}")
        for k, v in items.items():
            print(f"  {_c(DIM, k + ':'): <26} {_c(WHITE, v)}")
        print(f"{_c(GREEN, bar)}\n")

    # ── step progress ─────────────────────────────────────────────────────────

    @classmethod
    def step(cls, idx: int, total: int, label: str, showTime: bool = True) -> None:
        pct    = int((idx / total) * 100)
        filled = int(pct / 5)
        bar    = _c(GREEN, "█" * filled) + _c(DIM, "░" * (20 - filled))
        print(f"\n  [{bar}{RESET}] {_c(BOLD, f'{pct:>3}%')}  Step {idx}/{total}: {_c(WHITE, label)}")

    # ── log levels ────────────────────────────────────────────────────────────

    @classmethod
    def info(cls, msg: str, showTime: bool = True) -> None:
        print(f"  {_c(DIM, cls._ts()) if showTime else ''}  {_c(CYAN, '›')}  {msg}")

    @classmethod
    def success(cls, msg: str, showTime: bool = True) -> None:
        print(f"  {_c(DIM, cls._ts()) if showTime else ''}  {_c(GREEN, '✔')}  {_c(GREEN, msg)}")

    @classmethod
    def warning(cls, msg: str, showTime: bool = True) -> None:
        print(f"  {_c(DIM, cls._ts()) if showTime else ''}  {_c(YELLOW, '⚠')}  {_c(YELLOW, msg)}")

    @classmethod
    def error(cls, msg: str, showTime: bool = True) -> None:
        print(f"  {_c(DIM, cls._ts()) if showTime else ''}  {_c(RED, '✖')}  {_c(RED, msg)}")

    @classmethod
    def command(cls, cmd: str, showTime: bool = True) -> None:
        from .colours import MAGENTA
        print(f"\n  {_c(DIM, '$ ')}{_c(MAGENTA, cmd)}")
    
    @classmethod
    def menu(
        cls,
        title: str,
        items: list[tuple[str, str]],
        usage: str | None = None,
        footer: str | None = None,
        showTime: bool = True,
    ) -> None:
        bar = "─" * cls.WIDTH

        # Header
        print(f"\n{_c(BLUE, bar)}")
        print(f"  {_c(BOLD + CYAN, title.upper())}")
        print(f"{_c(BLUE, bar)}")

        # Usage
        if usage:
            print(f"\n  {_c(BOLD + WHITE, 'Usage:')} {usage}")

        # Items
        if items:
            print(f"\n  {_c(BOLD + WHITE, 'Options:')}")
            width = max(len(name) for name, _ in items) + 4

            for name, desc in items:
                print(
                    f"    {_c(CYAN, name):<{width}}"
                    f"{_c(WHITE, desc)}"
                )

        # Footer
        if footer:
            print(f"\n  {_c(DIM, footer)}")

        print("")