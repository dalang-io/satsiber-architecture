"""
Generate DXF (AutoCAD-compatible) technical drawings for Satsiber Data Center.
Uptime Institute Tier III Design Certification documentation.

Standards: IEC 60617, TIA-942, ASHRAE TC 9.9, NFPA 75/2001
Output: DXF R2018 format (compatible with AutoCAD, BricsCAD, LibreCAD, etc.)

Usage:
    uv run generate_dxf.py
"""

import ezdxf
from ezdxf import units
from ezdxf.enums import TextEntityAlignment
from pathlib import Path
import math

OUTPUT_DIR = Path("build/dxf")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Standard colors (AutoCAD Color Index)
WHITE = 7
RED = 1
YELLOW = 2
GREEN = 3
CYAN = 4
BLUE = 5
MAGENTA = 6
GRAY = 8
LIGHT_GRAY = 9
DARK_RED = 14
DARK_GREEN = 94
DARK_BLUE = 174


def add_title_block(msp, dwg_no, title_line1, title_line2, standard, x_off=0, y_off=0):
    """Add standard architectural title block."""
    bx = x_off
    by = y_off

    # Outer frame
    msp.add_lwpolyline(
        [(bx, by), (bx + 570, by), (bx + 570, by + 140),
         (bx, by + 140), (bx, by)],
        dxfattribs={"color": WHITE, "lineweight": 50}
    )

    # Logo section
    msp.add_text("SATSIBER", dxfattribs={"height": 18, "color": WHITE, "style": "TITLE"}).set_placement(
        (bx + 100, by + 115), align=TextEntityAlignment.MIDDLE_CENTER
    )
    msp.add_text("DATA CENTER FACILITY", dxfattribs={"height": 6, "color": GRAY}).set_placement(
        (bx + 100, by + 95), align=TextEntityAlignment.MIDDLE_CENTER
    )

    # Vertical divider
    msp.add_line((bx + 200, by), (bx + 200, by + 140), dxfattribs={"color": WHITE})

    # Drawing title
    msp.add_text("DRAWING TITLE:", dxfattribs={"height": 4, "color": GRAY}).set_placement(
        (bx + 210, by + 125)
    )
    msp.add_text(title_line1, dxfattribs={"height": 8, "color": WHITE, "style": "TITLE"}).set_placement(
        (bx + 210, by + 112)
    )
    msp.add_text(title_line2, dxfattribs={"height": 7, "color": WHITE}).set_placement(
        (bx + 210, by + 100)
    )

    # Horizontal divider
    msp.add_line((bx + 200, by + 90), (bx + 570, by + 90), dxfattribs={"color": WHITE})

    # DWG info row
    msp.add_text(f"DWG NO: {dwg_no}", dxfattribs={"height": 6, "color": WHITE}).set_placement(
        (bx + 210, by + 75)
    )
    msp.add_text("REV: A", dxfattribs={"height": 6, "color": WHITE}).set_placement(
        (bx + 380, by + 75)
    )
    msp.add_text("DATE: 2026-02-27", dxfattribs={"height": 6, "color": WHITE}).set_placement(
        (bx + 450, by + 75)
    )

    # Horizontal divider
    msp.add_line((bx + 200, by + 65), (bx + 570, by + 65), dxfattribs={"color": WHITE})

    # Scale and standard
    msp.add_text("SCALE: NTS", dxfattribs={"height": 5, "color": WHITE}).set_placement(
        (bx + 210, by + 50)
    )
    msp.add_text(f"STD: {standard}", dxfattribs={"height": 5, "color": WHITE}).set_placement(
        (bx + 350, by + 50)
    )

    # Horizontal divider
    msp.add_line((bx + 200, by + 40), (bx + 570, by + 40), dxfattribs={"color": WHITE})

    msp.add_text("UPTIME TIER III", dxfattribs={"height": 7, "color": RED, "style": "TITLE"}).set_placement(
        (bx + 210, by + 20)
    )

    # Designer info (left column)
    msp.add_line((bx, by + 90), (bx + 200, by + 90), dxfattribs={"color": WHITE})
    msp.add_text("DESIGNED: SATSIBER ENGINEERING", dxfattribs={"height": 5, "color": WHITE}).set_placement(
        (bx + 10, by + 70)
    )
    msp.add_line((bx, by + 60), (bx + 200, by + 60), dxfattribs={"color": WHITE})
    msp.add_text("CHECKED: ___________", dxfattribs={"height": 5, "color": GRAY}).set_placement(
        (bx + 10, by + 42)
    )
    msp.add_line((bx, by + 30), (bx + 200, by + 30), dxfattribs={"color": WHITE})
    msp.add_text("APPROVED: ___________", dxfattribs={"height": 5, "color": GRAY}).set_placement(
        (bx + 10, by + 14)
    )


def add_border(msp, width=1180, height=840):
    """Add drawing border frame."""
    msp.add_lwpolyline(
        [(0, 0), (width, 0), (width, height), (0, height), (0, 0)],
        dxfattribs={"color": WHITE, "lineweight": 70}
    )
    msp.add_lwpolyline(
        [(5, 5), (width - 5, 5), (width - 5, height - 5), (5, height - 5), (5, 5)],
        dxfattribs={"color": WHITE, "lineweight": 18}
    )


def add_room_box(msp, x, y, w, h, label, ref, color=WHITE, fill_pattern=None):
    """Add a labeled room rectangle with reference tag."""
    msp.add_lwpolyline(
        [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)],
        dxfattribs={"color": color, "lineweight": 35}
    )
    msp.add_text(label, dxfattribs={"height": 6, "color": color, "style": "TITLE"}).set_placement(
        (x + w / 2, y + h - 10), align=TextEntityAlignment.MIDDLE_CENTER
    )
    # Reference tag
    msp.add_text(ref, dxfattribs={"height": 4, "color": RED}).set_placement(
        (x + w - 5, y + h - 5), align=TextEntityAlignment.MIDDLE_RIGHT
    )


def add_equipment(msp, x, y, w, h, label, tag, color=CYAN, dashed=False):
    """Add equipment block."""
    pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
    attribs = {"color": color, "lineweight": 25}
    if dashed:
        attribs["linetype"] = "DASHED"
    msp.add_lwpolyline(pts, dxfattribs=attribs)
    msp.add_text(label, dxfattribs={"height": 4, "color": color}).set_placement(
        (x + w / 2, y + h / 2 + 2), align=TextEntityAlignment.MIDDLE_CENTER
    )
    msp.add_text(tag, dxfattribs={"height": 3, "color": color}).set_placement(
        (x + w / 2, y + h / 2 - 4), align=TextEntityAlignment.MIDDLE_CENTER
    )


