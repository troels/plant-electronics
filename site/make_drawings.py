#!/usr/bin/env python3
"""Generate the layout drawings used by org/build.org.

Run from the repository root:  python3 site/make_drawings.py
Writes SVG files to org/img/. All dimensions in the code are centimetres.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "org" / "img"

STYLE = """
<style>
  :root { --bg:#fbfaf7; --fg:#22261f; --muted:#646b5e; --line:#8b9184;
          --frame:#5d6358; --water:#9cc7e6; --waterline:#2f78ad; --plant:#5fa052;
          --led:#e0a020; --glow:#f6d76a; --elec:#7a5ea8; --elecfill:#e6ddf3;
          --tray:#e9e7dd; --tub:#3a3f38; --card:#9a9a9a; --wrap:#1f221d; }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#171a16; --fg:#e4e6df; --muted:#9aa193; --line:#6f7669;
            --frame:#a3a99c; --water:#2c5f86; --waterline:#7fc0ee; --plant:#79bd6b;
            --led:#f0b840; --glow:#8a7420; --elec:#b79be0; --elecfill:#34294a;
            --tray:#2a2e27; --tub:#c9cdc2; --card:#8a8a8a; --wrap:#e4e6df; }
  }
  .bg{fill:var(--bg)} text{font:12px system-ui,-apple-system,"Segoe UI",sans-serif;fill:var(--fg)}
  .t{font-size:15px;font-weight:650} .m{fill:var(--muted)} .big{font-size:22px;font-weight:700;fill:var(--muted)}
  .frame{fill:none;stroke:var(--frame);stroke-width:2.5} .shelf{fill:var(--bg);stroke:var(--frame);stroke-width:1.5}
  .wire{stroke:var(--frame);stroke-width:1;stroke-dasharray:3 3} .thin{fill:none;stroke:var(--line);stroke-width:1}
  .lead{fill:none;stroke:var(--muted);stroke-width:.8} .dim{fill:none;stroke:var(--muted);stroke-width:.8}
  .tray{fill:var(--tray);stroke:var(--frame);stroke-width:1.5} .tub{fill:var(--bg);stroke:var(--tub);stroke-width:2}
  .water{fill:var(--water)} .wl{stroke:var(--waterline);stroke-width:1.5;fill:none} .plant{fill:var(--plant)}
  .root{stroke:var(--line);stroke-width:1;fill:none}
  .led{fill:var(--led)} .glow{fill:var(--glow);opacity:.28} .alu{fill:var(--line)}
  .elec{fill:var(--elecfill);stroke:var(--elec);stroke-width:1.5} .cable{fill:none;stroke:var(--elec);stroke-width:1.6}
  .film{stroke:var(--fg);stroke-width:2;fill:none} .curtain{stroke:var(--fg);stroke-width:2;fill:none;stroke-dasharray:7 4}
  .sheet{stroke:var(--fg);stroke-width:2} .cam{fill:var(--fg)} .card{fill:var(--card)} .wrap{fill:var(--wrap)}
  .rod{fill:var(--tub)} .wool{fill:var(--tray);stroke:var(--line)} .dash{stroke-dasharray:5 4}
