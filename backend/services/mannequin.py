"""
Parametric mannequin — single connected human body mesh.
Y=up, origin at feet, total height ~1.75 units.
"""

import numpy as np
import trimesh
from trimesh import creation
import logging

logger = logging.getLogger(__name__)


def build_mannequin_mesh() -> trimesh.Trimesh:
    parts = []

    # ── Feet / ankles ─────────────────────────────────────────────────
    parts.append(_cyl(rx=0.055, rz=0.065, h=0.08, cx=-0.08, cy=0.00, cz=0.0))
    parts.append(_cyl(rx=0.055, rz=0.065, h=0.08, cx= 0.08, cy=0.00, cz=0.0))

    # ── Lower legs ────────────────────────────────────────────────────
    parts.append(_cyl(rx=0.060, rz=0.070, h=0.30, cx=-0.08, cy=0.08, cz=0.0))
    parts.append(_cyl(rx=0.060, rz=0.070, h=0.30, cx= 0.08, cy=0.08, cz=0.0))

    # ── Knees ─────────────────────────────────────────────────────────
    parts.append(_sphere(r=0.068, cx=-0.08, cy=0.40, cz=0.0))
    parts.append(_sphere(r=0.068, cx= 0.08, cy=0.40, cz=0.0))

    # ── Upper legs ────────────────────────────────────────────────────
    parts.append(_cyl(rx=0.075, rz=0.085, h=0.30, cx=-0.08, cy=0.42, cz=0.0))
    parts.append(_cyl(rx=0.075, rz=0.085, h=0.30, cx= 0.08, cy=0.42, cz=0.0))

    # ── Hips / pelvis ─────────────────────────────────────────────────
    parts.append(_ellipsoid(rx=0.19, ry=0.13, rz=0.12, cx=0.0, cy=0.73, cz=0.0))

    # ── Waist ─────────────────────────────────────────────────────────
    parts.append(_cyl(rx=0.155, rz=0.110, h=0.14, cx=0.0, cy=0.80, cz=0.0))

    # ── Chest / torso ─────────────────────────────────────────────────
    parts.append(_ellipsoid(rx=0.21, ry=0.17, rz=0.13, cx=0.0, cy=1.02, cz=0.0))

    # ── Shoulders ─────────────────────────────────────────────────────
    parts.append(_sphere(r=0.085, cx=-0.25, cy=1.18, cz=0.0))
    parts.append(_sphere(r=0.085, cx= 0.25, cy=1.18, cz=0.0))

    # ── Upper arms ────────────────────────────────────────────────────
    parts.append(_cyl(rx=0.058, rz=0.058, h=0.26, cx=-0.27, cy=0.96, cz=0.0))
    parts.append(_cyl(rx=0.058, rz=0.058, h=0.26, cx= 0.27, cy=0.96, cz=0.0))

    # ── Elbows ────────────────────────────────────────────────────────
    parts.append(_sphere(r=0.052, cx=-0.28, cy=0.82, cz=0.0))
    parts.append(_sphere(r=0.052, cx= 0.28, cy=0.82, cz=0.0))

    # ── Forearms ──────────────────────────────────────────────────────
    parts.append(_cyl(rx=0.048, rz=0.048, h=0.24, cx=-0.28, cy=0.64, cz=0.0))
    parts.append(_cyl(rx=0.048, rz=0.048, h=0.24, cx= 0.28, cy=0.64, cz=0.0))

    # ── Neck ──────────────────────────────────────────────────────────
    parts.append(_cyl(rx=0.052, rz=0.052, h=0.10, cx=0.0, cy=1.20, cz=0.0))

    # ── Head ──────────────────────────────────────────────────────────
    parts.append(_ellipsoid(rx=0.11, ry=0.135, rz=0.11, cx=0.0, cy=1.38, cz=0.0))

    body = trimesh.util.concatenate(parts)
    body = trimesh.Trimesh(vertices=body.vertices, faces=body.faces, process=True)
    return body


# ── Primitives ────────────────────────────────────────────────────────

def _cyl(rx, rz, h, cx, cy, cz, sections=20):
    """Elliptic cylinder. cy = bottom center Y."""
    c = creation.cylinder(radius=1.0, height=h, sections=sections)
    # Scale to elliptic cross-section (X and Z radii)
    c.vertices[:, 0] *= rx
    c.vertices[:, 2] *= rz
    # Move so bottom is at cy
    c.vertices[:, 1] += h / 2
    c.vertices[:, 0] += cx
    c.vertices[:, 1] += cy
    c.vertices[:, 2] += cz
    return c


def _sphere(r, cx, cy, cz, subdivisions=3):
    s = creation.icosphere(subdivisions=subdivisions, radius=r)
    s.apply_translation([cx, cy, cz])
    return s


def _ellipsoid(rx, ry, rz, cx, cy, cz, subdivisions=3):
    s = creation.icosphere(subdivisions=subdivisions, radius=1.0)
    s.vertices[:, 0] *= rx
    s.vertices[:, 1] *= ry
    s.vertices[:, 2] *= rz
    s.apply_translation([cx, cy, cz])
    return s