def add_bus_bar(msp, x, y, length, label, color=WHITE, horizontal=True):
    """Add a thick bus bar line with label."""
    if horizontal:
        msp.add_lwpolyline(
            [(x, y), (x + length, y)],
            dxfattribs={"color": color, "lineweight": 70}
        )
        msp.add_text(label, dxfattribs={"height": 4, "color": color}).set_placement(
            (x + length / 2, y - 8), align=TextEntityAlignment.MIDDLE_CENTER
        )
    else:
        msp.add_lwpolyline(
            [(x, y), (x, y + length)],
            dxfattribs={"color": color, "lineweight": 70}
        )


def add_generator_symbol(msp, cx, cy, radius, label, tag, color=WHITE):
    """Add IEC 60617 generator symbol (circle with G)."""
    msp.add_circle((cx, cy), radius, dxfattribs={"color": color, "lineweight": 35})
    msp.add_text("G", dxfattribs={"height": radius * 1.2, "color": color, "style": "TITLE"}).set_placement(
        (cx, cy), align=TextEntityAlignment.MIDDLE_CENTER
    )
    msp.add_text(label, dxfattribs={"height": 3.5, "color": color}).set_placement(
        (cx, cy - radius - 6), align=TextEntityAlignment.MIDDLE_CENTER
    )
    msp.add_text(tag, dxfattribs={"height": 3, "color": CYAN}).set_placement(
        (cx, cy - radius - 12), align=TextEntityAlignment.MIDDLE_CENTER
    )


def add_transformer_symbol(msp, cx, cy, radius, label, color=WHITE):
    """Add IEC 60617 transformer symbol (two overlapping circles)."""
    msp.add_circle((cx, cy + radius * 0.4), radius, dxfattribs={"color": color, "lineweight": 35})
    msp.add_circle((cx, cy - radius * 0.4), radius, dxfattribs={"color": color, "lineweight": 35})
    msp.add_text(label, dxfattribs={"height": 3.5, "color": color}).set_placement(
        (cx + radius + 5, cy), align=TextEntityAlignment.MIDDLE_LEFT
    )


def add_cb_symbol(msp, x, y, label="CB", color=WHITE):
    """Add circuit breaker symbol."""
    s = 4
    msp.add_lwpolyline(
        [(x - s, y - s / 2), (x + s, y - s / 2), (x + s, y + s / 2),
         (x - s, y + s / 2), (x - s, y - s / 2)],
        dxfattribs={"color": color, "lineweight": 18}
    )
    msp.add_text(label, dxfattribs={"height": 2.5, "color": color}).set_placement(
        (x, y), align=TextEntityAlignment.MIDDLE_CENTER
    )


def create_text_style(doc, name, font="Arial"):
    """Create a text style."""
    if name not in doc.styles:
        doc.styles.new(name, dxfattribs={"font": font})


def setup_doc():
    """Create a new DXF document with standard setup."""
    doc = ezdxf.new("R2018")
    doc.units = units.MM
    create_text_style(doc, "TITLE", "Arial")
    create_text_style(doc, "NOTES", "Arial")

    # Add linetypes
    if "DASHED" not in doc.linetypes:
        doc.linetypes.add("DASHED", pattern=[10.0, 5.0, -5.0])
    if "DASHDOT" not in doc.linetypes:
        doc.linetypes.add("DASHDOT", pattern=[14.0, 5.0, -3.0, 0.0, -3.0])

    return doc