</style>
"""


class Drawing:
    def __init__(self, w, h, x0, y0, scale, title):
        self.w, self.h, self.x0, self.y0, self.s = w, h, x0, y0, scale
        self.parts = [f'<rect class="bg" width="{w}" height="{h}"/>',
                      f'<text class="t" x="16" y="26">{title}</text>']

    def X(self, cm): return round(self.x0 + cm * self.s, 1)
    def Y(self, cm): return round(self.y0 - cm * self.s, 1)

    def rect(self, x, y, w, h, cls, extra=""):
        """x, y = lower-left corner in cm; w, h in cm."""
        self.parts.append(f'<rect class="{cls}" x="{self.X(x)}" y="{self.Y(y + h)}" '
                          f'width="{round(w * self.s, 1)}" height="{round(h * self.s, 1)}" {extra}/>')

    def line(self, x1, y1, x2, y2, cls):
        self.parts.append(f'<line class="{cls}" x1="{self.X(x1)}" y1="{self.Y(y1)}" '
                          f'x2="{self.X(x2)}" y2="{self.Y(y2)}"/>')

    def path(self, pts, cls, close=False):
        d = "M" + " L".join(f"{self.X(x)},{self.Y(y)}" for x, y in pts) + (" Z" if close else "")
        self.parts.append(f'<path class="{cls}" d="{d}"/>')

    def ellipse(self, x, y, rx, ry, cls):
        self.parts.append(f'<ellipse class="{cls}" cx="{self.X(x)}" cy="{self.Y(y)}" '
                          f'rx="{round(rx * self.s, 1)}" ry="{round(ry * self.s, 1)}"/>')

    def text(self, x, y, s, anchor="start", cls="", dx=0, dy=0):
        self.parts.append(f'<text class="{cls}" x="{self.X(x) + dx}" y="{self.Y(y) + dy}" '
                          f'text-anchor="{anchor}">{s}</text>')

    def label(self, px, py, s, tx, ty, anchor="start", lines=None):
        """Label at pixel position (px, py) with a leader to the point (tx, ty) in cm."""
        rows = [s] + (lines or [])
        for i, row in enumerate(rows):
            cls = "" if i == 0 else "m"
            self.parts.append(f'<text class="{cls}" x="{px}" y="{py + 15 * i}" text-anchor="{anchor}">{row}</text>')
        ex = px + (6 if anchor == "end" else -6)
        self.parts.append(f'<line class="lead" x1="{ex}" y1="{py - 4}" x2="{self.X(tx)}" y2="{self.Y(ty)}"/>')
        self.parts.append(f'<circle cx="{self.X(tx)}" cy="{self.Y(ty)}" r="2" fill="var(--muted)"/>')

    def vdim(self, x, y1, y2, s, side=1):
        """Vertical dimension line with its text rotated alongside."""
        self.line(x, y1, x, y2, "dim")
        for y in (y1, y2):
            self.line(x - .8, y, x + .8, y, "dim")
        px, py = self.X(x) + 13 * side - (0 if side > 0 else 4), self.Y((y1 + y2) / 2)
        self.parts.append(f'<text class="m" text-anchor="middle" transform="translate({px},{py}) rotate(-90)">{s}</text>')

    def hdim(self, x1, x2, y, s):
        self.line(x1, y, x2, y, "dim")
        for x in (x1, x2):
            self.line(x, y - .8, x, y + .8, "dim")
        self.text((x1 + x2) / 2, y, s, "middle", "m", dy=16)

    def plant(self, x, y, size=1.0):
        for dx, dy, rx, ry in ((0, 5, 4.2, 4.6), (-4.2, 3.2, 3.4, 2.6), (4.2, 3.2, 3.4, 2.6), (0, 8.5, 3, 2.4)):
            self.ellipse(x + dx * size, y + dy * size, rx * size, ry * size, "plant")

    def save(self, name, desc):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
               f'width="{self.w}" height="{self.h}" role="img" aria-label="{desc}">'
               f'<title>{desc}</title>{STYLE}' + "\n".join(self.parts) + "</svg>\n")
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / name).write_text(svg)


SHELVES = (8, 62, 116, 170)   # top surface of each shelf above the floor
PITCH = 54


def rack_front():
    d = Drawing(900, 900, 280, 850, 4, "Rack, front view (curtain removed)")
    for x in (0, 92):
        d.rect(x - 1.2, 0, 2.4, 181, "shelf")
    for h in SHELVES:
        d.rect(0, h - 3, 92, 3, "shelf")
        d.line(1, h - 1.5, 91, h - 1.5, "wire")
    d.line(-50, 0, 120, 0, "thin")

    # dry shelf
    d.rect(8, 170, 30, 8, "elec"); d.text(23, 173, "24 V supply", "middle")
    d.rect(42, 170, 14, 5, "elec"); d.text(49, 171.5, "fuses", "middle")
    d.rect(60, 170, 22, 5, "elec"); d.text(71, 171.5, "USB hub", "middle")
    d.path([(38, 176.5), (100, 176.5), (100, 187)], "cable")
    d.text(102, 187, "mains to a wall socket", "start", "m", dy=-2)
    d.text(102, 187, "on an HPFI breaker", "start", "m", dy=13)

    zone = iter("ABCD")
    for h in (116, 62):
        top = h + PITCH - 3
        d.line(2, h + .4, 90, h + .4, "sheet")
        d.line(46, h + 1, 46, top, "film")
        for zx in (3, 47):
            d.path([(zx + 4, top - 2), (zx + 38, top - 2), (zx + 42, h + 27), (zx, h + 27)], "glow", True)
            d.rect(zx, h + .6, 42, 10, "tray")
            for tx in (zx + 5, zx + 26):
                d.rect(tx, h + 1.6, 11, 10, "tub")
                d.rect(tx + .4, h + 2, 10.2, 6.5, "water")
                d.rect(tx - .5, h + 11.6, 12, .8, "wrap")
                d.plant(tx + 5.5, h + 12, .85)
            d.rect(zx + 3, top - 1.4, 36, 1.4, "alu")
            d.rect(zx + 3, top - 2.2, 36, .8, "led")
            d.rect(zx + 19, top - 5.2, 4, 3, "cam")
            d.text(zx + 21, h + 36, next(zone), "middle", "big")
        # controller boxes outside the end frames; every cable enters from below
        for bx, trunk, mid, inner, post in ((-17, -3, -11, -6.5, 2.5), (97, 95, 103, 98.5, 89.5)):
            d.rect(bx, h + 36, 12, 11, "elec")
            d.text(bx + 6, h + 40.5, "box", "middle")
            d.path([(trunk, h + 32), (mid, h + 32), (mid, h + 36)], "cable")
            d.path([(inner, h + 36), (inner, h + 34), (post, h + 34), (post, top - 2.2)], "cable")
    # supply and USB trunks run down between the frame and the boxes
    d.path([(8, 172), (-3, 172), (-3, 62 + 32)], "cable")
    d.path([(82, 172), (95, 172), (95, 62 + 32)], "cable")

    # nursery level
    d.rect(8, 8.6, 54, 6, "tray")
    for i in range(9):
        d.ellipse(12 + i * 5.7, 16.2, 1.6, 1.4, "plant")
    d.rect(8, 57.6, 54, 1.4, "alu"); d.rect(8, 56.8, 54, .8, "led")
    d.rect(68, 8.2, 20, 16, "shelf"); d.text(78, 15, "spares", "middle", "m")

    L = 190
    d.label(L, 110, "Dry shelf", 8, 174, "end", ["supply, fuses and hub,", "above all the water"])
    d.label(L, 178, "LED bars and camera", 8, 165.5, "end", ["under the shelf above"])
    d.label(L, 232, "Controller box", -17, 160, "end", ["outside the frame,", "cables enter from below"])
    d.label(L, 304, "Drip loop", -11, 148, "end", ["each cable dips below", "where it enters"])
    d.label(L, 380, "Spill tray", 3, 122, "end", ["42 x 30 x 10 cm, holds", "all four tubs' water"])
    d.label(L, 452, "Liner sheet", 3, 116.4, "end", ["stops drips and light", "between levels"])
    d.label(L, 740, "Nursery tray", 8, 12, "end", ["seedlings, weeks 1 to 3,", "under a white bar"])
    R = 752
    d.label(R, 330, "Divider", 46, 145, "start", ["black-and-white film,", "white side to plants"])
    d.label(R, 420, "Tubs", 78.5, 124, "start", ["four per zone,", "opaque, one plant each"])
    d.label(R, 560, "Zones A to D", 68, 98, "start", ["each with its own", "lights, camera, box"])
    d.vdim(111, 116, 170, "54 cm between shelves")
    d.vdim(-61, 0, 181, "181 cm", -1)
    d.hdim(0, 92, -4, "92 cm wide, 36 cm deep")
    d.save("rack-front.svg", "Front view of the shelf rack with four light zones, a dry shelf on top and a nursery tray at the bottom")


def zone_section():
    d = Drawing(880, 690, 260, 600, 9, "One zone, side view (back of the rack on the left)")
    d.rect(-1, -3, 38, 3, "shelf"); d.line(0, -1.5, 36, -1.5, "wire")
    d.rect(-1, 51, 38, 3, "shelf"); d.line(0, 52.5, 36, 52.5, "wire")
    d.line(.3, .4, 35.7, .4, "sheet")
    d.line(0, .4, 0, 51, "film")
    d.path([(36, 51), (36.6, 44), (35.6, 37), (36.6, 30), (35.6, 23), (36.6, 16), (35.6, 9), (36.2, 1)], "curtain")
    # light
    d.path([(4, 49), (32, 49), (34, 26), (2, 26)], "glow", True)
    for x, cls in ((5, "led"), (29, "led")):
        d.rect(x, 50, 4, 1, "alu"); d.rect(x + .5, 49.3, 3, .7, cls)
    d.rect(21, 50, 5, 1, "alu")
    for i in range(3):
        d.rect(21.5 + i * 1.5, 49.3, 1, .7, "led")
    d.rect(13, 47.2, 4, 3.8, "cam"); d.ellipse(15, 46.8, 1, .6, "cam")
    # fan on the back
    d.rect(.5, 34, 2.5, 10, "elec")
    for y in (36, 39, 42):
        d.path([(4, y), (9, y)], "lead"); d.path([(8, y + .6), (9, y), (8, y - .6)], "lead")
    # tray, tubs, plants
    d.rect(3, .6, 30, 10, "tray")
    for tx in (5, 20):
        d.rect(tx, 1.6, 11, 10, "tub"); d.rect(tx + .3, 1.9, 10.4, 6.6, "water")
        d.rect(tx - .5, 11.6, 12, .8, "wrap"); d.plant(tx + 5.5, 12, 1.05)
    # sensors
    d.line(18, 1, 18, 24, "thin"); d.rect(16.6, 24, 2.8, 1, "elec")
    d.rect(1, 28, 2, 2, "elec"); d.path([(.5, 31), (4, 31)], "film")
    L = 215
    d.label(L, 90, "Wire shelf above", -1, 52.5, "end", ["carries the next zone up"])
    d.label(L, 190, "Fan", .5, 40, "end", ["moves air across the leaves"])
    d.label(L, 290, "Air sensor", 1, 29, "end", ["temperature and humidity,", "shaded from the LEDs"])
    d.label(L, 390, "Back wall", 0, 20, "end", ["black-and-white film"])
    d.label(L, 520, "Spill tray", 3, 6, "end", ["on a liner sheet"])
    R = 670
    d.label(R, 80, "White strips", 31, 49.6, "start", ["two rows, on aluminium bar"])
    d.label(R, 132, "Colour bar", 24, 49.6, "start", ["red, blue and UV-A LEDs"])
    d.label(R, 184, "Camera", 15, 48, "start", ["looks straight down,", "fixed exposure and focus"])
    d.label(R, 270, "Front curtain", 36.2, 34, "start", ["lifts for access"])
    d.label(R, 350, "Light sensor", 18, 24.6, "start", ["at leaf height, facing up"])
    d.label(R, 410, "Plants", 27, 19, "start", ["leaf tops 20 cm or more", "below the LEDs"])
    d.label(R, 500, "Tub", 31, 6, "start", ["opaque, lidded, 0.8 to 1 L"])
    d.vdim(39.5, 0, 54, "54 cm")
    d.hdim(0, 36, -5, "36 cm deep")
    d.save("zone-section.svg", "Side view of one light zone showing LEDs, camera, fan, plants in tubs and the spill tray")


def tub_detail():
    d = Drawing(860, 560, 270, 470, 30, "One tub, cut through the middle")
    d.rect(-.25, 0, 11.5, 10.3, "wrap")
    d.rect(0, .25, 11, 10.05, "bg")
    d.rect(.15, .4, 10.7, 6.2, "water")
    d.line(.15, 6.6, 10.85, 6.6, "wl")
    d.line(.15, 3.2, 10.85, 3.2, "wl dash")
    # lid with 5 cm hole
    d.rect(-.5, 10.3, 3.5, .5, "wrap"); d.rect(8, 10.3, 3.5, .5, "wrap")
    # net pot
    d.path([(2.8, 10.9), (8.2, 10.9), (7.5, 5.6), (3.5, 5.6)], "tub", True)
    for x in (4.3, 5.5, 6.7):
        d.line(x, 5.8, x, 7.6, "thin")
    d.rect(3.7, 6.3, 3.6, 4, "wool")
    # roots
    for i, x in enumerate((4.2, 4.9, 5.5, 6.1, 6.8)):
        d.path([(x, 6.3), (x - .3 + .2 * i, 4.5), (x + .25 - .1 * i, 2.8), (x - .2, 1.2 + .15 * i)], "root")
    d.plant(5.5, 10.4, .3)
    # electrodes and probe
    for x in (.9, 9.5):
        d.rect(x, 1, .6, 10.8, "rod")
        d.path([(x + .3, 11.8), (x + .3, 12.6), (x + .3 + (1.5 if x > 5 else -1.5), 13.2)], "cable")
    d.rect(2.05, 2.2, .3, 9.4, "elec")
    d.label(215, 96, "Lid", -.5, 10.55, "end", ["with a 5 cm hole for the pot", "and small holes for the rods"])
    d.label(215, 186, "Light-proof wall", -.2, 8, "end", ["black tape or paint outside,", "so no algae grow"])
    d.label(215, 276, "Temperature probe", 2.2, 5, "end", ["in one tub per zone"])
    d.label(215, 352, "Graphite rods", 1.2, 3, "end", ["only in tubs that get current,", "on opposite sides of the roots"])
    R = 640
    d.label(R, 96, "Net pot and rockwool cube", 7.4, 9, "start", ["the seedling moves here", "from the nursery"])
    d.label(R, 186, "Air gap", 9, 8.2, "start", ["roots here breathe;", "do not refill to the brim"])
    d.label(R, 276, "Starting level", 10.4, 6.6, "start", ["wets the bottom centimetre", "of the pot"])
    d.label(R, 356, "Level after a week or two", 10.4, 3.2, "start", ["top up to about halfway"])
    d.hdim(0, 11, -.7, "about 11 cm")
    d.save("tub-detail.svg", "Cross-section of a growing tub with net pot, nutrient solution, air gap and optional graphite electrodes")


def zone_plan():
    d = Drawing(900, 560, 250, 480, 10, "One zone, seen from above (front of the rack at the bottom)")
    # the y axis here is depth: 0 = front, 36 = back
    d.rect(0, 0, 45, 36, "thin")
    d.line(0, 36, 45, 36, "film")
    d.line(45, 0, 45, 36, "film")
    d.path([(0, 0), (6, .6), (12, -.6), (18, .6), (24, -.6), (30, .6), (36, -.6), (45, 0)], "curtain")
    d.rect(1.5, 3, 42, 30, "tray")
    n = 1
    for y in (25.5, 10.5):
        for x in (12, 33):
            d.rect(x - 5.5, y - 5.5, 11, 11, "tub")
            d.ellipse(x, y, 4.6, 4.6, "plant")
            d.text(x, y, str(n), "middle", "t", dy=5); n += 1
    d.rect(18.5, 14.2, 8, 5, "card")
    d.rect(21.2, 24.2, 2.6, 2.6, "elec")
    for y in (29, 7):
        d.parts.append(f'<line x1="{d.X(4)}" y1="{d.Y(y)}" x2="{d.X(41)}" y2="{d.Y(y)}" '
                       f'stroke="var(--led)" stroke-width="3" stroke-dasharray="8 5"/>')
    d.parts.append(f'<line x1="{d.X(8)}" y1="{d.Y(13)}" x2="{d.X(37)}" y2="{d.Y(13)}" '
                   f'stroke="var(--led)" stroke-width="5" stroke-dasharray="3 9"/>')
    d.parts.append(f'<circle cx="{d.X(22.5)}" cy="{d.Y(21.3)}" r="14" fill="none" stroke="var(--fg)" '
                   f'stroke-width="2" stroke-dasharray="3 3"/>')
    d.rect(-13, 12, 10, 12, "elec"); d.text(-8, 17.5, "box", "middle", dy=4)
    d.path([(-3, 18), (0, 18)], "cable")
    d.text(-8, 12, "controller box,", "middle", "m", dy=16)
    d.text(-8, 12, "outside the frame", "middle", "m", dy=31)
    d.text(22.5, 36, "back wall (film)", "middle", "m", dy=-8)
    d.text(22.5, 0, "front curtain", "middle", "m", dy=20)
    R = 730
    d.label(R, 96, "White strips above", 41, 29, "start", ["two dashed rows"])
    d.label(R, 156, "Light sensor", 23.8, 25.5, "start", ["on a stalk at leaf height"])
    d.label(R, 212, "Camera above", 23.9, 21.3, "start", ["centred over the tray"])
    d.label(R, 268, "Grey card", 26.5, 16, "start", ["flat, in every photo"])
    d.label(R, 324, "Colour bar above", 37, 13, "start", ["dotted row"])
    d.label(R, 380, "Tub positions 1 to 4", 38.5, 8, "start", ["each tub keeps a label;", "its position is logged"])
    d.label(R, 452, "Divider to next zone", 45, 3, "start")
    d.hdim(0, 45, -3.4, "45 cm (half the shelf)")
    d.vdim(-17, 0, 36, "36 cm", -1)
    d.save("zone-plan.svg", "Top view of one light zone with four tubs in a spill tray, grey card, light sensor and camera position")


if __name__ == "__main__":
    rack_front()
    zone_section()
    tub_detail()
    zone_plan()
    print("wrote", ", ".join(sorted(p.name for p in OUT.glob("*.svg"))))
