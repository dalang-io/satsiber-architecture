#!/usr/bin/env python3
"""
Satsiber Data Center — Tier III Design Certification Drawings
Generates professional A4 landscape PDF technical drawings using reportlab.

Drawings:
  1. DC Floor Plan (16 racks, hot/cold aisle)
  2. Electrical Single Line Diagram (dual feed, N+1)
  3. Network Topology (redundant core, dual ISP)
  4. Cooling System (N+1 chillers, CRAHs)
  5. Fire Suppression (VESDA, clean agent, pre-action)

Standards: IEC 60617, TIA-942, ASHRAE TC 9.9, NFPA 75/2001
Run: uv run generate_pdf.py
"""

import os
import math
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import (
    HexColor, black, white, red, blue, green, gray,
    darkgray, lightgrey, orange, Color
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Page setup
PAGE_W, PAGE_H = landscape(A4)  # 297mm x 210mm
MARGIN = 10 * mm
BORDER = MARGIN + 2 * mm

# Colors
C_BORDER = HexColor("#1a1a2e")
C_TITLE_BG = HexColor("#16213e")
C_TITLE_TEXT = HexColor("#e2e2e2")
C_GRID = HexColor("#cccccc")
C_WALL = HexColor("#2c3e50")
C_WALL_FILL = HexColor("#ecf0f1")
C_RACK = HexColor("#2c3e50")
C_RACK_FILL = HexColor("#34495e")
C_HOT = HexColor("#e74c3c")
C_COLD = HexColor("#3498db")
C_ELEC_A = HexColor("#e74c3c")
C_ELEC_B = HexColor("#2980b9")
C_MECH = HexColor("#27ae60")
C_GEN = HexColor("#f39c12")
C_UPS = HexColor("#8e44ad")
C_FIRE = HexColor("#c0392b")
C_NET_CORE = HexColor("#2c3e50")
C_NET_AGG = HexColor("#2980b9")
C_NET_ACC = HexColor("#27ae60")
C_COOL_SUPPLY = HexColor("#3498db")
C_COOL_RETURN = HexColor("#e74c3c")
C_LIGHT_BLUE = HexColor("#d6eaf8")
C_LIGHT_RED = HexColor("#fadbd8")
C_LIGHT_GREEN = HexColor("#d5f5e3")
C_LIGHT_YELLOW = HexColor("#fef9e7")
C_LIGHT_PURPLE = HexColor("#e8daef")
C_DASHED = HexColor("#7f8c8d")

# Drawing area
DRW_LEFT = BORDER + 2 * mm
DRW_BOTTOM = BORDER + 40 * mm  # space for title block
DRW_RIGHT = PAGE_W - BORDER - 2 * mm
DRW_TOP = PAGE_H - BORDER - 2 * mm
DRW_W = DRW_RIGHT - DRW_LEFT
DRW_H = DRW_TOP - DRW_BOTTOM


def draw_border(c):
    """Double-line border with margin."""
    c.setStrokeColor(C_BORDER)
    c.setLineWidth(0.5)
    c.rect(MARGIN, MARGIN, PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN)
    c.setLineWidth(1.5)
    c.rect(BORDER, BORDER, PAGE_W - 2 * BORDER, PAGE_H - 2 * BORDER)


def draw_title_block(c, dwg_no, title, subtitle, standard, rev="A", scale="NTS"):
    """Standard title block at bottom of drawing."""
    tb_x = BORDER
    tb_y = BORDER
    tb_w = PAGE_W - 2 * BORDER
    tb_h = 36 * mm

    # Background
    c.setFillColor(C_TITLE_BG)
    c.rect(tb_x, tb_y, tb_w, tb_h, fill=1, stroke=0)

    # Dividers
    c.setStrokeColor(C_TITLE_TEXT)
    c.setLineWidth(0.5)
    # Horizontal divider
    c.line(tb_x, tb_y + 12 * mm, tb_x + tb_w, tb_y + 12 * mm)
    c.line(tb_x, tb_y + 24 * mm, tb_x + tb_w, tb_y + 24 * mm)
    # Vertical dividers
    c.line(tb_x + 80 * mm, tb_y, tb_x + 80 * mm, tb_y + 24 * mm)
    c.line(tb_x + 160 * mm, tb_y, tb_x + 160 * mm, tb_y + 24 * mm)
    c.line(tb_x + 200 * mm, tb_y, tb_x + 200 * mm, tb_y + 12 * mm)

    # Top row — Title
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(tb_x + 6 * mm, tb_y + 27 * mm, f"SATSIBER DATA CENTER — {title}")
    c.setFont("Helvetica", 8)
    c.drawRightString(tb_x + tb_w - 4 * mm, tb_y + 27 * mm, f"UPTIME TIER III DESIGN")

    # Middle row
    c.setFont("Helvetica", 7)
    c.setFillColor(HexColor("#aaaaaa"))
    c.drawString(tb_x + 4 * mm, tb_y + 19 * mm, "PROJECT")
    c.drawString(tb_x + 84 * mm, tb_y + 19 * mm, "SUBTITLE")
    c.drawString(tb_x + 164 * mm, tb_y + 19 * mm, "CLASSIFICATION")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(tb_x + 4 * mm, tb_y + 14 * mm, "Satsiber New Data Center")
    c.drawString(tb_x + 84 * mm, tb_y + 14 * mm, subtitle)
    c.drawString(tb_x + 164 * mm, tb_y + 14 * mm, "CONFIDENTIAL")

    # Bottom row
    c.setFont("Helvetica", 7)
    c.setFillColor(HexColor("#aaaaaa"))
    c.drawString(tb_x + 4 * mm, tb_y + 7 * mm, "DWG NO.")
    c.drawString(tb_x + 84 * mm, tb_y + 7 * mm, "STANDARD")
    c.drawString(tb_x + 164 * mm, tb_y + 7 * mm, "SCALE")
    c.drawString(tb_x + 204 * mm, tb_y + 7 * mm, "REV")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(tb_x + 4 * mm, tb_y + 2 * mm, dwg_no)
    c.setFont("Helvetica", 9)
    c.drawString(tb_x + 84 * mm, tb_y + 2 * mm, standard)
    c.drawString(tb_x + 164 * mm, tb_y + 2 * mm, scale)
    c.drawString(tb_x + 204 * mm, tb_y + 2 * mm, rev)

    # Date
    c.setFont("Helvetica", 7)
    c.setFillColor(HexColor("#aaaaaa"))
    c.drawString(tb_x + 230 * mm, tb_y + 7 * mm, "DATE")
    c.setFillColor(white)
    c.setFont("Helvetica", 9)
    c.drawString(tb_x + 230 * mm, tb_y + 2 * mm, "2026-02-27")


def draw_grid_refs(c):
    """Grid reference letters/numbers along edges."""
    c.setFont("Helvetica", 6)
    c.setFillColor(C_GRID)
    cols = "ABCDEFGHJK"
    for i, ch in enumerate(cols):
        x = DRW_LEFT + (i + 0.5) * DRW_W / len(cols)
        c.drawCentredString(x, DRW_TOP + 2 * mm, ch)
        c.drawCentredString(x, DRW_BOTTOM - 6 * mm, ch)
    rows = "12345678"
    for i, ch in enumerate(rows):
        y = DRW_BOTTOM + (i + 0.5) * DRW_H / len(rows)
        c.drawCentredString(DRW_LEFT - 5 * mm, y - 2, ch)
        c.drawCentredString(DRW_RIGHT + 5 * mm, y - 2, ch)


def draw_room(c, x, y, w, h, label, ref_id=None, fill=C_WALL_FILL, text_color=C_WALL):
    """Draw a room rectangle with label."""
    c.setFillColor(fill)
    c.setStrokeColor(C_WALL)
    c.setLineWidth(1.2)
    c.rect(x, y, w, h, fill=1, stroke=1)
    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(x + w / 2, y + h / 2 + 2, label)
    if ref_id:
        c.setFont("Helvetica", 5.5)
        c.setFillColor(HexColor("#666666"))
        c.drawCentredString(x + w / 2, y + h / 2 - 6, ref_id)


def draw_rack(c, x, y, w, h, label, fill=C_RACK_FILL):
    """Draw a server rack."""
    c.setFillColor(fill)
    c.setStrokeColor(C_RACK)
    c.setLineWidth(0.8)
    c.rect(x, y, w, h, fill=1, stroke=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 4.5)
    c.drawCentredString(x + w / 2, y + h / 2 - 1.5, label)


def draw_arrow(c, x1, y1, x2, y2, color=black, width=0.8):
    """Draw an arrow from (x1,y1) to (x2,y2)."""
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)
    # Arrowhead
    angle = math.atan2(y2 - y1, x2 - x1)
    alen = 3 * mm
    p = c.beginPath()
    p.moveTo(x2, y2)
    p.lineTo(x2 - alen * math.cos(angle - 0.3), y2 - alen * math.sin(angle - 0.3))
    p.lineTo(x2 - alen * math.cos(angle + 0.3), y2 - alen * math.sin(angle + 0.3))
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def draw_dashed_rect(c, x, y, w, h, color=C_DASHED, width=0.6):
    """Draw a dashed rectangle."""
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.setDash(3, 2)
    c.rect(x, y, w, h, fill=0, stroke=1)
    c.setDash()