# ============================================================
# 1. FLOOR PLAN
# ============================================================
def generate_floor_plan():
    doc = setup_doc()
    msp = doc.modelspace()

    W, H = 1180, 840
    add_border(msp, W, H)

    # Title block
    add_title_block(msp, "SAT-DC-FP-001",
                    "DATA CENTER FLOOR PLAN",
                    "GENERAL ARRANGEMENT",
                    "UPTIME TIER III",
                    x_off=600, y_off=10)

    # Building envelope
    msp.add_lwpolyline(
        [(30, 170), (580, 170), (580, 810), (30, 810), (30, 170)],
        dxfattribs={"color": GRAY, "lineweight": 50}
    )
    msp.add_text("BUILDING ENVELOPE", dxfattribs={"height": 5, "color": GRAY}).set_placement((35, 805))

    # Security Vestibule
    add_room_box(msp, 230, 760, 120, 40, "SECURITY VESTIBULE", "R-01", color=GRAY)

    # Lobby
    add_room_box(msp, 230, 710, 120, 45, "LOBBY", "R-02", color=GRAY)

    # Data Hall (main space)
    add_room_box(msp, 140, 320, 380, 380, "DATA HALL", "R-03", color=CYAN)
    msp.add_text("AREA: ~280 m²  |  RAISED FLOOR: 600mm  |  FLOOR LOAD: 12 kPa",
                 dxfattribs={"height": 3.5, "color": CYAN}).set_placement(
        (330, 330), align=TextEntityAlignment.MIDDLE_CENTER
    )

    # Rack rows inside data hall
    row_labels = ["A", "B", "C", "D", "E", "F"]
    row_y = 660
    for i, label in enumerate(row_labels):
        ry = row_y - i * 52
        # Rack row
        msp.add_lwpolyline(
            [(160, ry), (500, ry), (500, ry + 12), (160, ry + 12), (160, ry)],
            dxfattribs={"color": WHITE, "lineweight": 35}
        )
        rack_ids = " | ".join([f"{label}{j:02d}" for j in range(1, 13)])
        msp.add_text(f"ROW {label} — {rack_ids}",
                     dxfattribs={"height": 2.5, "color": WHITE}).set_placement(
            (330, ry + 6), align=TextEntityAlignment.MIDDLE_CENTER
        )

        # Hot/cold aisle labels (between rows)
        if i % 2 == 0 and i < len(row_labels) - 1:
            msp.add_text("COLD AISLE", dxfattribs={"height": 2.5, "color": BLUE}).set_placement(
                (165, ry - 5)
            )
        elif i % 2 == 1 and i < len(row_labels) - 1:
            msp.add_text("HOT AISLE (CONTAINED)", dxfattribs={"height": 2.5, "color": RED}).set_placement(
                (165, ry - 5)
            )

    # UPS Room A
    add_room_box(msp, 30, 560, 100, 130, "UPS ROOM A", "R-04", color=YELLOW)
    add_equipment(msp, 40, 640, 35, 20, "UPS-A1", "400kVA", color=YELLOW)
    add_equipment(msp, 80, 640, 35, 20, "UPS-A2", "400kVA", color=YELLOW)
    add_equipment(msp, 40, 610, 35, 20, "UPS-A3", "(N+1)", color=YELLOW, dashed=True)
    add_equipment(msp, 40, 575, 75, 15, "STS-A", "", color=GREEN)
    add_equipment(msp, 40, 565, 75, 10, "BATTERY A", "VRLA", color=RED)

    # UPS Room B
    add_room_box(msp, 30, 400, 100, 130, "UPS ROOM B", "R-05", color=YELLOW)
    add_equipment(msp, 40, 480, 35, 20, "UPS-B1", "400kVA", color=YELLOW)
    add_equipment(msp, 80, 480, 35, 20, "UPS-B2", "400kVA", color=YELLOW)
    add_equipment(msp, 40, 450, 35, 20, "UPS-B3", "(N+1)", color=YELLOW, dashed=True)
    add_equipment(msp, 40, 415, 75, 15, "STS-B", "", color=GREEN)
    add_equipment(msp, 40, 405, 75, 10, "BATTERY B", "VRLA", color=RED)

    # Electrical Room
    add_room_box(msp, 30, 260, 100, 110, "ELECTRICAL ROOM", "R-06", color=MAGENTA)
    msp.add_text("XFMR-A  XFMR-B", dxfattribs={"height": 3, "color": MAGENTA}).set_placement(
        (80, 340), align=TextEntityAlignment.MIDDLE_CENTER
    )
    msp.add_text("ATS-A   ATS-B", dxfattribs={"height": 3, "color": MAGENTA}).set_placement(
        (80, 325), align=TextEntityAlignment.MIDDLE_CENTER
    )
    msp.add_text("MSB-A   MSB-B", dxfattribs={"height": 3, "color": MAGENTA}).set_placement(
        (80, 310), align=TextEntityAlignment.MIDDLE_CENTER
    )

    # Generator Yard
    msp.add_lwpolyline(
        [(30, 170), (300, 170), (300, 250), (30, 250), (30, 170)],
        dxfattribs={"color": GREEN, "lineweight": 35, "linetype": "DASHED"}
    )
    msp.add_text("GENERATOR YARD (OUTDOOR)", dxfattribs={"height": 5, "color": GREEN, "style": "TITLE"}).set_placement(
        (35, 240)
    )
    add_equipment(msp, 40, 185, 70, 40, "GEN-A", "2000kVA DIESEL", color=GREEN)
    add_equipment(msp, 120, 185, 70, 40, "GEN-B", "2000kVA DIESEL", color=GREEN)
    add_equipment(msp, 200, 185, 70, 40, "GEN-C (N+1)", "2000kVA DIESEL", color=GREEN, dashed=True)

    # NOC
    add_room_box(msp, 530, 600, 130, 110, "NOC", "R-08", color=BLUE)
    msp.add_text("NETWORK OPERATIONS CENTER", dxfattribs={"height": 3, "color": BLUE}).set_placement(
        (595, 670), align=TextEntityAlignment.MIDDLE_CENTER
    )
    msp.add_text("VIDEO WALL  |  6 OPERATOR STATIONS", dxfattribs={"height": 3, "color": BLUE}).set_placement(
        (595, 650), align=TextEntityAlignment.MIDDLE_CENTER
    )
    msp.add_text("BMS / DCIM MONITORING", dxfattribs={"height": 3, "color": BLUE}).set_placement(
        (595, 635), align=TextEntityAlignment.MIDDLE_CENTER
    )

    # Meet-Me Room
    add_room_box(msp, 530, 470, 130, 110, "MEET-ME ROOM", "R-09", color=MAGENTA)
    msp.add_text("CARRIER ENTRY A (DIVERSE)", dxfattribs={"height": 3, "color": MAGENTA}).set_placement(
        (540, 540)
    )
    msp.add_text("CARRIER ENTRY B (DIVERSE)", dxfattribs={"height": 3, "color": MAGENTA}).set_placement(
        (540, 525)
    )
    msp.add_text("CROSS-CONNECT PANELS", dxfattribs={"height": 3, "color": MAGENTA}).set_placement(
        (540, 510)
    )

    # Cooling Plant
    add_room_box(msp, 530, 345, 130, 110, "COOLING PLANT", "R-10", color=CYAN)

    # Staging
    add_room_box(msp, 530, 250, 130, 80, "STAGING & LOADING", "R-11", color=GRAY)

    # Fire Control
    add_room_box(msp, 370, 720, 110, 60, "FIRE CONTROL", "R-13", color=RED)
    msp.add_text("FACP (REDUNDANT)", dxfattribs={"height": 3, "color": RED}).set_placement(
        (425, 740), align=TextEntityAlignment.MIDDLE_CENTER
    )

    # Cooling Yard
    msp.add_lwpolyline(
        [(310, 170), (580, 170), (580, 250), (310, 250), (310, 170)],
        dxfattribs={"color": CYAN, "lineweight": 35, "linetype": "DASHED"}
    )
    msp.add_text("COOLING YARD (OUTDOOR)", dxfattribs={"height": 5, "color": CYAN, "style": "TITLE"}).set_placement(
        (315, 240)
    )
    add_equipment(msp, 320, 185, 60, 40, "CHILLER A", "500kW", color=CYAN)
    add_equipment(msp, 390, 185, 60, 40, "CHILLER B", "500kW", color=CYAN)
    add_equipment(msp, 460, 185, 60, 40, "CHILLER C", "(N+1)", color=CYAN, dashed=True)

    # North arrow
    msp.add_text("N", dxfattribs={"height": 8, "color": WHITE, "style": "TITLE"}).set_placement(
        (20, 825), align=TextEntityAlignment.MIDDLE_CENTER
    )
    msp.add_line((20, 815), (20, 830), dxfattribs={"color": WHITE, "lineweight": 35})

    # Legend
    lx, ly = 680, 810
    msp.add_text("LEGEND", dxfattribs={"height": 6, "color": WHITE, "style": "TITLE"}).set_placement((lx, ly))
    msp.add_line((lx, ly - 5), (lx + 160, ly - 5), dxfattribs={"color": WHITE})
    legend_items = [
        (CYAN, "Data Hall"), (YELLOW, "UPS / Power Room"),
        (GREEN, "Generator Yard"), (BLUE, "NOC / Operations"),
        (MAGENTA, "Meet-Me Room / Electrical"), (RED, "Fire Control"),
        (GRAY, "Support / Non-Critical"),
    ]
    for i, (c, t) in enumerate(legend_items):
        y = ly - 15 - i * 12
        msp.add_lwpolyline(
            [(lx, y), (lx + 10, y), (lx + 10, y + 6), (lx, y + 6), (lx, y)],
            dxfattribs={"color": c}
        )
        msp.add_text(t, dxfattribs={"height": 4, "color": WHITE}).set_placement((lx + 15, y + 3))

    out = OUTPUT_DIR / "SAT-DC-FP-001_Floor-Plan.dxf"
    doc.saveas(out)
    print(f"  {out}")


