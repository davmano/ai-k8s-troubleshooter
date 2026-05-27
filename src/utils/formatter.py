from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

console = Console()


def print_section(title: str, body: str, style: str = "cyan") -> None:
    console.print(Panel.fit(body, title=title, border_style=style))
