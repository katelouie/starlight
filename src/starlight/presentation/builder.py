"""
Report builder for creating chart reports.

The builder pattern allows users to progressively construct reports
by adding sections one at a time, then rendering in their chosen format.
"""

from typing import Any

from starlight.core.models import CalculatedChart
from starlight.core.protocols import ReportRenderer, ReportSection

from .renderers import PlainTextRenderer, RichTableRenderer
from .sections import (
    AspectSection,
    ChartOverviewSection,
    MidpointSection,
    PlanetPositionSection,
)


class ReportBuilder:
    """
    Builder for chart reports.

    Usage:
        report = (
            ReportBuilder()
            .from_chart(chart)
            .with_chart_overview()
            .with_planet_positions()
            .render(format="rich_table")
        )
    """

    def __init__(self) -> None:
        """Initialize an empty report builder."""
        self._chart: CalculatedChart | None = None
        self._sections: list[ReportSection] = []

    def from_chart(self, chart: CalculatedChart) -> "ReportBuilder":
        """
        Set the chart to generate reports from.

        Args:
            chart: A CalculatedChart from ChartBuilder

        Returns:
            Self for chaining
        """
        self._chart = chart
        return self

    # -------------------------------------------------------------------------
    # Section Adding Methods
    # -------------------------------------------------------------------------
    # Each .with_*() method adds a section to the report.
    # Sections are not evaluated until render() is called.
    def with_chart_overview(self) -> "ReportBuilder":
        """
        Add chart overview section (birth data, chart type, etc.).

        Returns:
            Self for chaining
        """
        self._sections.append(ChartOverviewSection())
        return self

    def with_planet_positions(
        self,
        include_speed: bool = False,
        include_house: bool = True,
        house_system: str | None = None,
    ) -> "ReportBuilder":
        """
        Add planet positions table.

        Args:
            include_speed: Show speed in longitude (for retrogrades)
            include_house: Show house placement
            house_system: Which house system to use (None = default)

        Returns:
            Self for chaining
        """
        self._sections.append(
            PlanetPositionSection(
                include_speed=include_speed,
                include_house=include_house,
                house_system=house_system,
            )
        )
        return self

    def with_aspects(
        self,
        mode: str = "all",
        orbs: bool = True,
        sort_by: str = "orb",  # or "planet" or "aspect_type"
    ) -> "ReportBuilder":
        """
        Add aspects table.

        Args:
            mode: "all", "major", or "minor"
            orb_display: Show orb column
            sort_by: How to sort aspects

        Returns:
            Self for chaining
        """
        self._sections.append(
            AspectSection(
                mode=mode,
                orbs=orbs,
                sort_by=sort_by,
            )
        )
        return self

    def with_midpoints(
        self,
        mode: str = "all",
        threshold: int | None = None,
    ) -> "ReportBuilder":
        """
        Add midpoints table.

        Args:
            mode: "all" or "core" (Sun/Moon/ASC/MC midpoints)
            threshold: Only show top N midpoints by importance

        Returns:
            Self for chaining
        """
        self._sections.append(
            MidpointSection(
                mode=mode,
                threshold=threshold,
            )
        )
        return self

    def with_section(self, section: ReportSection) -> "ReportBuilder":
        """
        Add a custom section.

        This allows users to extend the report system with their own sections.

        Args:
            section: Any object implementing the ReportSection protocol

        Returns:
            Self for chaining

        Example:
            class MyCustomSection:
                @property
                def section_name(self) -> str:
                    return "My Analysis"

                def generate_data(self, chart: CalculatedChart) -> dict:
                    return {"type": "text", "text": "Custom analysis..."}

            report = (
                ReportBuilder()
                .from_chart(chart)
                .with_section(MyCustomSection())
                .render()
            )
        """
        self._sections.append(section)
        return self

    # -------------------------------------------------------------------------
    # Rendering Methods
    # -------------------------------------------------------------------------
    def render(self, format: str = "rich_table") -> str:
        """
        Render the report in the specified format.

        Args:
            format: Output format ("rich_table", "plaintext", "html")

        Returns:
            Formatted report string

        Raises:
            ValueError: If no chart has been set
            ValueError: If unknown format specified
        """
        if not self._chart:
            raise ValueError("No chart set. Call .from_chart(chart) before rendering.")

        # Select renderer based on format
        renderer = self._get_renderer(format)

        # Generate data from all sections
        section_data = [
            (section.section_name, section.generate_data(self._chart))
            for section in self._sections
        ]

        # Render the complete report
        return renderer.render_report(section_data)

    def to_file(self, filename: str, format: str = "plaintext") -> str:
        """
        Render report and save to file.

        Args:
            filename: Output file path
            format: Output format

        Returns:
            The filename (for confirmation)
        """
        content = self.render(format=format)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        return filename

    def _get_renderer(self, format: str) -> ReportRenderer:
        """
        Get the appropriate renderer for the format.

        Why a factory method?
        - Centralizes renderer selection logic
        - Easy to add new renderers
        - Can implement caching if needed

        Args:
            format: Renderer name

        Returns:
            Renderer instance

        Raises:
            ValueError: If format is unknown
        """
        renderers = {
            "rich_table": RichTableRenderer(),
            "plaintext": PlainTextRenderer(),
            # Future: "html": HTMLRenderer(),
            # Future: "markdown": MarkdownRenderer(),
        }

        if format not in renderers:
            available = ", ".join(renderers.keys())
            raise ValueError(f"Unknown format '{format}'. Available: {available}")

        return renderers[format]
