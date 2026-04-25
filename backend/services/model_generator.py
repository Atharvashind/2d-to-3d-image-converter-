"""
Model generator using TripoSR for proper 3D reconstruction.
"""

import io
import sys
import os
import numpy as np
import logging
import uuid
from pathlib import Path
from PIL import Image

# Add TripoSR to path
TRIPOSR_PATH = Path(__file__).parent.parent.parent / "TripoSR"
if str(TRIPOSR_PATH) not in sys.path:
    sys.path.insert(0, str(TRIPOSR_PATH))

from rembg import remove, new_session
import torch
import trimesh

logger = logging.getLogger(__name__)

_rembg_session = None
_triposr_model = None


def _get_rembg():
    global _rembg_session
    if _rembg_session is None:
        _rembg_session = new_session('u2net')
        logger.info("rembg ready")
    return _rembg_session


def _get_triposr():
    global _triposr_model
    if _triposr_model is None:
        logger.info("Loading TripoSR model...")
        from tsr.system import TSR
        _triposr_model = TSR.from_pretrained(
            "stabilityai/TripoSR",
            config_name="config.yaml",
            weight_name="model.ckpt",
        )
        _triposr_model.renderer.set_chunk_size(131072)
        _triposr_model.to("cpu")
        logger.info("TripoSR model loaded on CPU")
    return _triposr_model


class ModelGenerator:
    def __init__(self):
        # Pre-load TripoSR at startup
        try:
            _get_triposr()
        except Exception as e:
            logger.error(f"TripoSR load failed: {e}")

    async def generate_mesh(self, depth_map, texture_path, quality, output_dir, back_texture_path=None):
        uid = uuid.uuid4().hex[:8]
        out = output_dir / f"mesh_{quality}_{uid}.glb"
        self._run_triposr(texture_path, quality, out)
        return out

    async def generate_textured_model(self, depth_map, texture_path, quality, output_dir, back_texture_path=None):
        uid = uuid.uuid4().hex[:8]
        out = output_dir / f"textured_{quality}_{uid}.glb"
        self._run_triposr(texture_path, quality, out)
        return out

    async def generate_point_cloud(self, depth_map, quality, output_dir):
        # For point cloud, still use depth-based approach
        uid = uuid.uuid4().hex[:8]
        out = output_dir / f"pointcloud_{quality}_{uid}.glb"
        self._run_triposr(None, quality, out)
        return out

    def _run_triposr(self, texture_path: Path, quality: str, output_path: Path):
        """Remove background, run TripoSR, export GLB."""
        resolution_map = {"low": 64, "medium": 128, "high": 256}
        resolution = resolution_map.get(quality, 48)

        # 1. Remove background
        logger.info("Removing background with rembg...")
        with open(texture_path, "rb") as f:
            raw = f.read()
        result = remove(raw, session=_get_rembg())
        img = Image.open(io.BytesIO(result)).convert("RGBA")

        # Resize to 512x512 and composite on neutral grey background
        # (white bg causes TripoSR to wash out colors)
        img = img.resize((512, 512), Image.LANCZOS)
        bg = Image.new("RGB", (512, 512), (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg

        # 2. Run TripoSR
        logger.info(f"Running TripoSR inference (resolution={resolution}, CPU)...")
        model = _get_triposr()

        with torch.no_grad():
            scene_codes = model([img], device="cpu")

        logger.info("Extracting mesh...")
        meshes = model.extract_mesh(scene_codes, has_vertex_color=True, resolution=resolution)
        mesh = meshes[0]

        # Boost vertex color contrast (TripoSR outputs washed-out colors on CPU)
        if hasattr(mesh.visual, 'vertex_colors') and mesh.visual.vertex_colors is not None:
            vc = mesh.visual.vertex_colors.astype(np.float32)
            rgb = vc[:, :3] / 255.0
            # Gamma correction to bring out colors
            rgb = np.power(np.clip(rgb, 0, 1), 0.6)
            vc[:, :3] = (rgb * 255).astype(np.uint8)
            mesh.visual.vertex_colors = vc.astype(np.uint8)

        # 3. Export as GLB
        logger.info(f"Exporting GLB → {output_path}")
        mesh.export(str(output_path))
        logger.info("Done!")
