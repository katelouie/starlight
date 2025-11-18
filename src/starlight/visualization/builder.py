"""
Fluent builder API for chart visualization.

Provides a convenient, discoverable API for creating chart visualizations
with presets and easy customization.
"""

from typing import Any

from starlight.core.comparison import Comparison
from starlight.core.models import CalculatedChart


class ChartDrawBuilder:
    """
    Fluent builder for chart visualization with preset support.

    This builder provides a high-level, user-friendly API for creating
    chart visualizations. It wraps the lower-level draw_chart() function
    with a fluent interface and convenient presets.

    Usage:
        # Simple preset
        chart.draw("chart.svg").preset_standard().save()

        # Custom configuration
        chart.draw("custom.svg") \\
            .with_size(800) \\
            .with_theme("midnight") \\
            .with_moon_phase(position="top-left", show_label=True) \\
            .save()

        # Comparison charts
        comparison.draw("synastry.svg").preset_synastry().save()
    """

    def __init__(self, chart: CalculatedChart | Comparison):
        """
        Initialize the builder.

        Args:
            chart: The chart or comparison to visualize
        """
        self._chart = chart
        self._is_comparison = isinstance(chart, Comparison)

        # Core settings
        self._filename = "chart.svg"
        self._size = 600

        # Theme and palettes
        self._theme: str | None = None
        self._zodiac_palette: str | None = None
        self._aspect_palette: str | None = None
        self._planet_glyph_palette: str | None = None
        self._color_sign_info = False

        # Moon phase
        self._moon_phase = True
        self._moon_phase_position = None  # Auto-detect based on aspects
        self._moon_phase_show_label = False
        self._moon_phase_size: int | None = None
        self._moon_phase_label_size: str | None = None

        # Corner elements
        self._chart_info = False
        self._chart_info_position = "top-left"
        self._chart_info_fields: list[str] | None = None

        self._aspect_counts = False
        self._aspect_counts_position = "top-right"

        self._element_modality_table = False
        self._element_modality_table_position = "bottom-left"

        self._chart_shape = False
        self._chart_shape_position = "bottom-right"

        # Extended canvas
        self._extended_canvas: dict[str, Any] | None = None

    def with_filename(self, filename: str) -> "ChartDrawBuilder":
        """
        Set the output filename.

        Args:
            filename: Path to save the SVG file

        Returns:
            Self for chaining
        """
        self._filename = filename
        return self

    def with_size(self, size: int) -> "ChartDrawBuilder":
        """
        Set the chart size in pixels.

        Args:
            size: Chart size (width and height)

        Returns:
            Self for chaining
        """
        self._size = size
        return self

    def with_theme(self, theme: str) -> "ChartDrawBuilder":
        """
        Set the chart theme.

        Args:
            theme: Theme name (e.g., "classic", "dark", "midnight", "neon", "celestial")

        Returns:
            Self for chaining
        """
        self._theme = theme
        return self

    def with_zodiac_palette(self, palette: str) -> "ChartDrawBuilder":
        """
        Set the zodiac ring color palette.

        Args:
            palette: Palette name (e.g., "grey", "rainbow", "viridis", "elemental")

        Returns:
            Self for chaining
        """
        self._zodiac_palette = palette
        return self

    def with_aspect_palette(self, palette: str) -> "ChartDrawBuilder":
        """
        Set the aspect line color palette.

        Args:
            palette: Palette name (e.g., "classic", "dark", "blues", "plasma")

        Returns:
            Self for chaining
        """
        self._aspect_palette = palette
        return self

    def with_planet_glyph_palette(self, palette: str) -> "ChartDrawBuilder":
        """
        Set the planet glyph color palette.

        Args:
            palette: Palette name (e.g., "default", "element", "chakra", "rainbow")

        Returns:
            Self for chaining
        """
        self._planet_glyph_palette = palette
        return self

    def with_adaptive_colors(self, sign_info: bool = True) -> "ChartDrawBuilder":
        """
        Enable adaptive coloring for sign glyphs in planet info stack.

        Args:
            sign_info: Color sign glyphs in planet info based on zodiac palette

        Returns:
            Self for chaining

        Note:
            Zodiac wheel glyphs are always adaptively colored for accessibility.
            This setting only controls the tiny sign glyphs in planet info stacks.
        """
        self._color_sign_info = sign_info
        return self

    def with_moon_phase(
        self,
        position: str = "center",
        show_label: bool = False,
        size: int | None = None,
        label_size: str | None = None,
    ) -> "ChartDrawBuilder":
        """
        Configure moon phase display.

        Args:
            position: Where to place moon ("center", "top-left", "top-right", "bottom-left", "bottom-right")
            show_label: Whether to show the phase name
            size: Moon radius in pixels (defaults: 60 for center, 30-35 for corners)
            label_size: Label font size (defaults: "14px" for center, "11px" for corners)

        Returns:
            Self for chaining
        """
        self._moon_phase = True
        self._moon_phase_position = position
        self._moon_phase_show_label = show_label

        # Auto-size based on position if not specified
        if size is not None:
            self._moon_phase_size = size
        elif position == "center":
            self._moon_phase_size = 60
        else:
            self._moon_phase_size = 32

        # Auto-size label based on position if not specified
        if label_size is not None:
            self._moon_phase_label_size = label_size
        elif position == "center":
            self._moon_phase_label_size = "14px"
        else:
            self._moon_phase_label_size = "11px"

        return self

    def without_moon_phase(self) -> "ChartDrawBuilder":
        """
        Disable moon phase display.

        Returns:
            Self for chaining
        """
        self._moon_phase = False
        return self

    def with_chart_info(
        self,
        position: str = "top-left",
        fields: list[str] | None = None,
    ) -> "ChartDrawBuilder":
        """
        Add chart information box.

        Args:
            position: Corner position ("top-left", "top-right", "bottom-left", "bottom-right")
            fields: Fields to display (options: "name", "location", "datetime", "timezone", "coordinates", "house_system")

        Returns:
            Self for chaining
        """
        self._chart_info = True
        self._chart_info_position = position
        self._chart_info_fields = fields
        return self

    def with_aspect_counts(self, position: str = "top-right") -> "ChartDrawBuilder":
        """
        Add aspect counts summary.

        Args:
            position: Corner position

        Returns:
            Self for chaining
        """
        self._aspect_counts = True
        self._aspect_counts_position = position
        return self

    def with_element_modality_table(
        self, position: str = "bottom-left"
    ) -> "ChartDrawBuilder":
        """
        Add element × modality cross-table.

        Args:
            position: Corner position

        Returns:
            Self for chaining
        """
        self._element_modality_table = True
        self._element_modality_table_position = position
        return self

    def with_chart_shape(self, position: str = "bottom-right") -> "ChartDrawBuilder":
        """
        Add chart shape detection display.

        Args:
            position: Corner position

        Returns:
            Self for chaining
        """
        self._chart_shape = True
        self._chart_shape_position = position
        return self

    # === Preset Methods ===

    def preset_minimal(self) -> "ChartDrawBuilder":
        """
        Minimal preset: Just the core chart with no decorations.

        Returns:
            Self for chaining
        """
        self._moon_phase = False
        self._chart_info = False
        self._aspect_counts = False
        self._element_modality_table = False
        self._chart_shape = False
        return self

    def preset_standard(self) -> "ChartDrawBuilder":
        """
        Standard preset: Core chart with moon phase in center.

        Returns:
            Self for chaining
        """
        self._moon_phase = True
        self._moon_phase_position = None  # Auto-detect based on aspects
        self._moon_phase_show_label = False
        self._chart_info = False
        self._aspect_counts = False
        self._element_modality_table = False
        self._chart_shape = False
        return self

    def preset_detailed(self) -> "ChartDrawBuilder":
        """
        Detailed preset: Chart with info boxes in all corners.

        Returns:
            Self for chaining
        """
        self._moon_phase = True
        self._moon_phase_position = None  # Auto-detect based on aspects
        self._moon_phase_show_label = False

        self._chart_info = True
        self._chart_info_position = "top-left"

        self._aspect_counts = True
        self._aspect_counts_position = "top-right"

        self._element_modality_table = True
        self._element_modality_table_position = "bottom-left"

        self._chart_shape = True
        self._chart_shape_position = "bottom-right"

        return self

    def preset_synastry(self) -> "ChartDrawBuilder":
        """
        Synastry preset: Optimized for relationship comparison charts.

        Returns:
            Self for chaining
        """
        # Moon in corner to make room for two charts' data
        self._moon_phase = True
        self._moon_phase_position = "top-left"
        self._moon_phase_show_label = True

        self._chart_info = True
        self._chart_info_position = "top-right"

        self._aspect_counts = True
        self._aspect_counts_position = "bottom-right"

        return self

    # === Execute ===

    def save(self) -> str:
        """
        Build and save the chart visualization.

        Returns:
            The filename of the saved SVG file

        Raises:
            ValueError: If required configuration is missing
        """
        # Import here to avoid circular dependency
        from starlight.visualization.drawing import draw_chart

        # Build options dictionary
        options = {
            "filename": self._filename,
            "size": self._size,
            "theme": self._theme,
            "zodiac_palette": self._zodiac_palette,
            "aspect_palette": self._aspect_palette,
            "planet_glyph_palette": self._planet_glyph_palette,
            "color_sign_info": self._color_sign_info,
            "moon_phase": self._moon_phase,
            "moon_phase_position": self._moon_phase_position,
            "chart_info": self._chart_info,
            "aspect_counts": self._aspect_counts,
            "element_modality_table": self._element_modality_table,
            "chart_shape": self._chart_shape,
        }

        # Add moon phase options if enabled
        if self._moon_phase:
            options["moon_phase_label"] = self._moon_phase_show_label
            # NOTE: draw_chart doesn't currently support moon_phase_size or label_size customization
            # These would need to be added to drawing.py first

        # Add chart info options if enabled
        if self._chart_info:
            options["chart_info_position"] = self._chart_info_position
            if self._chart_info_fields:
                options["chart_info_fields"] = self._chart_info_fields

        # Add aspect counts position if enabled
        if self._aspect_counts:
            options["aspect_counts_position"] = self._aspect_counts_position

        # Add element/modality table position if enabled
        if self._element_modality_table:
            options["element_modality_position"] = self._element_modality_table_position

        # Add chart shape position if enabled
        if self._chart_shape:
            options["chart_shape_position"] = self._chart_shape_position

        # Add extended canvas if configured
        if self._extended_canvas:
            options["extended_canvas"] = self._extended_canvas

        # Call draw_chart with all options
        return draw_chart(self._chart, **options)