def draw_legend_item(c, x, y, color, label, shape="rect"):
    """Draw a single legend entry."""
    if shape == "rect":
        c.setFillColor(color)
        c.setStrokeColor(black)
        c.setLineWidth(0.4)
        c.rect(x, y, 4 * mm, 3 * mm, fill=1, stroke=1)
    elif shape == "line":
        c.setStrokeColor(color)
        c.setLineWidth(1.5)
        c.line(x, y + 1.5 * mm, x + 4 * mm, y + 1.5 * mm)
    elif shape == "dash":
        c.setStrokeColor(color)
        c.setLineWidth(1)
        c.setDash(2, 1.5)
        c.line(x, y + 1.5 * mm, x + 4 * mm, y + 1.5 * mm)
        c.setDash()
    elif shape == "circle":
        c.setFillColor(color)
        c.setStrokeColor(black)
        c.setLineWidth(0.4)
        c.circle(x + 2 * mm, y + 1.5 * mm, 1.5 * mm, fill=1, stroke=1)
    c.setFillColor(black)
    c.setFont("Helvetica", 5.5)
    c.drawString(x + 6 * mm, y + 0.5 * mm, label)


def draw_north_arrow(c, x, y):
    """Draw a north arrow symbol."""
    c.setStrokeColor(black)
    c.setFillColor(black)
    c.setLineWidth(0.8)
    p = c.beginPath()
    p.moveTo(x, y)
    p.lineTo(x - 2 * mm, y - 6 * mm)
    p.lineTo(x, y - 4.5 * mm)
    p.lineTo(x + 2 * mm, y - 6 * mm)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(x, y + 2 * mm, "N")


# ═══════════════════════════════════════════════════════════
#  DRAWING 1: FLOOR PLAN
# ═══════════════════════════════════════════════════════════
def draw_floor_plan(c):
    draw_border(c)
    draw_title_block(c, "SAT-DC-FP-001", "DATA CENTER FLOOR PLAN",
                     "16-Rack Layout — Hot/Cold Aisle", "ISO/IEC 22237 / TIA-942")
    draw_grid_refs(c)

    ox = DRW_LEFT + 8 * mm
    oy = DRW_BOTTOM + 8 * mm
    bw = 230 * mm
    bh = DRW_H - 16 * mm

    # Building envelope
    c.setStrokeColor(C_WALL)
    c.setLineWidth(2.5)
    c.setFillColor(white)
    c.rect(ox, oy, bw, bh, fill=1, stroke=1)

    # ── DATA HALL ──
    dh_x = ox + 58 * mm
    dh_y = oy + 5 * mm
    dh_w = 130 * mm
    dh_h = bh - 10 * mm
    c.setFillColor(C_LIGHT_BLUE)
    c.setStrokeColor(C_WALL)
    c.setLineWidth(1.5)
    c.rect(dh_x, dh_y, dh_w, dh_h, fill=1, stroke=1)
    c.setFillColor(C_WALL)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(dh_x + dh_w / 2, dh_y + dh_h - 7 * mm, "DATA HALL")
    c.setFont("Helvetica", 6)
    c.drawCentredString(dh_x + dh_w / 2, dh_y + dh_h - 12 * mm, "R-01  |  ~120 m²  |  Raised Floor 600mm")

    # Cold aisle containment zones (2 cold aisles)
    ca_w = 18 * mm
    # Row positions: 2 rows of 8 racks per cold aisle
    row_start_y = dh_y + 10 * mm
    rack_w = 7 * mm
    rack_h = 11 * mm
    rack_gap = 2 * mm
    row_gap = 4 * mm

    # Aisle 1 — racks A01-A08 and B01-B08
    a1_x = dh_x + 12 * mm
    # Row A (left side of cold aisle 1)
    for i in range(8):
        ry = row_start_y + i * (rack_h + rack_gap)
        draw_rack(c, a1_x, ry, rack_w, rack_h, f"A{i+1:02d}")

    # Cold aisle 1
    ca1_x = a1_x + rack_w + 1 * mm
    c.setFillColor(HexColor("#d6eaf844"))
    c.setStrokeColor(C_COLD)
    c.setLineWidth(0.6)
    c.setDash(2, 1)
    c.rect(ca1_x, row_start_y - 1 * mm, ca_w, 8 * (rack_h + rack_gap) - rack_gap + 2 * mm, fill=0, stroke=1)
    c.setDash()
    c.saveState()
    c.setFillColor(C_COLD)
    c.setFont("Helvetica", 5)
    c.translate(ca1_x + ca_w / 2, row_start_y + 30 * mm)
    c.rotate(90)
    c.drawCentredString(0, 0, "COLD AISLE 1")
    c.restoreState()

    # Row B (right side of cold aisle 1)
    b1_x = ca1_x + ca_w + 1 * mm
    for i in range(8):
        ry = row_start_y + i * (rack_h + rack_gap)
        draw_rack(c, b1_x, ry, rack_w, rack_h, f"B{i+1:02d}")

    # Hot aisle between aisle groups
    hot_x = b1_x + rack_w + 2 * mm
    c.setStrokeColor(C_HOT)
    c.setLineWidth(0.6)
    c.setDash(2, 1)
    c.rect(hot_x, row_start_y - 1 * mm, 14 * mm, 8 * (rack_h + rack_gap) - rack_gap + 2 * mm, fill=0, stroke=1)
    c.setDash()
    c.saveState()
    c.setFillColor(C_HOT)
    c.setFont("Helvetica", 5)
    c.translate(hot_x + 7 * mm, row_start_y + 30 * mm)
    c.rotate(90)
    c.drawCentredString(0, 0, "HOT AISLE")
    c.restoreState()

    # Aisle 2 — racks C01-C08 and D01-D08
    a2_x = hot_x + 14 * mm + 2 * mm
    for i in range(8):
        ry = row_start_y + i * (rack_h + rack_gap)
        draw_rack(c, a2_x, ry, rack_w, rack_h, f"C{i+1:02d}")

    ca2_x = a2_x + rack_w + 1 * mm
    c.setStrokeColor(C_COLD)
    c.setLineWidth(0.6)
    c.setDash(2, 1)
    c.rect(ca2_x, row_start_y - 1 * mm, ca_w, 8 * (rack_h + rack_gap) - rack_gap + 2 * mm, fill=0, stroke=1)
    c.setDash()
    c.saveState()
    c.setFillColor(C_COLD)
    c.setFont("Helvetica", 5)
    c.translate(ca2_x + ca_w / 2, row_start_y + 30 * mm)
    c.rotate(90)
    c.drawCentredString(0, 0, "COLD AISLE 2")
    c.restoreState()

    d1_x = ca2_x + ca_w + 1 * mm
    for i in range(8):
        ry = row_start_y + i * (rack_h + rack_gap)
        draw_rack(c, d1_x, ry, rack_w, rack_h, f"D{i+1:02d}")

    # ── SUPPORT ROOMS (left side) ──
    sr_x = ox + 2 * mm
    sr_w = 54 * mm

    # Electrical Room
    draw_room(c, sr_x, oy + bh - 30 * mm, sr_w, 28 * mm,
              "ELECTRICAL ROOM", "R-02", C_LIGHT_YELLOW)
    c.setFont("Helvetica", 4.5)
    c.setFillColor(HexColor("#666666"))
    c.drawCentredString(sr_x + sr_w / 2, oy + bh - 18 * mm, "MV/LV Switchgear")
    c.drawCentredString(sr_x + sr_w / 2, oy + bh - 22 * mm, "ATS / Transformers")

    # UPS Room A
    draw_room(c, sr_x, oy + bh - 57 * mm, sr_w / 2 - 1, 24 * mm,
              "UPS-A", "R-03", C_LIGHT_PURPLE)
    # UPS Room B
    draw_room(c, sr_x + sr_w / 2 + 1, oy + bh - 57 * mm, sr_w / 2 - 1, 24 * mm,
              "UPS-B", "R-04", C_LIGHT_PURPLE)

    # Battery Room A
    draw_room(c, sr_x, oy + bh - 78 * mm, sr_w / 2 - 1, 18 * mm,
              "BATT-A", "R-05", HexColor("#fdebd0"))
    # Battery Room B
    draw_room(c, sr_x + sr_w / 2 + 1, oy + bh - 78 * mm, sr_w / 2 - 1, 18 * mm,
              "BATT-B", "R-06", HexColor("#fdebd0"))

    # NOC
    draw_room(c, sr_x, oy + bh - 100 * mm, sr_w, 19 * mm,
              "NOC / OPERATIONS", "R-07", C_LIGHT_GREEN)

    # MMR
    draw_room(c, sr_x, oy + 2 * mm, sr_w, 18 * mm,
              "MEET-ME ROOM (MMR)", "R-08", HexColor("#d5dbdb"))
    c.setFont("Helvetica", 4.5)
    c.setFillColor(HexColor("#666666"))
    c.drawCentredString(sr_x + sr_w / 2, oy + 8 * mm, "Carrier Entries (Diverse)")

    # Staging
    draw_room(c, sr_x, oy + 23 * mm, sr_w, 14 * mm,
              "STAGING / LOADING", "R-09", HexColor("#f2f3f4"))

    # ── SUPPORT ROOMS (right side) ──
    rr_x = ox + bw - 40 * mm
    rr_w = 38 * mm

    # Cooling Plant
    draw_room(c, rr_x, oy + bh - 40 * mm, rr_w, 38 * mm,
              "COOLING PLANT", "R-10", C_LIGHT_BLUE)
    c.setFont("Helvetica", 4.5)
    c.setFillColor(HexColor("#666666"))
    c.drawCentredString(rr_x + rr_w / 2, oy + bh - 20 * mm, "Chillers (N+1)")
    c.drawCentredString(rr_x + rr_w / 2, oy + bh - 24 * mm, "Pumps / Piping")

    # Fire Control
    draw_room(c, rr_x, oy + bh - 62 * mm, rr_w, 19 * mm,
              "FIRE CONTROL", "R-11", C_LIGHT_RED)
    c.setFont("Helvetica", 4.5)
    c.setFillColor(HexColor("#666666"))
    c.drawCentredString(rr_x + rr_w / 2, oy + bh - 50 * mm, "FACP / Agent Storage")

    # Security / Access
    draw_room(c, rr_x, oy + 2 * mm, rr_w, 16 * mm,
              "SECURITY / ACCESS", "R-12", HexColor("#d5dbdb"))

    # Generator Yard (outside building, bottom right)
    gy_x = ox + bw + 4 * mm
    gy_y = oy
    gy_w = 28 * mm
    gy_h = 50 * mm
    c.setStrokeColor(C_GEN)
    c.setFillColor(C_LIGHT_YELLOW)
    c.setLineWidth(1.5)
    c.setDash(4, 2)
    c.rect(gy_x, gy_y, gy_w, gy_h, fill=1, stroke=1)
    c.setDash()
    c.setFillColor(C_GEN)
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(gy_x + gy_w / 2, gy_y + gy_h - 6 * mm, "GENERATOR")
    c.drawCentredString(gy_x + gy_w / 2, gy_y + gy_h - 10 * mm, "YARD")
    c.setFont("Helvetica", 5)
    c.drawCentredString(gy_x + gy_w / 2, gy_y + gy_h - 15 * mm, "R-13")
    # 3 generators
    for i in range(3):
        gx = gy_x + 4 * mm
        gy = gy_y + 4 * mm + i * 13 * mm
        c.setFillColor(C_GEN)
        c.setStrokeColor(black)
        c.setLineWidth(0.6)
        c.rect(gx, gy, 20 * mm, 10 * mm, fill=1, stroke=1)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 5)
        label = f"G{i+1}" if i < 2 else "G3(N+1)"
        c.drawCentredString(gx + 10 * mm, gy + 4 * mm, label)

    # Cooling Yard (outside building, top right)
    cy_x = ox + bw + 4 * mm
    cy_y = oy + 54 * mm
    cy_w = 28 * mm
    cy_h = bh - 54 * mm
    c.setStrokeColor(C_COOL_SUPPLY)
    c.setFillColor(C_LIGHT_BLUE)
    c.setLineWidth(1.5)
    c.setDash(4, 2)
    c.rect(cy_x, cy_y, cy_w, cy_h, fill=1, stroke=1)
    c.setDash()
    c.setFillColor(C_COOL_SUPPLY)
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(cy_x + cy_w / 2, cy_y + cy_h - 6 * mm, "COOLING")
    c.drawCentredString(cy_x + cy_w / 2, cy_y + cy_h - 10 * mm, "YARD")
    c.setFont("Helvetica", 5)
    c.drawCentredString(cy_x + cy_w / 2, cy_y + cy_h - 15 * mm, "Cooling Towers")

    # ── NORTH ARROW ──
    draw_north_arrow(c, DRW_RIGHT - 8 * mm, DRW_TOP - 8 * mm)

    # ── LEGEND ──
    lx = DRW_RIGHT - 52 * mm
    ly = DRW_BOTTOM + 2 * mm
    c.setStrokeColor(black)
    c.setFillColor(white)
    c.setLineWidth(0.5)
    c.rect(lx, ly, 50 * mm, 34 * mm, fill=1, stroke=1)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 6)
    c.drawString(lx + 2 * mm, ly + 29 * mm, "LEGEND")
    c.setLineWidth(0.3)
    c.line(lx + 2 * mm, ly + 28 * mm, lx + 48 * mm, ly + 28 * mm)

    draw_legend_item(c, lx + 2 * mm, ly + 23 * mm, C_RACK_FILL, "Server Rack (42U)")
    draw_legend_item(c, lx + 2 * mm, ly + 18 * mm, C_COLD, "Cold Aisle Containment", "dash")
    draw_legend_item(c, lx + 2 * mm, ly + 13 * mm, C_HOT, "Hot Aisle Containment", "dash")
    draw_legend_item(c, lx + 2 * mm, ly + 8 * mm, C_GEN, "Generator (N+1)")
    draw_legend_item(c, lx + 2 * mm, ly + 3 * mm, C_LIGHT_PURPLE, "UPS Room (A/B Redundant)")

    # ── GENERAL NOTES ──
    nx = DRW_LEFT + 2 * mm
    ny = DRW_BOTTOM + 2 * mm
    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(black)
    c.drawString(nx, ny + 30 * mm, "GENERAL NOTES:")
    notes = [
        "1. 16 racks total: 4 rows × 4 racks, hot/cold aisle containment",
        "2. Raised floor: 600mm plenum for under-floor cooling distribution",
        "3. Dual power feeds (A+B) to each rack via redundant PDUs",
        "4. Concurrent maintainability: all mechanical/electrical serviceable",
        "   without IT load interruption (Tier III requirement)",
        "5. Fire suppression: VESDA detection + Novec 1230 clean agent",
        "6. Physical security: mantrap entry, biometric + card access",
        "7. N+1 redundancy: generators, UPS, chillers, CRAHs",
    ]
    c.setFont("Helvetica", 5)
    for i, note in enumerate(notes):
        c.drawString(nx, ny + 24 * mm - i * 3.2 * mm, note)


