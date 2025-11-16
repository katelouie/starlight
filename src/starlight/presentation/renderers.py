"""
Report Renderers

This module provides concrete renderer classes.
Each class knows how to format a single "report section"
(like a header or a table) into a specific output.
"""

from typing import Any

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# --- Rich (Pretty Terminal) Renderer ---


class RichReportRenderer:
    """Renders report sections using the 'rich' library."""

    def render_header(self, header_data: dict[str, Any]) -> Panel:
        """Renders the header as a rich Panel."""
        header_text = Text.assemble(
            (f"{header_data['name']}\n", "bold white"),
            (f"{header_data['datetime']}\n", "dim"),
            (f"{header_data['location']}\n", "dim"),
            (f"House System: {header_data['house_system']}", "dim italic"),
        )
        return Panel(
            header_text, title=header_data["title"], expand=False, padding=(1, 2)
        )

    def render_table(self, table_data: dict[str, Any]) -> Table:
        """Renders a data block as a rich Table."""
        table = Table(
            title=table_data.get("title"), title_style="bold magenta", padding=(0, 1)
        )

        for header in table_data.get("headers", []):
            justify = "right" if header in ("Position", "Orb") else "left"
            style = "bold cyan" if header in ("Object", "Angle", "Point") else ""
            table.add_column(header, justify=justify, style=style, no_wrap=True)

        for row in table_data.get("rows", []):
            table.add_row(*row)

        return table

    def render_group(self, renderables: list[Any]) -> Group:
        """Groups multiple rich renderables for printing."""
        return Group(*renderables)


class PlainTextReportRenderer:
    """
    Renders report sections as clean, plain-text strings.
    """

    def __init__(self, col_width: int = 18):
        self.col_width = col_width  # Simple width for alignment

    def _divider(self, char: str = "-") -> str:
        # Simple divider, can be made smarter
        return char * (self.col_width * 3 + 4)

    def render_header(self, header_data: Dict[str, Any]) -> str:
        """Renders the header as text."""
        lines = []
        lines.append(self._divider("="))
        lines.append(f"| {header_data['title'].upper()} |")
        lines.append(self._divider("="))
        lines.append(header_data["name"])
        lines.append(header_data["datetime"])
        lines.append(header_data["location"])
        lines.append(f"House System: {header_data['house_system']}")
        lines.append(self._divider())
        return "\n".join(lines)

    def render_table(self, table_data: Dict[str, Any]) -> str:
        """Renders a data block as a text table."""
        lines = []
        title = table_data.get("title")
        if title:
            lines.append(f"\n--- {title} ---")

        headers = table_data.get("headers", [])
        if not headers:
            return "\n".join(lines)

        num_cols = len(headers)

        # Header
        header_str = " | ".join(h.ljust(self.col_width) for h in headers)
        lines.append(header_str)
        lines.append("-" * len(header_str))

        # Rows
        for row in table_data.get("rows", []):
            # Truncate or pad each item in the row
            formatted_row = [
                str(item).ljust(self.col_width)[: self.col_width] for item in row
            ]
            row_str = " | ".join(formatted_row)
            lines.append(row_str)

        return "\n".join(lines)

    def render_group(self, renderables: List[str]) -> str:
        """Joins multiple text sections into a single string."""
        return "\n\n".join(renderables)