# ============================================================
# 2. ELECTRICAL SINGLE LINE DIAGRAM
# ============================================================
def generate_electrical():
    doc = setup_doc()
    msp = doc.modelspace()

    W, H = 1180, 840
    add_border(msp, W, H)
    add_title_block(msp, "SAT-DC-EL-001",
                    "ELECTRICAL SINGLE LINE DIAGRAM",
                    "MAIN POWER DISTRIBUTION",
                    "IEC 60617 / IEEE C2",
                    x_off=600, y_off=10)

    # PATH A label
    msp.add_text("DISTRIBUTION PATH A", dxfattribs={"height": 8, "color": WHITE, "style": "TITLE"}).set_placement(
        (220, 800), align=TextEntityAlignment.MIDDLE_CENTER
    )

    # PATH B label
    msp.add_text("DISTRIBUTION PATH B", dxfattribs={"height": 8, "color": WHITE, "style": "TITLE"}).set_placement(
        (680, 800), align=TextEntityAlignment.MIDDLE_CENTER
    )

    # Concurrent maintainability separator
    msp.add_line((450, 180), (450, 810), dxfattribs={"color": RED, "linetype": "DASHDOT"})
    msp.add_text("CONCURRENT MAINTAINABILITY BOUNDARY",
                 dxfattribs={"height": 3.5, "color": RED, "rotation": 90}).set_placement((443, 400))

    for path, cx in [("A", 220), ("B", 680)]:
        # Utility Feed
        msp.add_text(f"UTILITY FEED {path}", dxfattribs={"height": 5, "color": WHITE}).set_placement(
            (cx, 775), align=TextEntityAlignment.MIDDLE_CENTER
        )
        msp.add_text("PLN 20kV 3φ", dxfattribs={"height": 3.5, "color": GRAY}).set_placement(
            (cx, 765), align=TextEntityAlignment.MIDDLE_CENTER
        )
        msp.add_text(f"UF-{path}", dxfattribs={"height": 3.5, "color": CYAN}).set_placement(
            (cx - 50, 770)
        )

        # Line down to MV bus
        msp.add_line((cx, 760), (cx, 740), dxfattribs={"color": WHITE, "lineweight": 35})
        add_cb_symbol(msp, cx, 745)

        # MV Switchgear bus
        add_bus_bar(msp, cx - 120, 720, 240, f"MV SWITCHGEAR {path} — 20kV BUS", color=WHITE)
        msp.add_text(f"MVSG-{path}", dxfattribs={"height": 3.5, "color": CYAN}).set_placement(
            (cx - 130, 722)
        )

        # Generator
        gen_x = cx - 150 if path == "A" else cx + 150
        add_generator_symbol(msp, gen_x, 700, 12, f"GEN-{path}", "2000kVA DIESEL", color=WHITE)
        msp.add_line((gen_x + 12, 700), (cx - 120, 720) if path == "A" else (cx + 120, 720),
                     dxfattribs={"color": WHITE, "lineweight": 25})
        msp.add_text(f"ATS-{path}", dxfattribs={"height": 3, "color": GREEN}).set_placement(
            (gen_x + 15, 710) if path == "A" else (gen_x - 30, 710)
        )

        # Transformer
        msp.add_line((cx, 720), (cx, 680), dxfattribs={"color": WHITE, "lineweight": 35})
        add_transformer_symbol(msp, cx, 665, 8, f"XFMR-{path}  2000kVA  20kV/415V  Dyn11", color=WHITE)

        # LV Switchboard bus
        msp.add_line((cx, 652), (cx, 620), dxfattribs={"color": WHITE, "lineweight": 35})
        add_bus_bar(msp, cx - 120, 620, 240, f"LV MAIN SWITCHBOARD {path} — 415V BUS", color=WHITE)
        msp.add_text(f"MSB-{path}", dxfattribs={"height": 3.5, "color": CYAN}).set_placement(
            (cx - 130, 622)
        )

        # UPS
        msp.add_line((cx, 620), (cx, 570), dxfattribs={"color": WHITE, "lineweight": 35})
        add_cb_symbol(msp, cx, 590)
        add_equipment(msp, cx - 45, 520, 90, 45, "UPS", f"UPS-{path}1/{path}2/{path}3(N+1)", color=YELLOW)
        msp.add_text("3×400kVA (2+1)", dxfattribs={"height": 3, "color": GRAY}).set_placement(
            (cx, 525), align=TextEntityAlignment.MIDDLE_CENTER
        )

        # Battery
        msp.add_text(f"BATT-{path}", dxfattribs={"height": 3, "color": RED}).set_placement(
            (cx - 70, 540)
        )
        msp.add_text("VRLA 15min", dxfattribs={"height": 2.5, "color": RED}).set_placement(
            (cx - 70, 533)
        )
        msp.add_line((cx - 55, 540), (cx - 45, 540), dxfattribs={"color": RED, "lineweight": 25})

        # Maintenance bypass
        bp_x = cx + 80
        msp.add_line((bp_x, 620), (bp_x, 470), dxfattribs={"color": GRAY, "linetype": "DASHED"})
        msp.add_text("MAINT. BYPASS", dxfattribs={"height": 3, "color": GRAY}).set_placement(
            (bp_x + 5, 550)
        )

        # STS output bus
        msp.add_line((cx, 520), (cx, 470), dxfattribs={"color": WHITE, "lineweight": 35})
        add_bus_bar(msp, cx - 120, 470, 240, f"STS-{path} OUTPUT BUS — 415V", color=GREEN)
        msp.add_text(f"STS-{path}", dxfattribs={"height": 3.5, "color": GREEN}).set_placement(
            (cx - 130, 472)
        )

        # PDUs
        for j, pdu_off in enumerate([-80, -20, 40, 100]):
            pdu_x = cx + pdu_off
            msp.add_line((pdu_x, 470), (pdu_x, 420), dxfattribs={"color": GREEN, "lineweight": 18})
            dashed = j == 3
            pdu_label = f"PDU-{path}{j + 1}" if j < 3 else f"PDU-{path}n"
            add_equipment(msp, pdu_x - 20, 395, 40, 20, pdu_label, "", color=GREEN, dashed=dashed)

    # N+1 Generator
    add_generator_symbol(msp, 450, 700, 12, "GEN-C (N+1 SPARE)", "2000kVA DIESEL", color=WHITE)
    msp.add_line((438, 700), (340, 720), dxfattribs={"color": WHITE, "lineweight": 18, "linetype": "DASHED"})
    msp.add_line((462, 700), (560, 720), dxfattribs={"color": WHITE, "lineweight": 18, "linetype": "DASHED"})

    # IT Load zone
    msp.add_lwpolyline(
        [(60, 200), (840, 200), (840, 370), (60, 370), (60, 200)],
        dxfattribs={"color": WHITE, "lineweight": 25, "linetype": "DASHED"}
    )
    msp.add_text("IT EQUIPMENT — DUAL-CORDED SERVERS (FEED A + FEED B)",
                 dxfattribs={"height": 6, "color": WHITE, "style": "TITLE"}).set_placement(
        (450, 355), align=TextEntityAlignment.MIDDLE_CENTER
    )

    # Rack symbols
    for i, rx in enumerate(range(120, 800, 100)):
        label = f"RACK" if i < 6 else ""
        if label:
            msp.add_lwpolyline(
                [(rx, 250), (rx + 40, 250), (rx + 40, 280), (rx, 280), (rx, 250)],
                dxfattribs={"color": WHITE, "lineweight": 18}
            )
            msp.add_text("RACK", dxfattribs={"height": 3, "color": WHITE}).set_placement(
                (rx + 20, 265), align=TextEntityAlignment.MIDDLE_CENTER
            )

    msp.add_text("FEED A ←", dxfattribs={"height": 4, "color": GREEN}).set_placement((120, 235))
    msp.add_text("→ FEED B", dxfattribs={"height": 4, "color": GREEN}).set_placement((760, 235))

    # Notes
    notes_y = 180
    msp.add_text("GENERAL NOTES", dxfattribs={"height": 6, "color": WHITE, "style": "TITLE"}).set_placement(
        (450, notes_y), align=TextEntityAlignment.MIDDLE_CENTER
    )
    notes = [
        "1. ALL ELECTRICAL PER IEC 60364. SYMBOLS PER IEC 60617.",
        "2. SYSTEM: 20kV(MV)/415V(LV), 3φ+N+E, 50Hz.",
        "3. DUAL INDEPENDENT UTILITY FEEDS FROM SEPARATE PLN SUBSTATIONS.",
        "4. GENERATORS: 2N+1 (GEN-A PATH A, GEN-B PATH B, GEN-C SHARED N+1).",
        "5. UPS: N+1 PER PATH (3 MODULES: 2+1). BATTERY: 15 MIN RUNTIME.",
        "6. STS: <4ms TRANSFER. ATS: <10s TO GENERATOR.",
        "7. ALL IT EQUIPMENT DUAL-CORDED A+B FEEDS.",
        "8. MAINTENANCE BYPASS FOR CONCURRENT MAINTAINABILITY.",
        "9. TOTAL CRITICAL IT LOAD: 1.6MW (800kW/PATH). PUE TARGET ≤1.4.",
    ]
    for i, note in enumerate(notes):
        msp.add_text(note, dxfattribs={"height": 3, "color": WHITE}).set_placement(
            (60, notes_y - 12 - i * 8)
        )

    out = OUTPUT_DIR / "SAT-DC-EL-001_Electrical-SLD.dxf"
    doc.saveas(out)
    print(f"  {out}")