# ═══════════════════════════════════════════════════════════
#  DRAWING 2: ELECTRICAL SINGLE LINE DIAGRAM
# ═══════════════════════════════════════════════════════════
def draw_electrical(c):
    draw_border(c)
    draw_title_block(c, "SAT-DC-EL-001", "ELECTRICAL SINGLE LINE DIAGRAM",
                     "Dual Feed — N+1 Redundancy", "IEC 60617 / IEEE C2")
    draw_grid_refs(c)

    cx = DRW_LEFT + DRW_W / 2
    top = DRW_TOP - 8 * mm

    # ── UTILITY FEEDS ──
    feed_a_x = cx - 55 * mm
    feed_b_x = cx + 55 * mm

    for fx, label, color in [(feed_a_x, "UTILITY FEED A", C_ELEC_A),
                              (feed_b_x, "UTILITY FEED B", C_ELEC_B)]:
        c.setFillColor(color)
        c.setStrokeColor(black)
        c.setLineWidth(1)
        c.rect(fx - 20 * mm, top - 2 * mm, 40 * mm, 8 * mm, fill=1, stroke=1)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(fx, top + 2 * mm, label)
        c.setFont("Helvetica", 5)
        c.drawCentredString(fx, top - 1 * mm, "20kV / 50Hz")

    # Bus bars
    bus_y1 = top - 18 * mm
    c.setStrokeColor(C_ELEC_A)
    c.setLineWidth(3)
    c.line(feed_a_x - 30 * mm, bus_y1, feed_a_x + 30 * mm, bus_y1)
    c.setFont("Helvetica-Bold", 5)
    c.setFillColor(C_ELEC_A)
    c.drawString(feed_a_x - 30 * mm, bus_y1 + 2 * mm, "MV SWGR-A (20kV)")

    c.setStrokeColor(C_ELEC_B)
    c.setLineWidth(3)
    c.line(feed_b_x - 30 * mm, bus_y1, feed_b_x + 30 * mm, bus_y1)
    c.setFillColor(C_ELEC_B)
    c.drawString(feed_b_x - 30 * mm, bus_y1 + 2 * mm, "MV SWGR-B (20kV)")

    # Vertical from utility to bus
    for fx, color in [(feed_a_x, C_ELEC_A), (feed_b_x, C_ELEC_B)]:
        c.setStrokeColor(color)
        c.setLineWidth(1.5)
        c.line(fx, top - 2 * mm, fx, bus_y1)
        # CB symbol
        cb_y = top - 10 * mm
        c.setFillColor(white)
        c.setStrokeColor(black)
        c.setLineWidth(0.8)
        c.rect(fx - 3 * mm, cb_y - 2 * mm, 6 * mm, 4 * mm, fill=1, stroke=1)
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 4)
        c.drawCentredString(fx, cb_y - 0.5 * mm, "CB")

    # ── GENERATORS ──
    gen_y = bus_y1
    gen_a_x = feed_a_x - 45 * mm
    gen_b_x = feed_b_x + 45 * mm

    for gx, label, color in [(gen_a_x, "GEN-A", C_GEN), (gen_b_x, "GEN-B", C_GEN)]:
        # Generator circle (IEC 60617)
        c.setFillColor(C_LIGHT_YELLOW)
        c.setStrokeColor(color)
        c.setLineWidth(1.5)
        c.circle(gx, gen_y - 12 * mm, 8 * mm, fill=1, stroke=1)
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(gx, gen_y - 14 * mm, "G")
        c.setFont("Helvetica", 5)
        c.drawCentredString(gx, gen_y - 22 * mm, label)
        c.drawCentredString(gx, gen_y - 26 * mm, "1500kVA")
        # ATS
        c.setStrokeColor(color)
        c.setLineWidth(1)
        c.line(gx, gen_y - 4 * mm, gx, gen_y)
        offset = 45 * mm if gx == gen_a_x else -45 * mm
        c.line(gx, gen_y, gx + offset, gen_y)

    # N+1 spare generator
    spare_x = cx
    c.setFillColor(C_LIGHT_YELLOW)
    c.setStrokeColor(C_GEN)
    c.setLineWidth(1)
    c.setDash(3, 2)
    c.circle(spare_x, gen_y - 12 * mm, 8 * mm, fill=1, stroke=1)
    c.setDash()
    c.setFillColor(C_GEN)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(spare_x, gen_y - 14 * mm, "G")
    c.setFont("Helvetica", 5)
    c.drawCentredString(spare_x, gen_y - 22 * mm, "GEN-S (N+1)")
    c.drawCentredString(spare_x, gen_y - 26 * mm, "1500kVA SPARE")

    # ── TRANSFORMERS ──
    tx_y = bus_y1 - 40 * mm
    for fx, label, color in [(feed_a_x, "TX-A", C_ELEC_A), (feed_b_x, "TX-B", C_ELEC_B)]:
        c.setStrokeColor(color)
        c.setLineWidth(1)
        c.line(fx, bus_y1, fx, tx_y + 10 * mm)
        # Transformer symbol (IEC 60617 — two overlapping circles)
        c.setFillColor(white)
        c.setStrokeColor(color)
        c.setLineWidth(1.2)
        c.circle(fx, tx_y + 7 * mm, 5 * mm, fill=1, stroke=1)
        c.circle(fx, tx_y + 1 * mm, 5 * mm, fill=1, stroke=1)
        c.setFillColor(color)
        c.setFont("Helvetica", 5)
        c.drawCentredString(fx, tx_y - 7 * mm, label)
        c.drawCentredString(fx, tx_y - 11 * mm, "20kV/415V Dyn11")
        c.line(fx, tx_y - 4 * mm, fx, tx_y - 14 * mm)

    # ── LV SWITCHBOARDS ──
    lv_y = tx_y - 22 * mm
    for fx, label, color in [(feed_a_x, "LV SWBD-A (415V)", C_ELEC_A),
                              (feed_b_x, "LV SWBD-B (415V)", C_ELEC_B)]:
        c.setStrokeColor(color)
        c.setLineWidth(3)
        c.line(fx - 30 * mm, lv_y, fx + 30 * mm, lv_y)
        c.setFont("Helvetica-Bold", 5)
        c.setFillColor(color)
        c.drawString(fx - 30 * mm, lv_y + 2 * mm, label)

    # ── UPS SYSTEMS ──
    ups_y = lv_y - 25 * mm
    for fx, label, color in [(feed_a_x, "UPS", C_ELEC_A), (feed_b_x, "UPS", C_ELEC_B)]:
        # 2 active + 1 spare per feed
        for i in range(3):
            ux = fx - 20 * mm + i * 20 * mm
            c.setStrokeColor(color)
            c.setLineWidth(1)
            c.line(ux, lv_y, ux, ups_y + 8 * mm)

            lw = 0.8 if i < 2 else 0.5
            c.setLineWidth(lw)
            if i == 2:
                c.setDash(3, 2)
            c.setFillColor(C_LIGHT_PURPLE)
            c.rect(ux - 8 * mm, ups_y, 16 * mm, 8 * mm, fill=1, stroke=1)
            if i == 2:
                c.setDash()
            c.setFillColor(color)
            c.setFont("Helvetica-Bold", 5)
            tag = f"{label}-{chr(65 + (0 if fx == feed_a_x else 1))}{i+1}"
            if i == 2:
                tag += "(N+1)"
            c.drawCentredString(ux, ups_y + 3 * mm, tag)

            # Battery
            c.setFont("Helvetica", 4)
            c.setFillColor(HexColor("#666666"))
            c.drawCentredString(ux, ups_y - 4 * mm, "BATT")

    # ── STS ──
    sts_y = ups_y - 20 * mm
    c.setStrokeColor(black)
    c.setLineWidth(1.5)
    c.line(feed_a_x, ups_y, feed_a_x, sts_y + 6 * mm)
    c.line(feed_b_x, ups_y, feed_b_x, sts_y + 6 * mm)

    for i in range(4):
        sx = cx - 30 * mm + i * 20 * mm
        c.setFillColor(HexColor("#d5dbdb"))
        c.setStrokeColor(black)
        c.setLineWidth(0.8)
        c.rect(sx - 8 * mm, sts_y, 16 * mm, 6 * mm, fill=1, stroke=1)
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 5)
        c.drawCentredString(sx, sts_y + 2 * mm, f"STS-{i+1}")
        # Lines from both feeds
        c.setStrokeColor(C_ELEC_A)
        c.setLineWidth(0.5)
        c.line(feed_a_x + (i - 1.5) * 6 * mm, ups_y, sx - 2 * mm, sts_y + 6 * mm)
        c.setStrokeColor(C_ELEC_B)
        c.line(feed_b_x + (i - 1.5) * 6 * mm, ups_y, sx + 2 * mm, sts_y + 6 * mm)

    # ── PDU / RACKS ──
    pdu_y = sts_y - 18 * mm
    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(black)
    c.drawCentredString(cx, pdu_y + 10 * mm, "PDU DISTRIBUTION")

    rack_y = pdu_y - 12 * mm
    for i in range(16):
        rx = cx - 72 * mm + i * 9.5 * mm
        c.setFillColor(C_RACK_FILL)
        c.setStrokeColor(C_RACK)
        c.setLineWidth(0.6)
        c.rect(rx - 3.5 * mm, rack_y, 7 * mm, 8 * mm, fill=1, stroke=1)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 4)
        row = chr(65 + i // 8)
        num = (i % 8) + 1
        c.drawCentredString(rx, rack_y + 3 * mm, f"{row}{num:02d}")
        # Dual cord lines
        c.setStrokeColor(C_ELEC_A)
        c.setLineWidth(0.3)
        c.line(rx - 1.5 * mm, rack_y + 8 * mm, rx - 1.5 * mm, rack_y + 11 * mm)
        c.setStrokeColor(C_ELEC_B)
        c.line(rx + 1.5 * mm, rack_y + 8 * mm, rx + 1.5 * mm, rack_y + 11 * mm)

    c.setFont("Helvetica", 5)
    c.setFillColor(black)
    c.drawCentredString(cx, rack_y - 5 * mm, "16 × DUAL-CORDED IT RACKS (A+B FEED)")

    # ── LEGEND ──
    lx = DRW_RIGHT - 50 * mm
    ly = DRW_BOTTOM + 2 * mm
    c.setStrokeColor(black)
    c.setFillColor(white)
    c.setLineWidth(0.5)
    c.rect(lx, ly, 48 * mm, 32 * mm, fill=1, stroke=1)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 6)
    c.drawString(lx + 2 * mm, ly + 27 * mm, "LEGEND")
    c.setLineWidth(0.3)
    c.line(lx + 2 * mm, ly + 26 * mm, lx + 46 * mm, ly + 26 * mm)

    draw_legend_item(c, lx + 2 * mm, ly + 21 * mm, C_ELEC_A, "Path A (Primary)", "line")
    draw_legend_item(c, lx + 2 * mm, ly + 16 * mm, C_ELEC_B, "Path B (Redundant)", "line")
    draw_legend_item(c, lx + 2 * mm, ly + 11 * mm, C_GEN, "Generator (IEC 60617)", "circle")
    draw_legend_item(c, lx + 2 * mm, ly + 6 * mm, C_LIGHT_PURPLE, "UPS Module")
    draw_legend_item(c, lx + 2 * mm, ly + 1 * mm, C_DASHED, "N+1 Spare (Standby)", "dash")


