import numpy as np
import cv2
import trimesh
import pyrender
import logging
from pathlib import Path
from typing import Tuple, Optional
import tempfile
import os
from PIL import Image
import json

logger = logging.getLogger(__name__)

class ModelGenerator:
    def __init__(self):
        """Initialize the 3D model generator"""
        self.quality_settings = {
            "low": {"resolution": 0.5, "simplification": 0.8},
            "medium": {"resolution": 0.75, "simplification": 0.5},
            "high": {"resolution": 1.0, "simplification": 0.2}
        }
    
    async def generate_mesh(self, depth_map: np.ndarray, texture_path: Path, 
                          quality: str, output_dir: Path) -> Path:
        """
        Generate a 3D mesh from depth map and texture
        
        Args:
            depth_map: Depth map array
            texture_path: Path to the texture image
            quality: Quality setting (low, medium, high)
            output_dir: Directory to save the model
            
        Returns:
            Path to the generated GLB file
        """
        try:
            logger.info(f"Generating mesh with quality: {quality}")
            
            settings = self.quality_settings[quality]
            
            # Create mesh from depth map
            mesh = self._create_mesh_from_depth(depth_map, texture_path, settings)
            
            # Simplify mesh if needed
            if settings["simplification"] < 1.0:
                mesh = self._simplify_mesh(mesh, settings["simplification"])
            
            # Save as GLB
            output_path = output_dir / f"mesh_{quality}.glb"
            mesh.export(str(output_path))
            
            logger.info(f"Mesh saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating mesh: {str(e)}")
            raise RuntimeError(f"Failed to generate mesh: {str(e)}")
    
    async def generate_point_cloud(self, depth_map: np.ndarray, 
                                 quality: str, output_dir: Path) -> Path:
        """
        Generate a point cloud from depth map
        
        Args:
            depth_map: Depth map array
            quality: Quality setting (low, medium, high)
            output_dir: Directory to save the model
            
        Returns:
            Path to the generated PLY file
        """
        try:
            logger.info(f"Generating point cloud with quality: {quality}")
            
            settings = self.quality_settings[quality]
            
            # Create point cloud from depth map
            points = self._create_point_cloud(depth_map, settings)
            
            # Save as PLY
            output_path = output_dir / f"pointcloud_{quality}.ply"
            self._save_point_cloud(points, output_path)
            
            logger.info(f"Point cloud saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating point cloud: {str(e)}")
            raise RuntimeError(f"Failed to generate point cloud: {str(e)}")
    
    async def generate_textured_model(self, depth_map: np.ndarray, 
                                    texture_path: Path, quality: str, 
                                    output_dir: Path) -> Path:
        """
        Generate a textured 3D model with normal and displacement mapping
        
        Args:
            depth_map: Depth map array
            texture_path: Path to the texture image
            quality: Quality setting (low, medium, high)
            output_dir: Directory to save the model
            
        Returns:
            Path to the generated GLB file
        """
        try:
            logger.info(f"Generating textured model with quality: {quality}")
            
            settings = self.quality_settings[quality]
            
            # Create base mesh
            mesh = self._create_mesh_from_depth(depth_map, texture_path, settings)
            
            # Generate normal map
            normal_map = self._generate_normal_map(depth_map)
            
            # Create textured mesh with normal mapping
            textured_mesh = self._apply_normal_mapping(mesh, normal_map, texture_path)
            
            # Save as GLB
            output_path = output_dir / f"textured_{quality}.glb"
            textured_mesh.export(str(output_path))
            
            logger.info(f"Textured model saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating textured model: {str(e)}")
            raise RuntimeError(f"Failed to generate textured model: {str(e)}")
    
    def _create_mesh_from_depth(self, depth_map: np.ndarray, 
                               texture_path: Path, settings: dict) -> trimesh.Trimesh:
        """Create a mesh from depth map using marching cubes"""
        try:
            # Resize depth map based on quality
            h, w = depth_map.shape
            new_h = int(h * settings["resolution"])
            new_w = int(w * settings["resolution"])
            
            if settings["resolution"] != 1.0:
                depth_map = cv2.resize(depth_map, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            
            # Create 3D grid
            x, y = np.meshgrid(np.arange(new_w), np.arange(new_h))
            z = depth_map * 10  # Scale depth for better visualization
            
            # Create vertices
            vertices = np.column_stack([x.flatten(), y.flatten(), z.flatten()])
            
            # Create faces (triangles)
            faces = []
            for i in range(new_h - 1):
                for j in range(new_w - 1):
                    # Create two triangles for each grid cell
                    idx = i * new_w + j
                    faces.append([idx, idx + 1, idx + new_w])
                    faces.append([idx + 1, idx + new_w + 1, idx + new_w])
            
            faces = np.array(faces)
            
            # Create mesh
            mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
            
            # Apply texture if available
            if texture_path.exists():
                mesh = self._apply_texture(mesh, texture_path, new_w, new_h)
            
            return mesh
            
        except Exception as e:
            logger.error(f"Error creating mesh from depth: {str(e)}")
            raise RuntimeError(f"Failed to create mesh from depth: {str(e)}")
    
    def _create_point_cloud(self, depth_map: np.ndarray, settings: dict) -> np.ndarray:
        """Create a point cloud from depth map"""
        try:
            # Resize depth map based on quality
            h, w = depth_map.shape
            new_h = int(h * settings["resolution"])
            new_w = int(w * settings["resolution"])
            
            if settings["resolution"] != 1.0:
                depth_map = cv2.resize(depth_map, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            
            # Create 3D coordinates
            x, y = np.meshgrid(np.arange(new_w), np.arange(new_h))
            z = depth_map * 10  # Scale depth
            
            # Stack coordinates
            points = np.column_stack([x.flatten(), y.flatten(), z.flatten()])
            
            # Remove invalid points (where depth is 0 or NaN)
            valid_mask = (z.flatten() > 0) & ~np.isnan(z.flatten())
            points = points[valid_mask]
            
            return points
            
        except Exception as e:
            logger.error(f"Error creating point cloud: {str(e)}")
            raise RuntimeError(f"Failed to create point cloud: {str(e)}")
    
    def _apply_texture(self, mesh: trimesh.Trimesh, texture_path: Path, 
                      width: int, height: int) -> trimesh.Trimesh:
        """Apply texture to mesh"""
        try:
            # Load texture
            texture_img = Image.open(texture_path)
            texture_img = texture_img.resize((width, height))
            
            # Create texture coordinates
            u = np.linspace(0, 1, width)
            v = np.linspace(0, 1, height)
            u, v = np.meshgrid(u, v)
            
            # Flatten texture coordinates
            tex_coords = np.column_stack([u.flatten(), v.flatten()])
            
            # Apply texture to mesh
            mesh.visual.uv = tex_coords
            mesh.visual.material.image = texture_img
            
            return mesh
            
        except Exception as e:
            logger.error(f"Error applying texture: {str(e)}")
            return mesh  # Return mesh without texture if application fails
    
    def _generate_normal_map(self, depth_map: np.ndarray) -> np.ndarray:
        """Generate normal map from depth map"""
        try:
            # Compute gradients
            grad_x = cv2.Sobel(depth_map, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(depth_map, cv2.CV_64F, 0, 1, ksize=3)
            
            # Create normal map
            normal_map = np.zeros((depth_map.shape[0], depth_map.shape[1], 3))
            normal_map[:, :, 0] = -grad_x
            normal_map[:, :, 1] = -grad_y
            normal_map[:, :, 2] = 1.0
            
            # Normalize
            norm = np.sqrt(np.sum(normal_map**2, axis=2, keepdims=True))
            normal_map = normal_map / (norm + 1e-8)
            
            # Convert to 0-1 range for texture
            normal_map = (normal_map + 1) / 2
            
            return normal_map
            
        except Exception as e:
            logger.error(f"Error generating normal map: {str(e)}")
            # Return default normal map (pointing up)
            return np.ones((depth_map.shape[0], depth_map.shape[1], 3)) * 0.5
    
    def _apply_normal_mapping(self, mesh: trimesh.Trimesh, normal_map: np.ndarray, 
                            texture_path: Path) -> trimesh.Trimesh:
        """Apply normal mapping to mesh"""
        try:
            # This is a simplified implementation
            # In a full implementation, you would modify vertex normals based on the normal map
            
            # For now, just return the mesh with texture
            return self._apply_texture(mesh, texture_path, 
                                     normal_map.shape[1], normal_map.shape[0])
            
        except Exception as e:
            logger.error(f"Error applying normal mapping: {str(e)}")
            return mesh
    
    def _simplify_mesh(self, mesh: trimesh.Trimesh, ratio: float) -> trimesh.Trimesh:
        """Simplify mesh by reducing number of faces"""
        try:
            target_faces = int(len(mesh.faces) * ratio)
            simplified = mesh.simplify_quadratic_decimation(target_faces)
            return simplified
            
        except Exception as e:
            logger.error(f"Error simplifying mesh: {str(e)}")
            return mesh  # Return original mesh if simplification fails
    
    def _save_point_cloud(self, points: np.ndarray, output_path: Path):
        """Save point cloud as PLY file"""
        try:
            # Create PLY header
            header = f"""ply
format ascii 1.0
element vertex {len(points)}
property float x
property float y
property float z
end_header
"""
            
            # Write PLY file
            with open(output_path, 'w') as f:
                f.write(header)
                for point in points:
                    f.write(f"{point[0]} {point[1]} {point[2]}\n")
                    
        except Exception as e:
            logger.error(f"Error saving point cloud: {str(e)}")
            raise RuntimeError(f"Failed to save point cloud: {str(e)}")
    
    def get_model_info(self, model_path: Path) -> dict:
        """Get information about a generated model"""
        try:
            if not model_path.exists():
                return {"error": "Model file not found"}
            
            file_size = os.path.getsize(model_path)
            
            if model_path.suffix.lower() == '.glb':
                # Load mesh and get info
                mesh = trimesh.load(str(model_path))
                return {
                    "type": "mesh",
                    "vertices": len(mesh.vertices),
                    "faces": len(mesh.faces),
                    "file_size": file_size,
                    "bounds": mesh.bounds.tolist()
                }
            elif model_path.suffix.lower() == '.ply':
                # Count points in PLY file
                with open(model_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith('element vertex'):
                            point_count = int(line.split()[-1])
                            break
                
                return {
                    "type": "point_cloud",
                    "points": point_count,
                    "file_size": file_size
                }
            else:
                return {
                    "type": "unknown",
                    "file_size": file_size
                }
                
        except Exception as e:
            logger.error(f"Error getting model info: {str(e)}")
            return {"error": str(e)} 