# ============================================================
# 3. NETWORK TOPOLOGY
# ============================================================
def generate_network():
    doc = setup_doc()
    msp = doc.modelspace()

    W, H = 1180, 840
    add_border(msp, W, H)
    add_title_block(msp, "SAT-DC-NT-001",
                    "NETWORK TOPOLOGY DIAGRAM",
                    "LOGICAL & PHYSICAL",
                    "TIA-942 / ISO/IEC 24764",
                    x_off=600, y_off=10)

    # Zone labels and separators
    zones = [
        (790, "WAN / CARRIER ZONE"),
        (650, "DMZ / PERIMETER ZONE"),
        (480, "CORE / DISTRIBUTION ZONE"),
        (310, "ACCESS / SERVER ZONE"),
    ]
    for zy, zl in zones:
        msp.add_text(zl, dxfattribs={"height": 5, "color": GRAY}).set_placement((20, zy))
        msp.add_line((20, zy - 5), (570, zy - 5),
                     dxfattribs={"color": GRAY, "linetype": "DASHED"})

    # Concurrent maintainability boundary
    msp.add_line((300, 200), (300, 810), dxfattribs={"color": RED, "linetype": "DASHDOT"})

    for path, cx in [("A", 160), ("B", 440)]:
        # ISP
        msp.add_circle((cx, 770), 25, dxfattribs={"color": BLUE})
        msp.add_text(f"ISP {path}", dxfattribs={"height": 5, "color": BLUE, "style": "TITLE"}).set_placement(
            (cx, 775), align=TextEntityAlignment.MIDDLE_CENTER
        )
        carrier = "PRIMARY" if path == "A" else "SECONDARY"
        msp.add_text(f"({carrier} CARRIER)", dxfattribs={"height": 3, "color": BLUE}).set_placement(
            (cx, 760), align=TextEntityAlignment.MIDDLE_CENTER
        )

        # MMR
        msp.add_line((cx, 745), (cx, 720), dxfattribs={"color": WHITE, "lineweight": 25})

    # MMR box spans both
    add_equipment(msp, 80, 710, 440, 25, "MEET-ME ROOM (MMR) — DIVERSE CARRIER ENTRIES", "", color=MAGENTA)

    for path, cx in [("A", 160), ("B", 440)]:
        y = 700
        # Border Router
        msp.add_line((cx, y), (cx, y - 30), dxfattribs={"color": WHITE, "lineweight": 25})
        add_equipment(msp, cx - 50, y - 65, 100, 35, f"BORDER ROUTER {path}", "BGP/OSPF 10GbE", color=YELLOW)

        # Firewall
        msp.add_line((cx, y - 65), (cx, y - 85), dxfattribs={"color": WHITE, "lineweight": 25})
        add_equipment(msp, cx - 50, y - 120, 100, 35, f"FIREWALL {path}",
                      "HA ACTIVE" if path == "A" else "HA STANDBY", color=RED)

        # FW HA heartbeat
        if path == "A":
            msp.add_line((210, y - 100), (390, y - 100),
                         dxfattribs={"color": RED, "linetype": "DASHED"})
            msp.add_text("HA HEARTBEAT", dxfattribs={"height": 3, "color": RED}).set_placement(
                (300, y - 96), align=TextEntityAlignment.MIDDLE_CENTER
            )

        # Core Switch
        msp.add_line((cx, y - 120), (cx, y - 150), dxfattribs={"color": WHITE, "lineweight": 25})
        add_equipment(msp, cx - 60, y - 195, 120, 45, f"CORE SWITCH {path}",
                      "L3 OSPF/BGP  40GbE", color=GREEN)

        # Core cross-connect
        if path == "A":
            msp.add_line((220, y - 170), (380, y - 170),
                         dxfattribs={"color": GREEN, "linetype": "DASHED", "lineweight": 25})
            msp.add_text("CROSS-CONNECT (40GbE)", dxfattribs={"height": 3, "color": GREEN}).set_placement(
                (300, y - 165), align=TextEntityAlignment.MIDDLE_CENTER
            )

        # Aggregation
        msp.add_line((cx, y - 195), (cx, y - 215), dxfattribs={"color": WHITE, "lineweight": 25})
        add_equipment(msp, cx - 55, y - 245, 110, 30, f"AGGREGATION {path}", "L2/L3 10GbE", color=BLUE)

        # ToR switches
        for j, tor_off in enumerate([-65, 0, 65]):
            tor_x = cx + tor_off
            msp.add_line((cx, y - 245), (tor_x, y - 270),
                         dxfattribs={"color": WHITE, "lineweight": 18})
            add_equipment(msp, tor_x - 25, y - 290, 50, 20, f"ToR-{path}{j + 1}", "", color=GRAY)

            # Server racks
            msp.add_line((tor_x, y - 290), (tor_x, y - 305),
                         dxfattribs={"color": WHITE, "lineweight": 13})
            row_label = chr(65 + (0 if path == "A" else 3) + j)
            msp.add_lwpolyline(
                [(tor_x - 25, y - 325), (tor_x + 25, y - 325),
                 (tor_x + 25, y - 305), (tor_x - 25, y - 305), (tor_x - 25, y - 325)],
                dxfattribs={"color": WHITE, "lineweight": 25}
            )
            msp.add_text(f"ROW {row_label}", dxfattribs={"height": 3, "color": WHITE}).set_placement(
                (tor_x, y - 315), align=TextEntityAlignment.MIDDLE_CENTER
            )

    # OOB Management
    add_equipment(msp, 250, 515, 100, 30, "OUT-OF-BAND MGMT", "IPMI/iLO/iDRAC", color=YELLOW, dashed=True)

    # Dual-home note
    msp.add_text("ALL SERVERS DUAL-HOMED (PATH A + PATH B)",
                 dxfattribs={"height": 4, "color": RED}).set_placement(
        (300, 365), align=TextEntityAlignment.MIDDLE_CENTER
    )

    # Legend
    lx, ly = 620, 810
    msp.add_text("LEGEND (PER TIA-942)", dxfattribs={"height": 5, "color": WHITE, "style": "TITLE"}).set_placement(
        (lx, ly)
    )
    legend = [
        (BLUE, "ISP / WAN Cloud"), (MAGENTA, "Meet-Me Room"),
        (YELLOW, "Border Router"), (RED, "Firewall (HA Pair)"),
        (GREEN, "Core Switch (L3)"), (BLUE, "Aggregation Switch"),
        (GRAY, "ToR Access Switch"), (WHITE, "Server Rack Row"),
    ]
    for i, (c, t) in enumerate(legend):
        y = ly - 12 - i * 10
        msp.add_lwpolyline(
            [(lx, y), (lx + 8, y), (lx + 8, y + 5), (lx, y + 5), (lx, y)],
            dxfattribs={"color": c}
        )
        msp.add_text(t, dxfattribs={"height": 3.5, "color": WHITE}).set_placement((lx + 12, y + 2.5))

    out = OUTPUT_DIR / "SAT-DC-NT-001_Network-Topology.dxf"
    doc.saveas(out)
    print(f"  {out}")


