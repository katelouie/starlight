"""
Output renderers for reports.

Renderers take structured data from sections and format it for different
output mediums (terminal with Rich, plain text, PDF, HTML, etc.).
"""

from typing import Any

try:
    from rich.console import Console
    from rich.table import Table
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class RichTableRenderer:
    """
    Renderer using the Rich library for beautiful terminal output.

    Requires: pip install rich

    Features:
    - Colored tables with borders
    - Automatic column width adjustment
    - Unicode box characters
    """

    def __init__(self) -> None:
        """Initialize Rich renderer."""
        if not RICH_AVAILABLE:
            raise ImportError(
                "Rich library not available. Install with: pip install rich"
            )

        # Use record=True to properly capture styled output
        self.console = Console(record=True)

    def render_section(self, section_name: str, section_data: dict[str, Any]) -> str:
        """Render a single section with Rich."""
        data_type = section_data.get("type")

        if data_type == "table":
            return self._render_table(section_name, section_data)
        elif data_type == "key_value":
            return self._render_key_value(section_name, section_data)
        elif data_type == "text":
            return self._render_text(section_name, section_data)
        else:
            return f"Unknown section type: {data_type}"

    def print_report(self, sections: list[tuple[str, dict[str, Any]]]) -> None:
        """
        Print report directly to terminal with Rich formatting.

        This method prints the report with full ANSI colors and styling,
        intended for immediate terminal display.
        """
        # Create a fresh console for direct printing (no recording)
        console = Console()

        for section_name, section_data in sections:
            # Print section header
            console.print(f"\n{section_name}", style="bold cyan")
            console.print("─" * len(section_name), style="cyan")

            # Print section content based on type
            data_type = section_data.get("type")

            if data_type == "table":
                self._print_table(console, section_data)
            elif data_type == "key_value":
                self._print_key_value(console, section_data)
            elif data_type == "text":
                console.print(section_data.get("text", ""))
            else:
                console.print(f"Unknown section type: {data_type}")

    def render_report(self, sections: list[tuple[str, dict[str, Any]]]) -> str:
        """
        Render complete report to plaintext string (ANSI codes stripped).

        Used for file output and testing.
        Returns clean text without ANSI escape codes.
        """
        output_parts = []

        for section_name, section_data in sections:
            # Render section header
            header = Text(f"\n{section_name}", style="bold cyan")
            output_parts.append(header)
            output_parts.append(Text("─" * len(section_name), style="cyan"))

            # Render section content
            content = self.render_section(section_name, section_data)
            output_parts.append(content)

        # Render all parts
        for part in output_parts:
            if isinstance(part, str):
                self.console.print(part)
            else:
                self.console.print(part)

        # Export as plain text (strips ANSI codes for file output)
        return self.console.export_text()

    def _render_table(self, section_name: str, data: dict[str, Any]) -> str:
        """Render table data with Rich."""
        table = Table(title=None, show_header=True, header_style="bold magenta")

        # Add columns
        for header in data["headers"]:
            table.add_column(header)

        # Add rows
        for row in data["rows"]:
            # Convert all values to strings
            str_row = [str(cell) for cell in row]
            table.add_row(*str_row)

        with self.console.capture() as capture:
            self.console.print(table)

        return capture.get()

    def _render_key_value(self, section_name: str, data: dict[str, Any]) -> str:
        """Render key-value data."""
        output = []

        for key, value in data["data"].items():
            # Format: "Key: Value" with key in bold
            line = Text()
            line.append(f"{key}: ", style="bold")
            line.append(str(value))
            output.append(line)

        with self.console.capture() as capture:
            for line in output:
                self.console.print(line)

        return capture.get()

    def _render_text(self, section_name: str, data: dict[str, Any]) -> str:
        """Render plain text block."""
        return data.get("text", "")

    def _print_table(self, console: Console, data: dict[str, Any]) -> None:
        """Print table directly to console with Rich formatting."""
        table = Table(title=None, show_header=True, header_style="bold magenta")

        # Add columns
        for header in data["headers"]:
            table.add_column(header)

        # Add rows
        for row in data["rows"]:
            # Convert all values to strings
            str_row = [str(cell) for cell in row]
            table.add_row(*str_row)

        console.print(table)

    def _print_key_value(self, console: Console, data: dict[str, Any]) -> None:
        """Print key-value pairs directly to console with Rich formatting."""
        for key, value in data["data"].items():
            # Format: "Key: Value" with key in bold
            line = Text()
            line.append(f"{key}: ", style="bold")
            line.append(str(value))
            console.print(line)


class PlainTextRenderer:
    """
    Plain text renderer with no dependencies.

    Creates simple ASCII tables and formatted text suitable for:
    - Log files
    - Email
    - Systems without Rich library
    - Piping to other tools
    """

    def render_section(self, section_name: str, section_data: dict[str, Any]) -> str:
        """Render a single section as plain text."""
        data_type = section_data.get("type")

        if data_type == "table":
            return self._render_table(section_name, section_data)
        elif data_type == "key_value":
            return self._render_key_value(section_name, section_data)
        elif data_type == "text":
            return section_data.get("text", "")
        else:
            return f"Unknown section type: {data_type}"

    def render_report(self, sections: list[tuple[str, dict[str, Any]]]) -> str:
        """Render complete report as plain text."""
        parts = []

        for section_name, section_data in sections:
            # Section header
            parts.append(f"\n{section_name}")
            parts.append("=" * len(section_name))

            # Section content
            content = self.render_section(section_name, section_data)
            parts.append(content)
            parts.append("")  # Blank line between sections

        return "\n".join(parts)

    def _render_table(self, section_name: str, data: dict[str, Any]) -> str:
        """
        Render ASCII table.

        Algorithm:
        1. Calculate column widths based on content
        2. Create header row with separators
        3. Create data rows
        4. Use | and - for borders
        """
        headers = data["headers"]
        rows = data["rows"]

        # Convert all cells to strings
        str_rows = [[str(cell) for cell in row] for row in rows]

        # Calculate column widths
        col_widths = []
        for i, header in enumerate(headers):
            # Start with header width
            width = len(header)

            # Check all row values
            for row in str_rows:
                if i < len(row):
                    width = max(width, len(row[i]))

            col_widths.append(width)

        # Build table
        lines = []

        # Header row
        header_cells = [h.ljust(w) for h, w in zip(headers, col_widths)]
        lines.append("| " + " | ".join(header_cells) + " |")

        # Separator
        separator_cells = ["-" * w for w in col_widths]
        lines.append("|-" + "-|-".join(separator_cells) + "-|")

        # Data rows
        for row in str_rows:
            # Pad row if needed
            padded_row = row + [""] * (len(headers) - len(row))

            row_cells = [cell.ljust(w) for cell, w in zip(padded_row, col_widths)]
            lines.append("| " + " | ".join(row_cells) + " |")

        return "\n".join(lines)

    def _render_key_value(self, section_name: str, data: dict[str, Any]) -> str:
        """Render key-value pairs."""
        lines = []

        # Find longest key for alignment
        max_key_len = max(len(k) for k in data["data"].keys())

        for key, value in data["data"].items():
            # Right-align keys for neat columns
            lines.append(f"{key.rjust(max_key_len)}: {value}")

        return "\n".join(lines)