# ═══════════════════════════════════════════════════════════
#  DRAWING 3: NETWORK TOPOLOGY
# ═══════════════════════════════════════════════════════════
def draw_network(c):
    draw_border(c)
    draw_title_block(c, "SAT-DC-NT-001", "NETWORK TOPOLOGY DIAGRAM",
                     "Redundant Core — Dual ISP", "TIA-942 / ISO/IEC 24764")
    draw_grid_refs(c)

    cx = DRW_LEFT + DRW_W / 2
    top = DRW_TOP - 6 * mm

    def net_box(x, y, w, h, label, sublabel, fill, border_color=black):
        c.setFillColor(fill)
        c.setStrokeColor(border_color)
        c.setLineWidth(1)
        c.roundRect(x - w / 2, y - h / 2, w, h, 2 * mm, fill=1, stroke=1)
        c.setFillColor(white if fill != white else black)
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(x, y + 1 * mm, label)
        if sublabel:
            c.setFont("Helvetica", 4.5)
            c.drawCentredString(x, y - 4 * mm, sublabel)

    def net_line(x1, y1, x2, y2, color=black, width=1, dashed=False):
        c.setStrokeColor(color)
        c.setLineWidth(width)
        if dashed:
            c.setDash(3, 2)
        c.line(x1, y1, x2, y2)
        if dashed:
            c.setDash()

    # ── ZONE: WAN / INTERNET ──
    zone_wan_y = top - 6 * mm
    c.setFillColor(HexColor("#fef9e7"))
    c.setStrokeColor(C_GEN)
    c.setLineWidth(0.5)
    c.setDash(3, 2)
    c.rect(DRW_LEFT + 20 * mm, zone_wan_y - 14 * mm, DRW_W - 40 * mm, 18 * mm, fill=1, stroke=1)
    c.setDash()
    c.setFillColor(C_GEN)
    c.setFont("Helvetica-Bold", 5)
    c.drawString(DRW_LEFT + 22 * mm, zone_wan_y + 1 * mm, "ZONE: WAN / INTERNET")

    isp_a_x = cx - 40 * mm
    isp_b_x = cx + 40 * mm
    isp_y = zone_wan_y - 6 * mm
    net_box(isp_a_x, isp_y, 30 * mm, 10 * mm, "ISP-A", "Primary / BGP", C_NET_CORE)
    net_box(isp_b_x, isp_y, 30 * mm, 10 * mm, "ISP-B", "Secondary / BGP", C_NET_CORE)

    # ── ZONE: DMZ ──
    zone_dmz_y = zone_wan_y - 34 * mm
    c.setFillColor(C_LIGHT_RED)
    c.setStrokeColor(C_FIRE)
    c.setLineWidth(0.5)
    c.setDash(3, 2)
    c.rect(DRW_LEFT + 20 * mm, zone_dmz_y - 16 * mm, DRW_W - 40 * mm, 24 * mm, fill=1, stroke=1)
    c.setDash()
    c.setFillColor(C_FIRE)
    c.setFont("Helvetica-Bold", 5)
    c.drawString(DRW_LEFT + 22 * mm, zone_dmz_y + 5 * mm, "ZONE: DMZ / BORDER")

    # Border routers
    br_a_x = cx - 40 * mm
    br_b_x = cx + 40 * mm
    br_y = zone_dmz_y + 1 * mm
    net_box(br_a_x, br_y, 28 * mm, 9 * mm, "BR-A", "Border Router", C_NET_CORE)
    net_box(br_b_x, br_y, 28 * mm, 9 * mm, "BR-B", "Border Router", C_NET_CORE)

    net_line(isp_a_x, isp_y - 5 * mm, br_a_x, br_y + 4.5 * mm, C_NET_CORE, 1.5)
    net_line(isp_b_x, isp_y - 5 * mm, br_b_x, br_y + 4.5 * mm, C_NET_CORE, 1.5)

    # Firewalls
    fw_a_x = cx - 40 * mm
    fw_b_x = cx + 40 * mm
    fw_y = zone_dmz_y - 9 * mm
    net_box(fw_a_x, fw_y, 28 * mm, 9 * mm, "FW-A", "Active", C_FIRE, C_FIRE)
    net_box(fw_b_x, fw_y, 28 * mm, 9 * mm, "FW-B", "Standby", C_FIRE, C_FIRE)

    net_line(br_a_x, br_y - 4.5 * mm, fw_a_x, fw_y + 4.5 * mm, C_NET_CORE, 1)
    net_line(br_b_x, br_y - 4.5 * mm, fw_b_x, fw_y + 4.5 * mm, C_NET_CORE, 1)
    # HA heartbeat
    net_line(fw_a_x + 14 * mm, fw_y, fw_b_x - 14 * mm, fw_y, C_FIRE, 0.5, True)
    c.setFillColor(C_FIRE)
    c.setFont("Helvetica", 4)
    c.drawCentredString(cx, fw_y + 2 * mm, "HA HEARTBEAT")

    # ── ZONE: CORE ──
    zone_core_y = zone_dmz_y - 38 * mm
    c.setFillColor(C_LIGHT_GREEN)
    c.setStrokeColor(C_MECH)
    c.setLineWidth(0.5)
    c.setDash(3, 2)
    c.rect(DRW_LEFT + 20 * mm, zone_core_y - 8 * mm, DRW_W - 40 * mm, 20 * mm, fill=1, stroke=1)
    c.setDash()
    c.setFillColor(C_MECH)
    c.setFont("Helvetica-Bold", 5)
    c.drawString(DRW_LEFT + 22 * mm, zone_core_y + 9 * mm, "ZONE: CORE NETWORK")

    # Core switches
    cs_a_x = cx - 40 * mm
    cs_b_x = cx + 40 * mm
    cs_y = zone_core_y + 2 * mm
    net_box(cs_a_x, cs_y, 32 * mm, 10 * mm, "CORE-SW-A", "L3 / 40GbE", C_MECH)
    net_box(cs_b_x, cs_y, 32 * mm, 10 * mm, "CORE-SW-B", "L3 / 40GbE", C_MECH)

    net_line(fw_a_x, fw_y - 4.5 * mm, cs_a_x, cs_y + 5 * mm, C_NET_CORE, 1)
    net_line(fw_b_x, fw_y - 4.5 * mm, cs_b_x, cs_y + 5 * mm, C_NET_CORE, 1)
    # Cross connect
    net_line(cs_a_x + 16 * mm, cs_y, cs_b_x - 16 * mm, cs_y, C_MECH, 1.5)
    c.setFillColor(C_MECH)
    c.setFont("Helvetica", 4)
    c.drawCentredString(cx, cs_y + 2 * mm, "40GbE CROSS-CONNECT")

    # ── ZONE: ACCESS ──
    zone_acc_y = zone_core_y - 30 * mm
    c.setFillColor(C_LIGHT_BLUE)
    c.setStrokeColor(C_COOL_SUPPLY)
    c.setLineWidth(0.5)
    c.setDash(3, 2)
    c.rect(DRW_LEFT + 10 * mm, zone_acc_y - 18 * mm, DRW_W - 20 * mm, 32 * mm, fill=1, stroke=1)
    c.setDash()
    c.setFillColor(C_COOL_SUPPLY)
    c.setFont("Helvetica-Bold", 5)
    c.drawString(DRW_LEFT + 12 * mm, zone_acc_y + 11 * mm, "ZONE: ACCESS / TOP-OF-RACK")

    # ToR Switches (8 pairs for 16 racks)
    tor_y = zone_acc_y + 4 * mm
    for i in range(8):
        tx = DRW_LEFT + 30 * mm + i * 30 * mm
        c.setFillColor(C_NET_AGG)
        c.setStrokeColor(black)
        c.setLineWidth(0.6)
        c.roundRect(tx - 12 * mm, tor_y - 3.5 * mm, 24 * mm, 7 * mm, 1 * mm, fill=1, stroke=1)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 5)
        c.drawCentredString(tx, tor_y, f"ToR-{i+1}")
        # Uplinks to both cores
        net_line(tx - 3 * mm, tor_y + 3.5 * mm, cs_a_x, cs_y - 5 * mm, C_NET_AGG, 0.4)
        net_line(tx + 3 * mm, tor_y + 3.5 * mm, cs_b_x, cs_y - 5 * mm, C_NET_AGG, 0.4)

    # Racks under ToR
    rack_y = zone_acc_y - 12 * mm
    for i in range(16):
        rx = DRW_LEFT + 22 * mm + i * 15.5 * mm
        c.setFillColor(C_RACK_FILL)
        c.setStrokeColor(C_RACK)
        c.setLineWidth(0.5)
        c.rect(rx - 5 * mm, rack_y, 10 * mm, 7 * mm, fill=1, stroke=1)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 4)
        row = chr(65 + i // 8)
        num = (i % 8) + 1
        c.drawCentredString(rx, rack_y + 2.5 * mm, f"{row}{num:02d}")
        # Link to ToR
        tor_idx = i // 2
        tor_x = DRW_LEFT + 30 * mm + tor_idx * 30 * mm
        net_line(rx, rack_y + 7 * mm, tor_x, tor_y - 3.5 * mm, C_NET_ACC, 0.3)

    # ── OOB MANAGEMENT ──
    oob_x = DRW_RIGHT - 40 * mm
    oob_y = zone_core_y + 2 * mm
    c.setFillColor(HexColor("#d5dbdb"))
    c.setStrokeColor(black)
    c.setLineWidth(0.8)
    c.setDash(3, 2)
    c.roundRect(oob_x - 15 * mm, oob_y - 12 * mm, 30 * mm, 24 * mm, 2 * mm, fill=1, stroke=1)
    c.setDash()
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 5)
    c.drawCentredString(oob_x, oob_y + 6 * mm, "OOB MGMT")
    c.setFont("Helvetica", 4)
    c.drawCentredString(oob_x, oob_y + 1 * mm, "IPMI / iLO / iDRAC")
    c.drawCentredString(oob_x, oob_y - 4 * mm, "Console Servers")
    c.drawCentredString(oob_x, oob_y - 9 * mm, "Separate VLAN")

    # ── LEGEND ──
    lx = DRW_LEFT + 4 * mm
    ly = DRW_BOTTOM + 2 * mm
    c.setStrokeColor(black)
    c.setFillColor(white)
    c.setLineWidth(0.5)
    c.rect(lx, ly, 55 * mm, 30 * mm, fill=1, stroke=1)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 6)
    c.drawString(lx + 2 * mm, ly + 25 * mm, "LEGEND")
    c.setLineWidth(0.3)
    c.line(lx + 2 * mm, ly + 24 * mm, lx + 53 * mm, ly + 24 * mm)

    draw_legend_item(c, lx + 2 * mm, ly + 19 * mm, C_NET_CORE, "WAN / Border (L3)")
    draw_legend_item(c, lx + 2 * mm, ly + 14 * mm, C_FIRE, "Firewall (HA Pair)")
    draw_legend_item(c, lx + 2 * mm, ly + 9 * mm, C_MECH, "Core Switch (L3 / 40GbE)")
    draw_legend_item(c, lx + 2 * mm, ly + 4 * mm, C_NET_AGG, "ToR Switch (L2 / 10GbE)")
    draw_legend_item(c, lx + 2 * mm, ly - 1 * mm, C_RACK_FILL, "Server Rack (Dual-homed)")


