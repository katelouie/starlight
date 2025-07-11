"""Draw an astrological SVG chart.

Absolutely NOTHING in this file works properly.
"""

# src/starlight/draw_chart.py

import math

import svgwrite
from PIL import Image, ImageDraw

from starlight.chart import Chart
from starlight.objects import format_long_sign, get_ephemeris_object


def polar_to_cartesian(cx, cy, angle_deg, radius):
    angle_rad = math.radians(angle_deg - 90)
    x = cx + radius * math.cos(angle_rad)
    y = cy + radius * math.sin(angle_rad)
    return x, y


def draw_svg_chart(chart: Chart, filename: str = "chart.svg"):
    # Canvas setup
    size = 600
    center = size // 2
    radius_outer = 250
    radius_inner = 200
    radius_planets = 150
    dwg = svgwrite.Drawing(filename, size=(size, size), profile="tiny")

    # Background ring
    dwg.add(
        dwg.circle(
            center=(center, center),
            r=radius_outer,
            fill="white",
            stroke="black",
            stroke_width=2,
        )
    )
    print([f"{str(x)}: {format_long_sign(x.long)}" for x in chart.angles])
    asc_degree = [x for x in chart.angles if x.name == "ASC"][0].long
    print(asc_degree)

    # Zodiac slices
    for i in range(12):
        angle = i * 30
        label_angle = angle + 15  # middle of each slice

        # Draw division line
        x, y = polar_to_cartesian(center, center, angle, radius_outer)
        dwg.add(
            dwg.line(start=(center, center), end=(x, y), stroke="gray", stroke_width=1)
        )

        # Sign label
        lx, ly = polar_to_cartesian(center, center, label_angle, radius_inner)
        # sign_long = (asc_degree + angle) % 360
        sign_long = (-asc_degree - i * 30 - 90) % 360
        print(sign_long, format_long_sign(sign_long))
        sign = format_long_sign(sign_long)
        dwg.add(
            dwg.text(
                sign,
                insert=(lx, ly),
                text_anchor="middle",
                # dominant_baseline="middle",
                font_size="14px",
                fill="black",
            )
        )

    for planet in chart.planets[:2]:
        # Calculate angle relative to ASC
        print(planet.name, planet.long, format_long_sign(planet.long))
        relative_angle = (270 - (planet.long - ((asc_degree // 30) * 30))) % 360
        print(planet.name, relative_angle)

        # Get position on the wheel
        px, py = polar_to_cartesian(center, center, relative_angle, radius_planets)

        # Get glyph from alias (last character of alias string)
        glyph = get_ephemeris_object(planet.swe)["alias"][-1]

        # Optional: retrograde indicator
        fill_color = "red" if planet.is_retro else "black"

        # Draw the glyph
        dwg.add(
            dwg.text(
                glyph,
                insert=(px, py),
                text_anchor="middle",
                font_size="18px",
                fill=fill_color,
            )
        )

    # Save it
    dwg.save()
    print(f"SVG chart saved as {filename}")


def draw_moon_phase_pil(phase_angle, size=200):
    img = Image.new("RGB", (size, size), "black")
    draw = ImageDraw.Draw(img)
    r = size // 2
    cx, cy = r, r

    # Draw full moon base
    draw.ellipse([0, 0, size, size], fill="gray")

    # Phase factor: 0 (new) to 1 (full)
    phase = (1 + math.cos(math.radians(phase_angle))) / 2

    # Overlay shadow
    shadow_width = int(
        r * (1 - 2 * abs(0.5 - phase))
    )  # thinner crescent = wider shadow
    if phase_angle <= 180:
        # Waxing (dark on left)
        draw.ellipse([cx - shadow_width, 0, cx + r, size], fill="black")
    else:
        # Waning (dark on right)
        draw.ellipse([cx - r, 0, cx + shadow_width, size], fill="black")

    return img


def draw_moon_phase(angle, filename="moon_phase.svg"):
    size = 200
    center = size // 2
    radius = 80

    dwg = svgwrite.Drawing(filename, size=(size, size), profile="full")

    # Define base clip path
    clip_path_id = "moonClip"
    clip_path = dwg.defs.add(dwg.clipPath(id=clip_path_id))
    clip_path.add(dwg.circle(center=(center, center), r=radius))

    # Illumination and waxing state
    illumination = (1 + math.cos(math.radians(angle))) / 2
    waxing = angle <= 180

    # Draw base lit moon
    dwg.add(dwg.circle(center=(center, center), r=radius, fill="white", stroke="black"))

    if not math.isclose(illumination, 1.0, abs_tol=1e-2):
        if math.isclose(illumination, 0.5, abs_tol=1e-2):
            # Perfect quarter moon: black half-circle
            if waxing:
                # Dark on left
                shadow = dwg.path(
                    d=f"M {center} {center - radius} A {radius} {radius} 0 0 0 {center} {center + radius} Z",
                    fill="black",
                )
            else:
                # Dark on right
                shadow = dwg.path(
                    d=f"M {center} {center - radius} A {radius} {radius} 0 0 1 {center} {center + radius} Z",
                    fill="black",
                )
        else:
            # Crescent or gibbous
            shadow_width = radius * 2 * (1 - illumination)
            cx = (
                center - (radius - shadow_width / 2)
                if waxing
                else center + (radius - shadow_width / 2)
            )
            shadow = dwg.ellipse(
                center=(cx, center), r=(shadow_width / 2, radius), fill="black"
            )

        shadow["clip-path"] = f"url(#{clip_path_id})"
        dwg.add(shadow)

    dwg.save()
    print(f"Moon phase SVG saved to {filename}")


def draw_moon_half_phased(angle, filename="moon_phase.svg"):
    """
    Draw an approximate half-phased moon (two-tone) in an SVG file,
    with 'angle' = separation Sun-Moon in [0..360] degrees:
      0° => Full Moon
      180° => New Moon
      90° => ~ First Quarter
      270° => ~ Last Quarter
    Waxing if angle<180, waning otherwise.
    """
    size = 200
    center = size // 2
    radius = 80

    dwg = svgwrite.Drawing(filename, size=(size, size), profile="full")

    # Clip path for the circle boundary
    clip_id = "moonClip"
    clip_path = dwg.defs.add(dwg.clipPath(id=clip_id))
    clip_path.add(dwg.circle(center=(center, center), r=radius))

    # White circle as the 'base' moon
    dwg.add(dwg.circle(center=(center, center), r=radius, fill="white", stroke="black"))

    # Convert angle -> illumination in [0..1], 0 => new, 1 => full
    # This is the standard formula for fraction of illuminated disc:
    #   ill = (1 + cos(angle)) / 2
    # but note angle=0 => cos(0)=1 => ill=1 => FULL
    # angle=180 => ill=0 => NEW
    illumination = (1 + math.cos(math.radians(angle))) / 2
    waxing = angle < 180

    # We'll define a helper that draws an arc-based path for "shadow".
    # side = 'left' or 'right': which side to fill black
    # arc_extent ~ how big the arc is in degrees, we set flags accordingly
    # curve_ratio can scale the horizontal radius for crescents.
    def add_shadow_arc(side, curve_ratio=1.0):
        # side: 'left' or 'right'
        # We'll do a path that covers from top to bottom with an elliptical arc.
        # We'll compute a path starting at top-of-moon, arc to bottom-of-moon,
        # then along the circle edge back up, or vice versa.

        # direction -1 => left, +1 => right
        direction = -1 if side == "left" else 1

        # We'll scale the horizontal radius of the arc by curve_ratio
        rx = radius * curve_ratio
        ry = radius

        # The arc path:
        #  M center,center-radius
        #  A rx,ry 0 large_arc_flag sweep_flag center, center+radius
        #  L (center + direction*radius),(center+radius)
        #  A radius,radius 0 large_arc_flag2 sweep_flag2 (center+direction*radius),(center-radius)
        #  Z
        #
        # We want a half ellipse from top to bottom, so the arc is 180°, i.e. large_arc_flag=0,
        # but for crescents we may do smaller arcs. We'll keep it simpler: if curve_ratio <1,
        # we get a narrower arc => "crescent."

        # We'll guess the arcs are <180 => large_arc_flag=0. We might flip sweep_flag for left vs right.
        # For side='left', the 1st arc sweeps outward to bottom on the left side => sweep_flag=0
        # For side='right', the 1st arc sweeps outward => sweep_flag=1
        # Then the second arc is the outer boundary going back up.

        # But let's keep a consistent approach:
        # We'll do top->bottom with the first arc. Because it's half or partial, large_arc=0 if we want <=180.
        # If the "angle" is exactly half, we want 180°, but let's keep large_arc=0 for now.
        # We'll keep the second arc as the circle edge (radius) with large_arc=1 only if we want a bigger chunk.
        # For simpler code, let's do large_arc=0 for all arcs in typical usage. If we find we need a bigger arc, we set it to 1.

        # We'll pick the flags by side:
        #   if side='left', first arc: sweep_flag=0, second arc: sweep_flag=1
        #   if side='right', first arc: sweep_flag=1, second arc: sweep_flag=0
        # That usually yields the correct path orientation.

        if side == "left":
            arc1_sweep = 0
            arc2_sweep = 1
        else:
            arc1_sweep = 1
            arc2_sweep = 0

        # We'll define path strings
        d = []
        # Move to top center
        d.append(f"M {center} {center - radius}")
        # First arc (the 'terminator'):
        # '0' for large_arc_flag => we want <=180 arcs
        d.append(f"A {rx} {ry} 0 0 {arc1_sweep} {center} {center + radius}")
        # line across the bottom to left or right
        xbottom = center + direction * radius
        d.append(f"L {xbottom} {center + radius}")
        # second arc along the outside circle edge
        d.append(f"A {radius} {radius} 0 0 {arc2_sweep} {xbottom} {center - radius}")
        d.append("Z")

        path = dwg.path(d=" ".join(d), fill="black")
        # Clip to the circle boundary
        path["clip-path"] = f"url(#{clip_id})"
        dwg.add(path)

    # Tolerance
    eps = 1e-3

    # edge cases:
    if illumination < eps:
        # new moon
        # fill entire circle black
        dwg.add(dwg.circle(center=(center, center), r=radius, fill="black"))
    elif (1.0 - illumination) < eps:
        # full moon => do nothing (already white)
        pass
    else:
        # partial
        # special check if half (quarter-phase)
        if abs(illumination - 0.5) < eps:
            # Exactly half. We want a perfect half black, half white.
            # if waxing => black on left half, else black on right half
            if waxing:
                # black on left
                add_shadow_arc("left", 1.0)
            else:
                add_shadow_arc("right", 1.0)
        else:
            # Crescent or Gibbous
            # 'illumination' is fraction of brightness
            # if illumination < 0.5 => mostly dark => "Crescent"
            # else => mostly bright => "Gibbous"
            # We'll define a 'curve_ratio' that controls how wide the black arc is
            # For a small bright crescent, black is big => wide arc => curve_ratio ~1
            # Actually we do curve_ratio = some function of illumination.
            # let shadow portion fraction = 1 - ill if waxing or ill if waning.
            # Because for waxing with ill<0.5 => black portion is (1-ill). We'll do ratio= (1-ill)*2 ?
            # We'll keep it simpler: ratio = 2*abs(0.5 - ill). That yields 1 at half, 0 near full/new.
            ratio = 2 * abs(0.5 - illumination)

            # if ratio>1, clamp
            if ratio > 1:
                ratio = 1

            if illumination < 0.5:
                # Crescent
                # if waxing => black on left is big, plus maybe partial on the right? Actually we only need one arc.
                # We'll do one big black arc on left if waxing, or on right if waning, with ratio.
                if waxing:
                    add_shadow_arc("left", 1.0)  # big left side black
                    add_shadow_arc("right", ratio)  # partial on right
                else:
                    add_shadow_arc("right", 1.0)
                    add_shadow_arc("left", ratio)
            else:
                # Gibbous
                # if waxing => small black portion on the right, else small black portion on the left
                # We'll invert ratio so that the arc is the smaller chunk
                # e.g. if illumination=0.8 => ratio=0.6 => we want that to be 0.4 for the smaller side's arc, so do (1-ratio)
                smaller = 1 - ratio
                if smaller < 0:
                    smaller = 0
                if waxing:
                    add_shadow_arc("right", smaller)
                else:
                    add_shadow_arc("left", smaller)

    dwg.save()
    return filename


def draw_moon_half_phased_fixed(angle, filename="moon_phase.svg"):
    size = 200
    center = size // 2
    radius = 80

    dwg = svgwrite.Drawing(filename, size=(size, size), profile="full")

    # Define clip path for Moon boundary
    clip_id = "moonClip"
    clip_path = dwg.defs.add(dwg.clipPath(id=clip_id))
    clip_path.add(dwg.circle(center=(center, center), r=radius))

    # Base white moon
    dwg.add(dwg.circle(center=(center, center), r=radius, fill="white", stroke="black"))

    illumination = (1 + math.cos(math.radians(angle))) / 2
    waxing = angle <= 180

    def add_half_shadow(side):
        # Straight half division
        if side == "left":
            path = dwg.path(
                d=f"M {center} {center - radius} "
                f"A {radius} {radius} 0 0 0 {center} {center + radius} "
                f"L {center - radius} {center + radius} "
                f"A {radius} {radius} 0 0 1 {center - radius} {center - radius} Z",
                fill="black",
            )
        else:  # right
            path = dwg.path(
                d=f"M {center} {center - radius} "
                f"A {radius} {radius} 0 0 1 {center} {center + radius} "
                f"L {center + radius} {center + radius} "
                f"A {radius} {radius} 0 0 0 {center + radius} {center - radius} Z",
                fill="black",
            )
        path["clip-path"] = f"url(#{clip_id})"
        dwg.add(path)

    def add_crescent(side, curve_ratio):
        width = radius * curve_ratio
        if side == "right":
            # inward curve on right
            x1 = center
            x2 = center + width
            arc = dwg.path(
                d=f"M {x1} {center - radius} "
                f"A {width} {radius} 0 0 1 {x1} {center + radius} "
                f"L {x2} {center + radius} "
                f"A {radius} {radius} 0 0 0 {x2} {center - radius} Z",
                fill="black",
            )
        else:
            # inward curve on left
            x1 = center
            x2 = center - width
            arc = dwg.path(
                d=f"M {x1} {center - radius} "
                f"A {width} {radius} 0 0 0 {x1} {center + radius} "
                f"L {x2} {center + radius} "
                f"A {radius} {radius} 0 0 1 {x2} {center - radius} Z",
                fill="black",
            )
        arc["clip-path"] = f"url(#{clip_id})"
        dwg.add(arc)

    def add_gibbous(side, curve_ratio):
        width = radius * curve_ratio
        if side == "left":
            # outward curve on left (black outer part)
            x1 = center
            x2 = center - width
            arc = dwg.path(
                d=f"M {x2} {center - radius} "
                f"A {width} {radius} 0 0 1 {x2} {center + radius} "
                f"L {x1} {center + radius} "
                f"A {radius} {radius} 0 0 0 {x1} {center - radius} Z",
                fill="black",
            )
        else:
            # outward curve on right (black outer part)
            x1 = center
            x2 = center + width
            arc = dwg.path(
                d=f"M {x2} {center - radius} "
                f"A {width} {radius} 0 0 0 {x2} {center + radius} "
                f"L {x1} {center + radius} "
                f"A {radius} {radius} 0 0 1 {x1} {center - radius} Z",
                fill="black",
            )
        arc["clip-path"] = f"url(#{clip_id})"
        dwg.add(arc)

    if math.isclose(illumination, 0.0, abs_tol=1e-2):
        dwg.add(dwg.circle(center=(center, center), r=radius, fill="black"))
    elif math.isclose(illumination, 1.0, abs_tol=1e-2):
        pass  # Full Moon (all white)
    elif math.isclose(illumination, 0.5, abs_tol=1e-2):
        if waxing:
            add_half_shadow("left")
        else:
            add_half_shadow("right")
    elif illumination < 0.5:
        curve_ratio = 1 - 2 * illumination
        if waxing:
            add_half_shadow("left")
            add_crescent("right", curve_ratio)
        else:
            add_half_shadow("right")
            add_crescent("left", curve_ratio)
    else:  # gibbous
        curve_ratio = 2 * illumination - 1
        if waxing:
            add_gibbous("right", curve_ratio)
        else:
            add_gibbous("left", curve_ratio)

    dwg.save()
    return filename


import math

from PIL import Image, ImageDraw


def draw_moon_phase(angle_degrees, size=200):
    """
    Returns a Pillow Image of approximate Moon phase for a given Sun-Moon separation angle (0..360).
    0 or 360 => Full Moon (all white),
    180 => New Moon (all black),
    90 or 270 => Quarters (half white/black),
    etc.

    The result is a 'cartoon' 2D circle with the lit portion on left or right.
    """
    # 1) Create a black background
    img = Image.new("RGB", (size, size), "black")
    draw = ImageDraw.Draw(img)

    # 2) Calculate fraction of illumination using the standard formula:
    #    fraction = (1 + cos(angle)) / 2
    # Where angle is in radians, 0 => fraction=1 => Full Moon, 180 => fraction=0 => New.
    angle_radians = math.radians(angle_degrees % 360)
    fraction = (1.0 + math.cos(angle_radians)) / 2.0

    # We'll consider "waxing" if angle<180, else "waning".
    # Actually if angle in [0..180], it's waxing from Full->New.
    # But many prefer 0 => Full, 180 => New, so let's define:
    #   if angle < 180 => waxing, else => waning
    waxing = (angle_degrees % 360) < 180

    # 3) We'll define a circle in the center. Radius = ~size//3
    radius = size // 3
    cx, cy = size // 2, size // 2

    # 4) Draw the "Moon circle" shape in a base color.
    #    We'll fill it with white if fraction >=0.5, else black,
    #    then we add the 'other' portion to represent the unlit or lit side.
    if fraction >= 0.5:
        # mostly white => base circle white
        base_color = "white"
        other_color = "black"
    else:
        # mostly black => base circle black
        base_color = "black"
        other_color = "white"

    # Draw the base circle
    bounding = [cx - radius, cy - radius, cx + radius, cy + radius]
    draw.ellipse(bounding, fill=base_color, outline="gray")

    # 5) If fraction close to 0 => new moon => fully black, or fraction close to 1 => full => fully white
    eps = 1e-3
    if fraction < eps:
        # New Moon => just leave it black
        draw.ellipse(bounding, fill="black", outline="gray")
        return img
    if abs(fraction - 1.0) < eps:
        # Full Moon => it's already white
        return img

    # 6) For partial phases, we define a vertical "terminator" offset.
    #    Let's define offset_x = (2*fraction -1)*radius.
    #    fraction=0.5 => offset=0 => half
    #    fraction>0.5 => positive => center terminator on the right
    #    fraction<0.5 => negative => center terminator on the left
    #    waxing vs. waning decides which side is lit vs. shadow.
    offset = (2 * fraction - 1.0) * radius

    # We'll do a pixel-based approach:
    # For each x in [cx-radius..cx+radius], figure out y-limits of the circle,
    # then fill with 'other_color' if it should be "shadow" or "lit portion."

    # The "dark portion" is on one side of the offset.
    # If fraction >= 0.5 => base is white => other_color=black => black is the shadow side
    #   if waxing => shadow is on the right side? Actually if fraction=0.75 => it's a waxing gibbous => the dark side is left or right? Let's see:
    # Actually let's do a simpler logic:
    #   If waxing => the bright portion is on the left side (for angles <180).
    #   If fraction>=0.5 => the black portion is smaller, so it belongs on the 'opposite side' from the bright portion.
    # We'll define a function is_shadow(xrel) that returns True if it's overshadowed or not.
    # We'll keep it simple:
    #   If fraction >=0.5 => base=white => shadow = black on the side:
    #     if waxing => black on right => xrel> offset => shadow
    #     else => black on left => xrel< offset => shadow
    #   If fraction <0.5 => base=black => bright portion is other_color =>
    #     if waxing => bright portion left => xrel < offset => bright
    #     else => bright portion right => xrel > offset => bright

    def in_circle(xi, yi):
        return (xi - cx) ** 2 + (yi - cy) ** 2 <= radius * radius

    def is_shadow(xrel):
        # xrel is x-cx
        if fraction >= 0.5:
            # base=white => shadow=black on one side
            if waxing:
                return xrel > offset  # black if x>offset
            else:
                return xrel < offset  # black if x<offset
        else:
            # base=black => bright= 'other_color'
            # so shadow means 'remain black'? but let's do shadow= base => isShadow=not bright
            if waxing:
                # bright if xrel<offset => so shadow if xrel>=offset
                return not (xrel < offset)
            else:
                # bright if xrel>offset => shadow if xrel<=offset
                return not (xrel > offset)

    # We'll scan pixel by pixel in bounding box
    for x in range(cx - radius, cx + radius + 1):
        xrel = x - cx
        # half chord in y?
        # y range from cy - halfchord to cy + halfchord
        # halfchord = sqrt(r^2 - xrel^2)
        halfc2 = radius * radius - xrel * xrel
        if halfc2 < 0:
            continue
        hy = int(math.sqrt(halfc2))
        ytop = cy - hy
        ybot = cy + hy
        for y in range(ytop, ybot + 1):
            if is_shadow(xrel):
                # shadow => color=other_color if fraction>=0.5, else base
                # but we said if fraction>=0.5 => base=white => shadow=black
                # if fraction<0.5 => base=black => bright= white => shadow= base
                # Actually simpler: if is_shadow => color=some
                if fraction >= 0.5:
                    color = "black"
                else:
                    color = "black"  # base is black => overshadowed means black
            else:
                if fraction >= 0.5:
                    color = "white"  # base is white => no shadow
                else:
                    color = "white"  # bright portion
            img.putpixel((x, y), Image.new("RGB", (1, 1), color).getpixel((0, 0)))

    return img


import math

from PIL import Image, ImageDraw


def draw_moon_2circle(angle_degrees, size=200):
    """
    Draw an approximate 2D "lens" shape for the Moon’s phase using the "two-circle" approach:
      - Circle #1: The Moon itself (centered).
      - Circle #2: The "light circle," same radius, but offset horizontally.
    The lit portion is the intersection of these circles (waxing or waning).

    angle_degrees in [0..360], interpreted as:
      0 deg => Full Moon (all lit)
      180 deg => New Moon (all dark)
      90/270 => quarter phases (half lit)
      etc.
    Return a Pillow Image of size x size.
    """
    # Create black background
    img = Image.new("RGB", (size, size), "black")
    draw = ImageDraw.Draw(img)

    # Moon center and radius
    cx, cy = size // 2, size // 2
    radius = size // 3

    # fraction of illuminated disc:
    #   fraction = (1 + cos(angle_radians)) / 2
    # angle=0 => fraction=1 => Full
    # angle=180 => fraction=0 => New
    angle_radians = math.radians(angle_degrees % 360)
    fraction = (1 + math.cos(angle_radians)) / 2.0

    # Decide waxing or waning
    #   angle <180 => waxing
    #   angle>180 => waning
    waxing = (angle_degrees % 360) < 180

    # We'll define an offset between the two circles:
    #   offset= 2*r*(1 - fraction).
    #   fraction=1 => offset=0 => circles coincide => fully lit
    #   fraction=0 => offset=2*r => circles just tangent => no intersection => new
    offset = 2 * radius * (1 - fraction)

    # If waxing, shift the "light circle" to the left, else to the right
    if waxing:
        light_center_x = cx - offset
    else:
        light_center_x = cx + offset

    # We'll do a pixel-by-pixel approach:
    #  A point is "in the Moon" if dist from (cx,cy)< radius
    #  A point is "in the Light" if dist from (light_center_x, cy)< radius
    #  The point is lit if it’s in BOTH circles.
    #  The final color is white if lit, black if in the Moon but not lit, else black background.

    for x in range(size):
        for y in range(size):
            dxm = x - cx
            dym = y - cy
            dmoon_sq = dxm * dxm + dym * dym

            if dmoon_sq <= radius * radius:
                # We are inside the moon’s disk
                dxl = x - light_center_x
                dyl = y - cy
                dlight_sq = dxl * dxl + dyl * dyl
                # is it lit? => also inside the light circle
                if dlight_sq <= radius * radius:
                    # lit
                    img.putpixel((x, y), (255, 255, 255))  # white
                else:
                    # shadow
                    img.putpixel((x, y), (0, 0, 0))  # black
            # else: remain black background

    # Optionally draw a gray circle outline for the moon
    # bounding box
    bounding = [cx - radius, cy - radius, cx + radius, cy + radius]
    draw.ellipse(bounding, outline="gray")

    return img


# # Example usage/test
# if __name__ == "__main__":
#     for deg in [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]:
#         im = draw_moon_2circle(deg, size=240)
#         im.save(f"moon_ellip_{deg:03d}.png")


# # Example usage:
# if __name__ == "__main__":
#     # For demonstration, create images for angles in increments of 30 degrees
#     for deg in range(0, 361, 30):
#         im = draw_moon_phase(deg, size=240)
#         im.save(f"moon_{deg:03d}.png")


import math

from PIL import Image, ImageDraw


def draw_one_moon(fraction, waxing, size=80):
    """
    Draw a single 'moon' with fraction of disk lit [0..1].
    If 'waxing' is True, the bright side is on the right; else on the left.
    Return a Pillow Image of size x size with transparent background.

    Uses the 'two-circle' intersection method:
      * Circle #1 = actual moon
      * Circle #2 = 'light circle' offset horizontally
    The overlap is the lit portion.
    """
    # Transparent background
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    r = size // 2 - 4  # radius for the moon
    cx = size // 2
    cy = size // 2

    # fraction=1 => full, fraction=0 => new
    # offset = 2*r*(1 - fraction). If fraction=1 => offset=0
    # If fraction=0 => offset=2r
    offset = 2 * r * (1 - fraction)

    if waxing:
        light_cx = cx + offset  # bright on right
    else:
        light_cx = cx - offset  # bright on left

    # pixel approach
    for x in range(size):
        for y in range(size):
            dx_moon = x - cx
            dy_moon = y - cy
            dist_moon_sq = dx_moon * dx_moon + dy_moon * dy_moon
            if dist_moon_sq <= r * r:
                # inside moon
                dx_light = x - light_cx
                dy_light = y - cy
                dist_light_sq = dx_light * dx_light + dy_light * dy_light
                if dist_light_sq <= r * r:
                    # lit
                    img.putpixel((x, y), (255, 255, 255, 255))  # white
                else:
                    # shadow
                    img.putpixel((x, y), (40, 40, 40, 255))  # dark gray
    # optional outline
    bounding = [cx - r, cy - r, cx + r, cy + r]
    draw.ellipse(bounding, outline="black", width=1)
    return img


def phases_diagram(out_size=600):
    """
    Create a diagram with 8 primary moon phases around a ring:
     new, waxing crescent, first quarter, waxing gibbous,
     full, waning gibbous, third quarter, waning crescent
    in a clockwise circle
    """
    # We'll define 8 angles for the fraction: 0, 0.25, 0.5, 0.75, 1.0...,
    # but actually we can do the standard angles for sun-moon separation:
    #   new = 180, waxing cres=135, first quarter=90, waxing gibb=45,
    #   full=0, waning gibb=315, third=270, waning cres=225, ...
    # Or we can just define fraction directly. We'll do fraction-labeled approach for clarity.

    # Fractions in typical order of phases (with approximate waxing/waning)
    # new=0.0, waxing cres~0.25, first quarter=0.5, waxing gibbous=0.75,
    # full=1.0, waning gibb=0.75, third=0.5, waning cres=0.25
    # We'll define a tuple of (fraction, waxing).
    phases = [
        (0.00, False),  # new (all shadow)
        (0.25, True),  # waxing crescent
        (0.50, True),  # first quarter
        (0.75, True),  # waxing gibbous
        (1.00, True),  # full
        (0.75, False),  # waning gibb
        (0.50, False),  # third quarter
        (0.25, False),  # waning crescent
    ]

    # create big image
    img = Image.new("RGBA", (out_size, out_size), (10, 30, 60, 255))
    draw = ImageDraw.Draw(img)

    # ring center
    cx, cy = out_size // 2, out_size // 2
    ring_radius = out_size // 3

    # place 8 phases around circle
    n = len(phases)
    for i, (frac, wax) in enumerate(phases):
        # angle in radians around ring. We'll do clockwise from top.
        # top is i=0 => let's define top is new => 0 means top, but let's do an offset so it lines up the diagram you posted:
        # That diagram starts new at the left, but let's do the typical standard approach:
        # We'll do i=0 at bottom. Actually let's just do i=0 at the bottom is an easy formula:
        # angle_radians = (math.pi/2) + i*(2*math.pi/n)
        # but let's define something that rotates them around in a circle with first at the bottom, etc.

        angle = -math.pi / 2 + i * (2 * math.pi / n)  # so i=0 => angle=-90 deg => top
        # or do angle = math.pi + i*(2*math.pi/n) => i=0 => 180 deg => left side
        # see what you like. We'll do left side for new:
        angle = math.pi + i * (2 * math.pi / n)

        # find center for that small phase
        moon_x = cx + ring_radius * math.cos(angle)
        moon_y = cy + ring_radius * math.sin(angle)

        # draw the sub-moon
        single = draw_one_moon(frac, wax, size=80)
        # paste so that center is (moon_x,moon_y)
        w, h = single.size
        # top-left corner
        topx = int(moon_x - w / 2)
        topy = int(moon_y - h / 2)
        img.alpha_composite(single, (topx, topy))

        # optional text label
        # We'll define a quick label:
        # match i to name:
        label_map = [
            "New",
            "Wax Cres",
            "1st Qtr",
            "Wax Gib",
            "Full",
            "Waning Gib",
            "3rd Qtr",
            "Waning Cres",
        ]
        # measure text
        # just skip text or do something simple
        # draw.text((topx, topy+h), label_map[i], fill="white")

    # optionally draw circle or arrows
    # done
    return img


# if __name__ == "__main__":
#     diagram = phases_diagram(700)
#     diagram.save("moon_phases_diagram.png")

import math

from PIL import Image, ImageDraw


def draw_moon_artistic(fraction, waxing=True, size=100):
    """
    Draw a single Moon face with 'fraction' of disk illuminated (0..1).
      0 => New Moon (all black), 1 => Full (all white).
    If fraction < 0.5 => a small bright crescent
    If fraction > 0.5 => a large bright portion (gibbous).
    If fraction ~0.5 => exactly half circle.

    waxing=True => bright side on right. waxing=False => bright side on left.
    This is done by a 'two-circle' approach,
    but using intersection if fraction < 0.5, difference if fraction > 0.5, etc.
    """
    # We'll create an RGBA image with black background outside the circle
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2
    r = size // 2 - 2  # radius for the Moon, with a small margin

    # If fraction ~0 => all black, fraction ~1 => all white
    eps = 1e-3
    if fraction < eps:
        # entire circle black
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill="black", outline="gray")
        return img
    if (1.0 - fraction) < eps:
        # entire circle white
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill="white", outline="gray")
        return img

    # For everything else:
    # We'll define the "Moon circle" center at (cx,cy).
    # We'll define a second circle (the 'light circle') of radius r, offset horizontally by offset.
    # offset = 2*r*(1 - fraction).
    # If fraction < 0.5, the intersection of these circles is the bright portion.
    # If fraction > 0.5, the bright portion is basically the entire circle minus the intersection (the shadow).

    offset = 2 * r * (1 - fraction)
    if waxing:
        light_cx = cx + offset
    else:
        light_cx = cx - offset

    # We'll do a pixel-based approach.
    # But we also need to handle special half circle if fraction ~ 0.5 => do a perfect half circle.

    # If half => draw a half circle
    if abs(fraction - 0.5) < eps:
        # half circle
        # if waxing => bright on right half, if not => bright on left half
        bounding = (cx - r, cy - r, cx + r, cy + r)
        # We'll do a "pieslice" from -90 to +90 if bright is on right, etc.
        # Actually let's do a vertical cut. If waxing => right side is bright => from -90..90 deg
        # if not => left side => from 90..270
        if waxing:
            start_angle = -90
            end_angle = 90
        else:
            start_angle = 90
            end_angle = 270
        # Fill entire circle black first
        draw.ellipse(bounding, fill="black", outline="gray")
        # Then fill a half pieslice with white
        draw.pieslice(bounding, start=start_angle, end=end_angle, fill="white")
        return img

    # For fraction < 0.5 => bright portion is intersection
    # For fraction > 0.5 => bright portion is everything minus intersection
    # We'll define two param:
    do_intersect = fraction < 0.5

    # We'll do a pixel loop for simplicity
    for x in range(size):
        for y in range(size):
            dxm = x - cx
            dym = y - cy
            dist_moon_sq = dxm * dxm + dym * dym
            if dist_moon_sq <= r * r:
                # inside the moon
                dxl = x - light_cx
                dyl = y - cy
                dist_light_sq = dxl * dxl + dyl * dyl
                in_light = dist_light_sq <= r * r
                if do_intersect:
                    # bright if in both
                    if in_light:
                        # bright
                        img.putpixel((x, y), (255, 255, 255, 255))
                    else:
                        # shadow
                        img.putpixel((x, y), (0, 0, 0, 255))
                else:
                    # fraction>0.5 => bright is (in moon) except intersection => bright if (in moon) and not (in both)
                    if in_light:
                        # intersection => shadow
                        img.putpixel((x, y), (0, 0, 0, 255))
                    else:
                        # bright
                        img.putpixel((x, y), (255, 255, 255, 255))
    # optional outline
    bounding = (cx - r, cy - r, cx + r, cy + r)
    dr = ImageDraw.Draw(img)
    dr.ellipse(bounding, outline="gray")
    return img


def example_diagram(size=400):
    """
    Creates a demonstration diagram with 8 phases arranged in a ring:
      new, waxing cres, first quarter, waxing gibbous,
      full, waning gibb, third quarter, waning cres
    in clockwise order
    """
    # We'll define 8 phases:
    # fraction, waxing
    phases = [
        (0.0, False),  # new moon
        (0.25, True),  # waxing crescent
        (0.5, True),  # first quarter
        (0.75, True),  # waxing gibbous
        (1.0, True),  # full
        (0.75, False),  # waning gibbous
        (0.5, False),  # third quarter
        (0.25, False),  # waning crescent
    ]
    bigimg = Image.new("RGB", (size, size), (12, 36, 60))  # background
    draw = ImageDraw.Draw(bigimg)

    # ring center, radius
    cx, cy = size // 2, size // 2
    ring_r = size // 3
    small_size = 80

    n = len(phases)
    for i, (frac, wax) in enumerate(phases):
        # define angle around circle, let's do i=0 => angle= -90 => top. So we do e.g angle= -90 + i*(360/n)
        angle = -math.pi / 2 + i * (2 * math.pi / n)
        moox = cx + ring_r * math.cos(angle)
        mooy = cy + ring_r * math.sin(angle)
        sub = draw_moon_artistic(frac, wax, small_size)
        # center it
        w, h = sub.size
        left = int(moox - w / 2)
        top = int(mooy - h / 2)
        bigimg.paste(sub, (left, top), sub)  # use sub as mask also

    return bigimg


if __name__ == "__main__":
    # test
    diag = example_diagram()
    diag.save("moon_phases_artistic.png")
