import cv2
import numpy as np
import torch
from PIL import Image
import logging
from pathlib import Path
from typing import Tuple, Optional
from transformers import pipeline, AutoImageProcessor, AutoModelForDepthEstimation

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        """Initialize the image processor with MiDaS model for depth estimation"""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Load MiDaS model using transformers
        self.model = self._load_midas_model()
        self.image_processor = self._load_image_processor()
        
    def _load_midas_model(self):
        """Load the MiDaS depth estimation model using transformers"""
        try:
            # Use MiDaS v3.1 (DPT-Large) for best quality
            model_name = "Intel/dpt-large"  # Alternative: "facebook/dpt-large-hybrid"
            
            logger.info(f"Loading MiDaS model: {model_name}")
            model = AutoModelForDepthEstimation.from_pretrained(model_name)
            model.to(self.device)
            model.eval()
            
            logger.info(f"Loaded MiDaS model: {model_name}")
            return model
            
        except Exception as e:
            logger.error(f"Error loading MiDaS model: {str(e)}")
            raise RuntimeError(f"Failed to load MiDaS model: {str(e)}")
    
    def _load_image_processor(self):
        """Load the image processor for preprocessing images"""
        try:
            model_name = "Intel/dpt-large"
            image_processor = AutoImageProcessor.from_pretrained(model_name)
            
            logger.info(f"Loaded image processor: {model_name}")
            return image_processor
            
        except Exception as e:
            logger.error(f"Error creating image processor: {str(e)}")
            raise RuntimeError(f"Failed to create image processor: {str(e)}")
    
    async def process_image(self, image_path: Path) -> np.ndarray:
        """
        Process an image and generate a depth map
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Depth map as numpy array
        """
        try:
            logger.info(f"Processing image: {image_path}")
            
            # Load image
            image = Image.open(image_path).convert("RGB")
            original_size = image.size
            
            # Preprocess image
            inputs = self.image_processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Compute depth
            with torch.no_grad():
                outputs = self.model(**inputs)
                predicted_depth = outputs.predicted_depth
                
                # Interpolate to original size
                prediction = torch.nn.functional.interpolate(
                    predicted_depth.unsqueeze(1),
                    size=original_size[::-1],  # PIL size is (width, height), torch expects (height, width)
                    mode="bicubic",
                    align_corners=False,
                )
                depth = prediction.squeeze().cpu().numpy()
            
            # Normalize depth map
            depth = self._normalize_depth(depth)

            # Enhance contrast using CLAHE-style stretch
            depth = self._enhance_contrast(depth)

            logger.info("Depth map generated successfully")
            return depth
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise RuntimeError(f"Failed to process image: {str(e)}")
    
    def _normalize_depth(self, depth: np.ndarray) -> np.ndarray:
        """Normalize depth map to 0-1 range"""
        try:
            # Remove invalid values
            depth = np.nan_to_num(depth, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Normalize to 0-1 range
            if depth.max() > depth.min():
                depth = (depth - depth.min()) / (depth.max() - depth.min())
            
            return depth
            
        except Exception as e:
            logger.error(f"Error normalizing depth: {str(e)}")
            raise RuntimeError(f"Failed to normalize depth: {str(e)}")
    
    def _enhance_contrast(self, depth: np.ndarray) -> np.ndarray:
        """Stretch depth histogram so near/far objects have more separation."""
        try:
            p2, p98 = np.percentile(depth[depth > 0], (2, 98)) if depth.max() > 0 else (0, 1)
            depth = np.clip((depth - p2) / (p98 - p2 + 1e-8), 0, 1)
            return depth.astype(np.float32)
        except Exception:
            return depth

    def enhance_depth_map(self, depth: np.ndarray, method: str = "bilateral") -> np.ndarray:
        """
        Enhance depth map using various filtering techniques
        
        Args:
            depth: Input depth map
            method: Enhancement method (bilateral, gaussian, median)
            
        Returns:
            Enhanced depth map
        """
        try:
            # Convert to uint8 for OpenCV operations
            depth_uint8 = (depth * 255).astype(np.uint8)
            
            if method == "bilateral":
                # Bilateral filter to preserve edges while smoothing
                enhanced = cv2.bilateralFilter(depth_uint8, 9, 75, 75)
            elif method == "gaussian":
                # Gaussian blur
                enhanced = cv2.GaussianBlur(depth_uint8, (5, 5), 0)
            elif method == "median":
                # Median filter to remove noise
                enhanced = cv2.medianBlur(depth_uint8, 5)
            else:
                enhanced = depth_uint8
            
            # Convert back to float
            enhanced = enhanced.astype(np.float32) / 255.0
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing depth map: {str(e)}")
            return depth  # Return original if enhancement fails
    
    def get_depth_statistics(self, depth: np.ndarray) -> dict:
        """Get statistics about the depth map"""
        try:
            valid_depth = depth[depth > 0]
            
            if len(valid_depth) == 0:
                return {
                    "mean": 0.0,
                    "std": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                    "valid_pixels": 0
                }
            
            return {
                "mean": float(np.mean(valid_depth)),
                "std": float(np.std(valid_depth)),
                "min": float(np.min(valid_depth)),
                "max": float(np.max(valid_depth)),
                "valid_pixels": int(len(valid_depth))
            }
            
        except Exception as e:
            logger.error(f"Error computing depth statistics: {str(e)}")
            return {} 