# ═══════════════════════════════════════════════════════════
#  DRAWING 4: COOLING SYSTEM
# ═══════════════════════════════════════════════════════════
def draw_cooling(c):
    draw_border(c)
    draw_title_block(c, "SAT-DC-CL-001", "COOLING SYSTEM DIAGRAM",
                     "Chilled Water — N+1 CRAHs", "ASHRAE TC 9.9")
    draw_grid_refs(c)

    cx = DRW_LEFT + DRW_W / 2
    top = DRW_TOP - 8 * mm

    def equip_box(x, y, w, h, label, sublabel, fill, is_spare=False):
        c.setStrokeColor(black if not is_spare else C_DASHED)
        c.setLineWidth(1 if not is_spare else 0.6)
        if is_spare:
            c.setDash(3, 2)
        c.setFillColor(fill)
        c.rect(x, y, w, h, fill=1, stroke=1)
        if is_spare:
            c.setDash()
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(x + w / 2, y + h / 2 + 1 * mm, label)
        if sublabel:
            c.setFont("Helvetica", 4.5)
            c.drawCentredString(x + w / 2, y + h / 2 - 4 * mm, sublabel)

    # ── OUTDOOR SECTION ──
    out_x = DRW_LEFT + 4 * mm
    out_y = top - 40 * mm
    out_w = 80 * mm
    out_h = 38 * mm
    c.setFillColor(C_LIGHT_YELLOW)
    c.setStrokeColor(C_GEN)
    c.setLineWidth(0.5)
    c.setDash(3, 2)
    c.rect(out_x, out_y, out_w, out_h, fill=1, stroke=1)
    c.setDash()
    c.setFillColor(C_GEN)
    c.setFont("Helvetica-Bold", 6)
    c.drawString(out_x + 2 * mm, out_y + out_h - 6 * mm, "OUTDOOR — COOLING YARD")

    # Cooling towers
    ct_y = out_y + out_h - 18 * mm
    for i in range(3):
        ctx = out_x + 8 * mm + i * 26 * mm
        is_spare = (i == 2)
        equip_box(ctx, ct_y, 22 * mm, 10 * mm,
                  f"CT-{i+1}" + (" (N+1)" if is_spare else ""),
                  "500kW Reject", HexColor("#85c1e9"), is_spare)

    # Condenser water labels
    c.setFont("Helvetica", 4.5)
    c.setFillColor(C_COOL_RETURN)
    c.drawCentredString(out_x + out_w / 2, out_y + 5 * mm, "Condenser Water Loop (32°C/37°C)")

    # ── CHILLER PLANT ──
    ch_x = DRW_LEFT + 4 * mm
    ch_y = out_y - 38 * mm
    ch_w = 80 * mm
    ch_h = 34 * mm
    c.setFillColor(C_LIGHT_BLUE)
    c.setStrokeColor(C_COOL_SUPPLY)
    c.setLineWidth(0.5)
    c.setDash(3, 2)
    c.rect(ch_x, ch_y, ch_w, ch_h, fill=1, stroke=1)
    c.setDash()
    c.setFillColor(C_COOL_SUPPLY)
    c.setFont("Helvetica-Bold", 6)
    c.drawString(ch_x + 2 * mm, ch_y + ch_h - 6 * mm, "CHILLER PLANT ROOM")

    # Chillers
    chl_y = ch_y + ch_h - 18 * mm
    for i in range(3):
        clx = ch_x + 8 * mm + i * 26 * mm
        is_spare = (i == 2)
        equip_box(clx, chl_y, 22 * mm, 10 * mm,
                  f"CH-{i+1}" + (" (N+1)" if is_spare else ""),
                  "500kW", C_COOL_SUPPLY, is_spare)

    # Primary pumps
    pump_y = ch_y + 3 * mm
    c.setFont("Helvetica-Bold", 5)
    c.setFillColor(black)
    c.drawString(ch_x + 4 * mm, pump_y + 6 * mm, "PRIMARY CHW PUMPS")
    for i in range(3):
        px = ch_x + 8 * mm + i * 26 * mm
        is_spare = (i == 2)
        c.setFillColor(C_MECH)
        c.setStrokeColor(black if not is_spare else C_DASHED)
        c.setLineWidth(0.6)
        if is_spare:
            c.setDash(3, 2)
        c.circle(px + 5 * mm, pump_y, 4 * mm, fill=1, stroke=1)
        if is_spare:
            c.setDash()
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 5)
        c.drawCentredString(px + 5 * mm, pump_y - 1.5 * mm, f"P{i+1}")

    # Pipes connecting outdoor to chiller
    c.setStrokeColor(C_COOL_SUPPLY)
    c.setLineWidth(2)
    c.line(out_x + 20 * mm, out_y, out_x + 20 * mm, ch_y + ch_h)
    c.setStrokeColor(C_COOL_RETURN)
    c.setLineWidth(2)
    c.line(out_x + 60 * mm, out_y, out_x + 60 * mm, ch_y + ch_h)

    # ── CHW DISTRIBUTION ──
    dist_x = ch_x + ch_w + 8 * mm
    dist_y = ch_y
    dist_w = DRW_RIGHT - dist_x - 4 * mm
    dist_h = out_y + out_h - ch_y

    c.setFillColor(white)
    c.setStrokeColor(C_WALL)
    c.setLineWidth(1)
    c.rect(dist_x, dist_y, dist_w, dist_h, fill=1, stroke=1)
    c.setFillColor(C_WALL)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(dist_x + dist_w / 2, dist_y + dist_h - 7 * mm, "DATA HALL — CHW DISTRIBUTION")

    # Supply/Return headers
    header_y = dist_y + dist_h - 18 * mm
    c.setStrokeColor(C_COOL_SUPPLY)
    c.setLineWidth(2.5)
    c.line(dist_x + 5 * mm, header_y, dist_x + dist_w - 5 * mm, header_y)
    c.setFont("Helvetica-Bold", 5)
    c.setFillColor(C_COOL_SUPPLY)
    c.drawString(dist_x + 7 * mm, header_y + 2 * mm, "CHW SUPPLY (7°C)")

    return_y = header_y - 10 * mm
    c.setStrokeColor(C_COOL_RETURN)
    c.setLineWidth(2.5)
    c.line(dist_x + 5 * mm, return_y, dist_x + dist_w - 5 * mm, return_y)
    c.setFillColor(C_COOL_RETURN)
    c.drawString(dist_x + 7 * mm, return_y + 2 * mm, "CHW RETURN (12°C)")

    # Pipe from chiller plant
    c.setStrokeColor(C_COOL_SUPPLY)
    c.setLineWidth(2)
    c.line(ch_x + ch_w, ch_y + ch_h - 10 * mm, dist_x, header_y)
    c.setStrokeColor(C_COOL_RETURN)
    c.line(ch_x + ch_w, ch_y + 10 * mm, dist_x, return_y)

    # CRAH units
    crah_y = return_y - 22 * mm
    num_crah = 5  # 4 active + 1 spare
    crah_spacing = (dist_w - 10 * mm) / num_crah
    c.setFont("Helvetica-Bold", 5)
    c.setFillColor(black)
    c.drawString(dist_x + 5 * mm, crah_y + 14 * mm, "CRAH UNITS (N+1)")

    for i in range(num_crah):
        crx = dist_x + 8 * mm + i * crah_spacing
        is_spare = (i == num_crah - 1)
        equip_box(crx, crah_y, crah_spacing - 4 * mm, 12 * mm,
                  f"CRAH-{i+1}" + (" (N+1)" if is_spare else ""),
                  "150kW", HexColor("#a9cce3"), is_spare)
        # Supply pipe down from header
        c.setStrokeColor(C_COOL_SUPPLY)
        c.setLineWidth(0.8)
        c.line(crx + (crah_spacing - 4 * mm) / 2 - 2 * mm, header_y, crx + (crah_spacing - 4 * mm) / 2 - 2 * mm, crah_y + 12 * mm)
        c.setStrokeColor(C_COOL_RETURN)
        c.line(crx + (crah_spacing - 4 * mm) / 2 + 2 * mm, return_y, crx + (crah_spacing - 4 * mm) / 2 + 2 * mm, crah_y + 12 * mm)

    # Airflow pattern
    airflow_y = crah_y - 20 * mm
    c.setFont("Helvetica-Bold", 5)
    c.setFillColor(black)
    c.drawString(dist_x + 5 * mm, airflow_y + 12 * mm, "AIRFLOW PATTERN")

    # Cold aisle
    ca_x = dist_x + 15 * mm
    ca_w2 = dist_w - 30 * mm
    c.setFillColor(HexColor("#d6eaf8"))
    c.setStrokeColor(C_COLD)
    c.setLineWidth(0.6)
    c.rect(ca_x, airflow_y, ca_w2, 8 * mm, fill=1, stroke=1)
    c.setFillColor(C_COLD)
    c.setFont("Helvetica-Bold", 5)
    c.drawCentredString(ca_x + ca_w2 / 2, airflow_y + 3 * mm, "COLD AISLE (18-27°C per ASHRAE)")

    # Arrows showing airflow
    for i in range(5):
        ax = ca_x + 10 * mm + i * (ca_w2 - 20 * mm) / 4
        draw_arrow(c, ax, crah_y, ax, airflow_y + 8 * mm, C_COLD, 0.6)

    # Hot aisle
    ha_y = airflow_y - 10 * mm
    c.setFillColor(HexColor("#fadbd8"))
    c.setStrokeColor(C_HOT)
    c.setLineWidth(0.6)
    c.rect(ca_x, ha_y, ca_w2, 8 * mm, fill=1, stroke=1)
    c.setFillColor(C_HOT)
    c.setFont("Helvetica-Bold", 5)
    c.drawCentredString(ca_x + ca_w2 / 2, ha_y + 3 * mm, "HOT AISLE (< 40°C)")

    # Return arrows
    for i in range(5):
        ax = ca_x + 10 * mm + i * (ca_w2 - 20 * mm) / 4
        draw_arrow(c, ax, ha_y + 8 * mm, ax, airflow_y, C_HOT, 0.6)

    # ── ENVIRONMENTAL MONITORING ──
    em_x = dist_x + 5 * mm
    em_y = dist_y + 3 * mm
    c.setFillColor(HexColor("#d5dbdb"))
    c.setStrokeColor(black)
    c.setLineWidth(0.6)
    c.roundRect(em_x, em_y, 60 * mm, 12 * mm, 2 * mm, fill=1, stroke=1)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 5)
    c.drawCentredString(em_x + 30 * mm, em_y + 6 * mm, "ENVIRONMENTAL MONITORING")
    c.setFont("Helvetica", 4)
    c.drawCentredString(em_x + 30 * mm, em_y + 2 * mm, "Temp / Humidity / Leak / Airflow Sensors → BMS")

    # ── LEGEND ──
    lx = DRW_LEFT + 4 * mm
    ly = DRW_BOTTOM + 2 * mm
    c.setStrokeColor(black)
    c.setFillColor(white)
    c.setLineWidth(0.5)
    c.rect(lx, ly, 55 * mm, 30 * mm, fill=1, stroke=1)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 6)
    c.drawString(lx + 2 * mm, ly + 25 * mm, "LEGEND")
    c.setLineWidth(0.3)
    c.line(lx + 2 * mm, ly + 24 * mm, lx + 53 * mm, ly + 24 * mm)

    draw_legend_item(c, lx + 2 * mm, ly + 19 * mm, C_COOL_SUPPLY, "CHW Supply (7°C)", "line")
    draw_legend_item(c, lx + 2 * mm, ly + 14 * mm, C_COOL_RETURN, "CHW Return (12°C)", "line")
    draw_legend_item(c, lx + 2 * mm, ly + 9 * mm, C_COLD, "Cold Air (18-27°C)", "rect")
    draw_legend_item(c, lx + 2 * mm, ly + 4 * mm, C_HOT, "Hot Air Exhaust", "rect")
    draw_legend_item(c, lx + 2 * mm, ly - 1 * mm, C_DASHED, "N+1 Spare Equipment", "dash")