# ============================================================
# 4. COOLING SYSTEM
# ============================================================
def generate_cooling():
    doc = setup_doc()
    msp = doc.modelspace()

    W, H = 1180, 840
    add_border(msp, W, H)
    add_title_block(msp, "SAT-DC-CL-001",
                    "HVAC & COOLING SYSTEM DIAGRAM",
                    "CHILLED WATER DISTRIBUTION",
                    "ASHRAE TC 9.9",
                    x_off=600, y_off=10)

    # Outdoor section
    msp.add_lwpolyline(
        [(30, 600), (560, 600), (560, 810), (30, 810), (30, 600)],
        dxfattribs={"color": GRAY, "lineweight": 25, "linetype": "DASHED"}
    )
    msp.add_text("OUTDOOR — COOLING YARD", dxfattribs={"height": 5, "color": GRAY}).set_placement((35, 800))

    # Cooling Towers
    for i, (label, x) in enumerate([("CT-A", 50), ("CT-B", 160), ("CT-C (N+1)", 270)]):
        dashed = i == 2
        add_equipment(msp, x, 730, 90, 50, label, "INDUCED DRAFT\nCOUNTERFLOW", color=CYAN, dashed=dashed)

    # Chillers
    for i, (label, x) in enumerate([("CHILLER A", 380), ("CHILLER B", 380), ("CHILLER C (N+1)", 380)]):
        y = 730 - i * 60
        dashed = i == 2
        lbl = f"CHILLER {'ABC'[i]}" + (" (N+1)" if i == 2 else "")
        add_equipment(msp, 400, y, 130, 45, lbl, "WATER-COOLED 500kW", color=GREEN, dashed=dashed)

    # Condenser water arrows
    msp.add_text("CONDENSER WATER LOOP →", dxfattribs={"height": 3.5, "color": CYAN}).set_placement((300, 760))
    msp.add_line((360, 755), (400, 755), dxfattribs={"color": CYAN, "lineweight": 25})

    # Primary CHW bus
    msp.add_text("INDOOR — MECHANICAL ROOM", dxfattribs={"height": 5, "color": GRAY}).set_placement((35, 575))
    add_bus_bar(msp, 30, 540, 540, "PRIMARY CHILLED WATER SUPPLY — 7°C / 12°C (SUPPLY/RETURN)", color=CYAN)

    # Primary pumps
    for i, (label, x) in enumerate([("PP-A", 80), ("PP-B", 160), ("PP-C (N+1)", 240)]):
        dashed = i == 2
        add_equipment(msp, x, 545, 60, 22, label, "", color=CYAN, dashed=dashed)
    msp.add_text("PRIMARY CHW PUMPS", dxfattribs={"height": 3, "color": CYAN}).set_placement((80, 570))

    # Secondary CHW bus
    add_bus_bar(msp, 30, 460, 540, "SECONDARY CHW DISTRIBUTION — TO CRAH UNITS", color=GREEN)

    # Secondary pumps
    for i, (label, x) in enumerate([("SP-A", 340), ("SP-B", 420), ("SP-C (N+1)", 500)]):
        dashed = i == 2
        add_equipment(msp, x, 465, 60, 22, label, "", color=GREEN, dashed=dashed)

    # Connection primary to secondary
    msp.add_line((300, 540), (300, 460), dxfattribs={"color": WHITE, "lineweight": 25})

    # CRAH Units
    msp.add_text("DATA HALL — HOT/COLD AISLE CONTAINMENT", dxfattribs={"height": 5, "color": GRAY}).set_placement(
        (35, 420)
    )
    for i, x in enumerate([50, 180, 310, 440]):
        dashed = i == 3
        label = f"CRAH-{i + 1}" + (" (N+1)" if dashed else "")
        add_equipment(msp, x, 350, 110, 55, label, "DOWNFLOW\n150kW COOLING", color=RED, dashed=dashed)
        msp.add_line((x + 55, 460), (x + 55, 405), dxfattribs={"color": GREEN, "lineweight": 18})

    # Airflow pattern
    msp.add_lwpolyline(
        [(30, 200), (570, 200), (570, 340), (30, 340), (30, 200)],
        dxfattribs={"color": GRAY, "lineweight": 18}
    )
    msp.add_text("AIRFLOW PATTERN — HOT/COLD AISLE CONTAINMENT",
                 dxfattribs={"height": 5, "color": WHITE, "style": "TITLE"}).set_placement(
        (300, 330), align=TextEntityAlignment.MIDDLE_CENTER
    )
    msp.add_text("COLD AISLE — SUPPLY AIR 18-22°C (ASHRAE A1)",
                 dxfattribs={"height": 3.5, "color": BLUE}).set_placement(
        (300, 310), align=TextEntityAlignment.MIDDLE_CENTER
    )
    msp.add_text("↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓",
                 dxfattribs={"height": 4, "color": BLUE}).set_placement(
        (300, 298), align=TextEntityAlignment.MIDDLE_CENTER
    )
    msp.add_lwpolyline(
        [(50, 275), (550, 275), (550, 290), (50, 290), (50, 275)],
        dxfattribs={"color": WHITE, "lineweight": 35}
    )
    msp.add_text("ROW A  |  ROW B  (SERVER RACKS)", dxfattribs={"height": 3, "color": WHITE}).set_placement(
        (300, 282), align=TextEntityAlignment.MIDDLE_CENTER
    )
    msp.add_text("HOT AISLE (CONTAINED) — EXHAUST 35-40°C → RETURN TO CRAH",
                 dxfattribs={"height": 3.5, "color": RED}).set_placement(
        (300, 265), align=TextEntityAlignment.MIDDLE_CENTER
    )
    msp.add_text("↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑",
                 dxfattribs={"height": 4, "color": RED}).set_placement(
        (300, 253), align=TextEntityAlignment.MIDDLE_CENTER
    )
    msp.add_lwpolyline(
        [(50, 233), (550, 233), (550, 248), (50, 248), (50, 233)],
        dxfattribs={"color": WHITE, "lineweight": 35}
    )
    msp.add_text("ROW C  |  ROW D  (SERVER RACKS)", dxfattribs={"height": 3, "color": WHITE}).set_placement(
        (300, 240), align=TextEntityAlignment.MIDDLE_CENTER
    )
    msp.add_text("COLD AISLE (RAISED FLOOR PLENUM SUPPLY)",
                 dxfattribs={"height": 3.5, "color": BLUE}).set_placement(
        (300, 220), align=TextEntityAlignment.MIDDLE_CENTER
    )

    # Environmental monitoring
    add_equipment(msp, 600, 350, 160, 55, "ENVIRONMENTAL MONITORING",
                  "TEMP/HUMIDITY/LEAK DETECT\n→ ALERTS TO BMS/DCIM", color=MAGENTA)

    # Legend
    lx, ly = 620, 810
    msp.add_text("LEGEND (PER ASHRAE TC 9.9)", dxfattribs={"height": 5, "color": WHITE, "style": "TITLE"}).set_placement(
        (lx, ly)
    )
    legend = [
        (CYAN, "Cooling Tower / Primary Pipe"),
        (GREEN, "Chiller / Secondary Pipe"),
        (RED, "CRAH Unit / Hot Return"),
        (BLUE, "Cold Aisle Supply"),
        (MAGENTA, "Environmental Monitoring"),
    ]
    for i, (c, t) in enumerate(legend):
        y = ly - 12 - i * 10
        msp.add_lwpolyline(
            [(lx, y), (lx + 8, y), (lx + 8, y + 5), (lx, y + 5), (lx, y)],
            dxfattribs={"color": c}
        )
        msp.add_text(t, dxfattribs={"height": 3.5, "color": WHITE}).set_placement((lx + 12, y + 2.5))

    out = OUTPUT_DIR / "SAT-DC-CL-001_Cooling-System.dxf"
    doc.saveas(out)
    print(f"  {out}")


