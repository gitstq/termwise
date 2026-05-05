"""Theme system for TermWise TUI."""

from __future__ import annotations

from textual.design import ColorSystem
from textual.theme import Theme


def get_dark_theme() -> Theme:
    """Get the dark theme configuration."""
    return Theme(
        name="termwise_dark",
        primary="#58a6ff",
        secondary="#7ee787",
        accent="#d2a8ff",
        background="#0d1117",
        surface="#161b22",
        panel="#1c2128",
        dark=True,
    )


def get_light_theme() -> Theme:
    """Get the light theme configuration."""
    return Theme(
        name="termwise_light",
        primary="#0969da",
        secondary="#1a7f37",
        accent="#8250df",
        background="#ffffff",
        surface="#f6f8fa",
        panel="#eaeef2",
        dark=False,
    )


THEMES = {
    "dark": get_dark_theme(),
    "light": get_light_theme(),
}


def get_all_theme_names() -> list[str]:
    """Get all available theme names."""
    return list(THEMES.keys())


def get_theme(name: str) -> Theme:
    """Get a theme by name, falling back to dark."""
    return THEMES.get(name, THEMES["dark"])