# ═══════════════════════════════════════════════════════════
#  DRAWING 5: FIRE SUPPRESSION
# ═══════════════════════════════════════════════════════════
def draw_fire(c):
    draw_border(c)
    draw_title_block(c, "SAT-DC-FS-001", "FIRE SUPPRESSION SYSTEM",
                     "VESDA / Clean Agent / Pre-Action", "NFPA 75 / NFPA 2001")
    draw_grid_refs(c)

    cx = DRW_LEFT + DRW_W / 2
    top = DRW_TOP - 8 * mm

    def sys_box(x, y, w, h, label, sublabel, fill, border=black):
        c.setFillColor(fill)
        c.setStrokeColor(border)
        c.setLineWidth(1)
        c.roundRect(x, y, w, h, 2 * mm, fill=1, stroke=1)
        c.setFillColor(white if fill not in (white, C_LIGHT_YELLOW, C_LIGHT_RED, C_LIGHT_GREEN, C_LIGHT_BLUE) else black)
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(x + w / 2, y + h / 2 + 1 * mm, label)
        if sublabel:
            c.setFont("Helvetica", 4.5)
            c.drawCentredString(x + w / 2, y + h / 2 - 4 * mm, sublabel)

    # ── FACP (TOP CENTER) ──
    facp_w = 60 * mm
    facp_h = 16 * mm
    facp_x = cx - facp_w / 2
    facp_y = top - facp_h - 2 * mm
    c.setFillColor(C_FIRE)
    c.setStrokeColor(black)
    c.setLineWidth(2)
    c.roundRect(facp_x, facp_y, facp_w, facp_h, 3 * mm, fill=1, stroke=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(cx, facp_y + facp_h / 2 + 2 * mm, "FACP")
    c.setFont("Helvetica", 5)
    c.drawCentredString(cx, facp_y + 3 * mm, "Fire Alarm Control Panel (Redundant, SIL 2)")

    # 72hr battery
    batt_x = facp_x + facp_w + 4 * mm
    sys_box(batt_x, facp_y + 2 * mm, 26 * mm, 12 * mm,
            "BATTERY", "72hr Standby", HexColor("#fdebd0"))
    c.setStrokeColor(C_FIRE)
    c.setLineWidth(1)
    c.line(facp_x + facp_w, facp_y + facp_h / 2, batt_x, facp_y + 8 * mm)

    # ── DETECTION TIER ──
    det_y = facp_y - 30 * mm
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(C_FIRE)
    c.drawString(DRW_LEFT + 8 * mm, det_y + 22 * mm, "DETECTION TIER")
    c.setLineWidth(0.3)
    c.line(DRW_LEFT + 8 * mm, det_y + 21 * mm, DRW_LEFT + 60 * mm, det_y + 21 * mm)

    # VESDA zones
    vesda_zones = [
        ("VESDA Zone 1", "Data Hall - Rows A/B"),
        ("VESDA Zone 2", "Data Hall - Rows C/D"),
        ("VESDA Zone 3", "Electrical / UPS"),
        ("VESDA Zone 4", "Under-Floor Plenum"),
    ]
    for i, (name, area) in enumerate(vesda_zones):
        vx = DRW_LEFT + 8 * mm + i * 60 * mm
        sys_box(vx, det_y, 54 * mm, 14 * mm, name, area, C_LIGHT_RED, C_FIRE)
        # Line to FACP
        c.setStrokeColor(C_FIRE)
        c.setLineWidth(0.6)
        c.line(vx + 27 * mm, det_y + 14 * mm, cx, facp_y)

    # Smoke detectors
    sd_y = det_y - 14 * mm
    c.setFont("Helvetica", 5)
    c.setFillColor(black)
    c.drawString(DRW_LEFT + 8 * mm, sd_y + 8 * mm, "POINT DETECTORS:")
    detectors = ["Photoelectric Smoke", "Heat (Rate-of-Rise)", "Beam Detector", "Manual Pull Stations"]
    for i, det in enumerate(detectors):
        dx = DRW_LEFT + 8 * mm + i * 60 * mm
        c.setFillColor(C_LIGHT_RED)
        c.setStrokeColor(C_FIRE)
        c.setLineWidth(0.5)
        c.circle(dx + 5 * mm, sd_y, 3 * mm, fill=1, stroke=1)
        c.setFillColor(black)
        c.setFont("Helvetica", 5)
        c.drawString(dx + 10 * mm, sd_y - 2 * mm, det)

    # ── SUPPRESSION TIER ──
    sup_y = sd_y - 30 * mm
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(C_FIRE)
    c.drawString(DRW_LEFT + 8 * mm, sup_y + 22 * mm, "SUPPRESSION TIER")
    c.setLineWidth(0.3)
    c.line(DRW_LEFT + 8 * mm, sup_y + 21 * mm, DRW_LEFT + 65 * mm, sup_y + 21 * mm)

    # Clean agent system
    ca_x = DRW_LEFT + 8 * mm
    sys_box(ca_x, sup_y, 75 * mm, 16 * mm,
            "CLEAN AGENT — NOVEC 1230 / FM-200", "Data Hall + Electrical Rooms",
            C_FIRE, C_FIRE)

    # Agent storage
    as_x = ca_x + 80 * mm
    sys_box(as_x, sup_y, 50 * mm, 16 * mm,
            "AGENT STORAGE", "Cylinders + Manifold", HexColor("#fdebd0"))

    c.setStrokeColor(C_FIRE)
    c.setLineWidth(1)
    c.line(ca_x + 75 * mm, sup_y + 8 * mm, as_x, sup_y + 8 * mm)

    # Pre-action sprinkler
    pa_x = as_x + 55 * mm
    sys_box(pa_x, sup_y, 55 * mm, 16 * mm,
            "PRE-ACTION SPRINKLER", "Support Areas / Corridors",
            HexColor("#a9cce3"))

    # ── INTEGRATION TIER ──
    int_y = sup_y - 32 * mm
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(C_FIRE)
    c.drawString(DRW_LEFT + 8 * mm, int_y + 22 * mm, "INTEGRATION & NOTIFICATION")
    c.setLineWidth(0.3)
    c.line(DRW_LEFT + 8 * mm, int_y + 21 * mm, DRW_LEFT + 75 * mm, int_y + 21 * mm)

    integrations = [
        ("EPO SYSTEM", "Emergency Power Off", C_ELEC_A),
        ("BMS / SCADA", "Building Management", C_MECH),
        ("HVAC SHUTDOWN", "Damper Close on Alarm", C_COOL_SUPPLY),
        ("NOTIFICATION", "Strobe/Horn + Remote", HexColor("#f39c12")),
    ]
    for i, (name, desc, color) in enumerate(integrations):
        ix = DRW_LEFT + 8 * mm + i * 62 * mm
        sys_box(ix, int_y, 56 * mm, 14 * mm, name, desc, color)
        # Line to FACP
        c.setStrokeColor(C_FIRE)
        c.setLineWidth(0.5)
        c.setDash(2, 1.5)
        mid_x = ix + 28 * mm
        c.line(mid_x, int_y + 14 * mm, mid_x, int_y + 18 * mm)
        c.line(mid_x, int_y + 18 * mm, cx, int_y + 18 * mm)
        c.setDash()

    # ── SEQUENCE OF OPERATIONS ──
    seq_y = int_y - 28 * mm
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(black)
    c.drawString(DRW_LEFT + 8 * mm, seq_y + 22 * mm, "SEQUENCE OF OPERATIONS")
    c.setLineWidth(0.5)
    c.line(DRW_LEFT + 8 * mm, seq_y + 21 * mm, DRW_LEFT + 72 * mm, seq_y + 21 * mm)

    steps = [
        ("1", "VESDA\nALERT", HexColor("#f5b041")),
        ("2", "VESDA\nACTION", HexColor("#eb984e")),
        ("3", "HVAC\nSHUTDOWN", C_COOL_SUPPLY),
        ("4", "PRE-\nDISCHARGE", HexColor("#e74c3c")),
        ("5", "AGENT\nDISCHARGE", C_FIRE),
        ("6", "EPO\n(IF REQ)", C_ELEC_A),
        ("7", "NOTIFY\nFIRE DEPT", HexColor("#f39c12")),
    ]
    step_w = 30 * mm
    for i, (num, label, color) in enumerate(steps):
        sx = DRW_LEFT + 10 * mm + i * 35 * mm
        c.setFillColor(color)
        c.setStrokeColor(black)
        c.setLineWidth(0.8)
        c.roundRect(sx, seq_y, step_w, 16 * mm, 2 * mm, fill=1, stroke=1)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(sx + step_w / 2, seq_y + 10 * mm, num)
        c.setFont("Helvetica-Bold", 4.5)
        lines = label.split("\n")
        for j, line in enumerate(lines):
            c.drawCentredString(sx + step_w / 2, seq_y + 5 * mm - j * 4 * mm, line)
        # Arrow to next
        if i < len(steps) - 1:
            draw_arrow(c, sx + step_w, seq_y + 8 * mm,
                       sx + step_w + 5 * mm, seq_y + 8 * mm, black, 0.8)

    # ── LEGEND ──
    lx = DRW_RIGHT - 50 * mm
    ly = DRW_BOTTOM + 2 * mm
    c.setStrokeColor(black)
    c.setFillColor(white)
    c.setLineWidth(0.5)
    c.rect(lx, ly, 48 * mm, 30 * mm, fill=1, stroke=1)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 6)
    c.drawString(lx + 2 * mm, ly + 25 * mm, "LEGEND")
    c.setLineWidth(0.3)
    c.line(lx + 2 * mm, ly + 24 * mm, lx + 46 * mm, ly + 24 * mm)

    draw_legend_item(c, lx + 2 * mm, ly + 19 * mm, C_FIRE, "Fire Alarm / Detection")
    draw_legend_item(c, lx + 2 * mm, ly + 14 * mm, C_LIGHT_RED, "VESDA Zone", "circle")
    draw_legend_item(c, lx + 2 * mm, ly + 9 * mm, HexColor("#fdebd0"), "Agent Storage")
    draw_legend_item(c, lx + 2 * mm, ly + 4 * mm, C_MECH, "BMS Integration")
    draw_legend_item(c, lx + 2 * mm, ly - 1 * mm, C_DASHED, "Control Signal", "dash")


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════
def main():
    out_dir = os.path.join(os.path.dirname(__file__), "build", "pdf")
    os.makedirs(out_dir, exist_ok=True)

    drawings = [
        ("SAT-DC-FP-001_Floor-Plan.pdf", draw_floor_plan),
        ("SAT-DC-EL-001_Electrical-SLD.pdf", draw_electrical),
        ("SAT-DC-NT-001_Network-Topology.pdf", draw_network),
        ("SAT-DC-CL-001_Cooling-System.pdf", draw_cooling),
        ("SAT-DC-FS-001_Fire-Suppression.pdf", draw_fire),
    ]

    print("=== Satsiber DC — Generating PDF Drawings (A4 Landscape) ===\n")
    for i, (filename, draw_fn) in enumerate(drawings, 1):
        filepath = os.path.join(out_dir, filename)
        print(f"[{i}/{len(drawings)}] {filename}...")
        pdf = canvas.Canvas(filepath, pagesize=landscape(A4))
        pdf.setTitle(filename.replace(".pdf", "").replace("_", " "))
        pdf.setAuthor("Satsiber Engineering")
        pdf.setSubject("Uptime Tier III Design Certification")
        draw_fn(pdf)
        pdf.save()
        print(f"  ✓ {filepath}")

    print(f"\nDone! All PDFs saved to: {out_dir}/")
    print("Open with any PDF viewer (Evince, Okular, Chrome, etc.)")


if __name__ == "__main__":
    main()