# ============================================================
# 5. FIRE SUPPRESSION
# ============================================================
def generate_fire():
    doc = setup_doc()
    msp = doc.modelspace()

    W, H = 1180, 840
    add_border(msp, W, H)
    add_title_block(msp, "SAT-DC-FS-001",
                    "FIRE DETECTION & SUPPRESSION",
                    "ZONE MAP & SCHEMATIC",
                    "NFPA 75 / NFPA 2001",
                    x_off=600, y_off=10)

    # FACP
    add_equipment(msp, 150, 720, 300, 60, "FIRE ALARM CONTROL PANEL (FACP)",
                  "REDUNDANT | ADDRESSABLE | SIL 2 | 72HR BATTERY", color=RED)

    # VESDA Zones
    msp.add_text("VERY EARLY SMOKE DETECTION — VESDA ASPIRATING SYSTEM",
                 dxfattribs={"height": 5, "color": GRAY}).set_placement((35, 690))

    vesda_zones = [
        ("VZ-1", "DATA HALL", "ABOVE & BELOW FLOOR\n4-STAGE ALARM"),
        ("VZ-2", "UPS ROOMS", "BATTERY MONITORING\nH2 GAS DETECTION"),
        ("VZ-3", "ELECTRICAL", "MV/LV SWITCHGEAR\nARC FLASH DETECTION"),
        ("VZ-4", "NOC / MMR", "FIRE CONTROL ROOM"),
    ]
    for i, (tag, label, detail) in enumerate(vesda_zones):
        x = 30 + i * 145
        add_equipment(msp, x, 620, 130, 55, f"VESDA ZONE {i + 1}", f"{label}\n{detail}", color=YELLOW)
        msp.add_text(tag, dxfattribs={"height": 3, "color": YELLOW}).set_placement((x + 115, 665))
        # Line to FACP
        msp.add_line((x + 65, 675), (300, 720), dxfattribs={"color": RED, "lineweight": 18})

    # Suppression systems
    msp.add_text("FIRE SUPPRESSION SYSTEMS", dxfattribs={"height": 5, "color": GRAY}).set_placement((35, 590))

    add_equipment(msp, 30, 500, 250, 75, "CLEAN AGENT SUPPRESSION",
                  "NOVEC 1230 / FM-200\nDATA HALL, UPS, ELECTRICAL\n≤10s DISCHARGE (NFPA 2001)", color=GREEN)
    add_equipment(msp, 320, 500, 250, 75, "PRE-ACTION SPRINKLER",
                  "DOUBLE-INTERLOCK (NFPA 13)\nNOC, MMR, STAGING, CORRIDORS\nDRY PIPE UNTIL DUAL TRIGGER", color=BLUE)

    # FACP to suppression
    msp.add_line((200, 720), (155, 575), dxfattribs={"color": RED, "lineweight": 25})
    msp.add_line((400, 720), (445, 575), dxfattribs={"color": RED, "lineweight": 25})

    # Integration systems
    msp.add_text("SYSTEM INTEGRATIONS", dxfattribs={"height": 5, "color": GRAY}).set_placement((35, 475))

    add_equipment(msp, 30, 400, 170, 60, "EMERGENCY POWER OFF",
                  "EPO VIA FACP\nFIRE2 ALARM LEVEL\nEPO BUTTONS AT EXITS", color=MAGENTA)
    add_equipment(msp, 220, 400, 170, 60, "BUILDING MANAGEMENT",
                  "BMS MODBUS/BACnet\nHVAC SHUTDOWN\nSMOKE DAMPER CONTROL", color=WHITE)
    add_equipment(msp, 410, 400, 170, 60, "NOTIFICATION",
                  "AUDIBLE/VISUAL ALARMS\nFIRE DEPT AUTO-DIAL\nSMS/EMAIL ESCALATION", color=YELLOW)

    # Lines from FACP to integrations
    msp.add_line((200, 720), (115, 460), dxfattribs={"color": MAGENTA, "lineweight": 18})
    msp.add_line((300, 720), (305, 460), dxfattribs={"color": WHITE, "lineweight": 18})
    msp.add_line((400, 720), (495, 460), dxfattribs={"color": YELLOW, "lineweight": 18})

    # Sequence of operations
    msp.add_lwpolyline(
        [(30, 220), (570, 220), (570, 370), (30, 370), (30, 220)],
        dxfattribs={"color": RED, "lineweight": 25}
    )
    msp.add_text("SEQUENCE OF OPERATIONS — FIRE EVENT RESPONSE",
                 dxfattribs={"height": 5, "color": RED, "style": "TITLE"}).set_placement(
        (300, 360), align=TextEntityAlignment.MIDDLE_CENTER
    )

    steps = [
        ("1. ALERT", "VESDA THRESHOLD", YELLOW),
        ("2. ACTION", "NOC NOTIFIED", YELLOW),
        ("3. FIRE 1", "AUDIBLE ALARM\nHVAC SHUTDOWN", RED),
        ("4. FIRE 2", "FIRE DEPT CALLED\n30s COUNTDOWN", RED),
        ("5. SUPPRESS", "CLEAN AGENT\nDISCHARGE", GREEN),
        ("6. EPO", "EMERGENCY\nPOWER OFF", MAGENTA),
        ("7. RESPONSE", "FIRE DEPT\nON-SITE", BLUE),
    ]
    for i, (step, detail, color) in enumerate(steps):
        sx = 50 + i * 72
        add_equipment(msp, sx, 280, 60, 35, step, detail, color=color)
        if i < len(steps) - 1:
            msp.add_text("→", dxfattribs={"height": 8, "color": RED}).set_placement(
                (sx + 65, 297), align=TextEntityAlignment.MIDDLE_CENTER
            )

    msp.add_text("NOTE: ABORT BUTTON AVAILABLE AT EACH STEP. NOC OPERATOR CAN HOLD DISCHARGE.",
                 dxfattribs={"height": 3.5, "color": RED}).set_placement(
        (300, 235), align=TextEntityAlignment.MIDDLE_CENTER
    )

    # Legend
    lx, ly = 620, 810
    msp.add_text("LEGEND (PER NFPA 75/2001)", dxfattribs={"height": 5, "color": WHITE, "style": "TITLE"}).set_placement(
        (lx, ly)
    )
    legend = [
        (RED, "FACP / Signal Line"),
        (YELLOW, "VESDA Detection Zone"),
        (GREEN, "Clean Agent Suppression"),
        (BLUE, "Pre-Action Sprinkler"),
        (MAGENTA, "Emergency Power Off (EPO)"),
        (WHITE, "BMS Integration"),
    ]
    for i, (c, t) in enumerate(legend):
        y = ly - 12 - i * 10
        msp.add_lwpolyline(
            [(lx, y), (lx + 8, y), (lx + 8, y + 5), (lx, y + 5), (lx, y)],
            dxfattribs={"color": c}
        )
        msp.add_text(t, dxfattribs={"height": 3.5, "color": WHITE}).set_placement((lx + 12, y + 2.5))

    # Standards
    msp.add_text("APPLICABLE STANDARDS:", dxfattribs={"height": 4, "color": WHITE, "style": "TITLE"}).set_placement(
        (lx, ly - 85)
    )
    stds = [
        "NFPA 75  — IT Equipment Protection",
        "NFPA 2001 — Clean Agent Systems",
        "NFPA 13  — Sprinkler Systems",
        "NFPA 72  — Fire Alarm & Signaling",
    ]
    for i, s in enumerate(stds):
        msp.add_text(s, dxfattribs={"height": 3, "color": WHITE}).set_placement(
            (lx, ly - 97 - i * 8)
        )

    out = OUTPUT_DIR / "SAT-DC-FS-001_Fire-Suppression.dxf"
    doc.saveas(out)
    print(f"  {out}")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=== Satsiber DC — Generating DXF Drawings ===\n")

    print("[1/5] Floor Plan...")
    generate_floor_plan()

    print("[2/5] Electrical Single Line Diagram...")
    generate_electrical()

    print("[3/5] Network Topology...")
    generate_network()

    print("[4/5] Cooling System...")
    generate_cooling()

    print("[5/5] Fire Suppression...")
    generate_fire()

    print(f"\nDone! All DXF files saved to: {OUTPUT_DIR}/")
    print("Open with AutoCAD, BricsCAD, LibreCAD, or any DXF-compatible CAD software.")
