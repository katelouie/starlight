"""Code to generate the charts for docs/VISUALIZATION.md"""

from starlight import ChartBuilder
import os

FILEDIR = "docs/images"

# Registry for chart functions
_chart_functions = []


def chart(func):
    """Decorator to register chart generation functions"""
    _chart_functions.append(func)
    return func


@chart
def readme_top_chart():
    filename = "readme_first.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing = (
        drawing.with_zodiac_palette("rainbow")
        .with_moon_phase(position="bottom-left", show_label=True)
        .with_chart_info(position="top-left")
    )
    drawing.save()


@chart
def readme_chart():
    filename = "readme_einstein.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.save()


@chart
def readme_chart_2():
    filename = "readme_einstein_celestial.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing = (
        drawing.with_theme("celestial")
        .with_zodiac_palette("rainbow_celestial")
        .with_moon_phase(position="bottom-left", show_label=True)
        .with_chart_info(position="top-left")
    )
    drawing.save()


@chart
def viz_chart_minimal():
    filename = "viz_minimal.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.preset_minimal().save()


@chart
def viz_chart_standard():
    filename = "viz_standard.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.preset_standard().save()


@chart
def viz_chart_detailed():
    filename = "viz_detailed.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.preset_detailed().save()


@chart
def viz_chart_midnight():
    filename = "viz_midnight.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("midnight").save()


@chart
def viz_chart_celestial():
    filename = "viz_celestial.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("celestial").save()


@chart
def viz_chart_neon():
    filename = "viz_neon.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("neon").save()


@chart
def viz_chart_celestial_more():
    filename = "viz_celestial_more.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    (
        drawing.with_theme("celestial")
        .with_zodiac_palette("rainbow_celestial")
        .with_moon_phase(position="bottom-left", show_label=True)
        .with_chart_info(position="top-left")
        .with_aspect_counts(position="top-right")
        .save()
    )


def main():
    """Execute all registered chart functions"""
    for func in _chart_functions:
        print(f"Generating {func.__name__}...")
        func()


if __name__ == "__main__":
    main()
