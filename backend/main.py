from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import os
import tempfile
from pathlib import Path
from typing import Optional
import logging

from utils.file_utils import save_upload_file, cleanup_temp_files

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Persistent output directory for generated models
OUTPUT_DIR = Path(tempfile.gettempdir()) / "3d_models"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="2D to 3D Image Converter API",
    description="Convert 2D images to 3D models using depth estimation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services with fallback
def initialize_services():
    """Initialize services with fallback options"""
    try:
        # Try to import and initialize MiDaS-based processor
        from services.image_processor import ImageProcessor
        image_processor = ImageProcessor()
        logger.info("Using MiDaS-based depth estimation")
        return image_processor
    except ImportError as e:
        logger.warning(f"MiDaS not available: {e}")
        try:
            # Fallback to simple depth estimator
            from services.simple_depth_estimator import SimpleDepthEstimator
            image_processor = SimpleDepthEstimator()
            logger.info("Using simple depth estimation (fallback)")
            return image_processor
        except ImportError as e2:
            logger.error(f"Failed to initialize any depth estimator: {e2}")
            raise RuntimeError("No depth estimation service available")

try:
    from services.model_generator import ModelGenerator
    model_generator = ModelGenerator()
    logger.info("Model generator initialized successfully")
except ImportError as e:
    logger.error(f"Failed to initialize model generator: {e}")
    model_generator = None

# Initialize image processor
image_processor = initialize_services()

@app.get("/")
async def root():
    return {"message": "2D to 3D Image Converter API"}

@app.get("/health")
async def health_check():
    services_status = {
        "image_processor": "ready" if image_processor else "error",
        "model_generator": "ready" if model_generator else "error"
    }
    
    return {
        "status": "healthy" if all(status == "ready" for status in services_status.values()) else "degraded",
        "services": services_status
    }

@app.post("/convert")
async def convert_image_to_3d(
    file: UploadFile = File(...),
    back_file: UploadFile = File(None),
    model_type: str = "mesh",
    quality: str = "medium"
):
    temp_dir = Path(tempfile.mkdtemp())
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        input_path = save_upload_file(file, temp_dir)
        logger.info(f"Processing front image: {input_path}")

        # Optional back image
        back_path = None
        if back_file and back_file.filename:
            back_path = save_upload_file(back_file, temp_dir)
            logger.info(f"Processing back image: {back_path}")

        depth_map = await image_processor.process_image(input_path)

        if model_generator is None:
            raise HTTPException(status_code=500, detail="Model generator not available")

        if model_type == "mesh":
            model_path = await model_generator.generate_mesh(depth_map, input_path, quality, OUTPUT_DIR, back_path)
        elif model_type == "point_cloud":
            model_path = await model_generator.generate_point_cloud(depth_map, quality, OUTPUT_DIR)
        elif model_type == "textured":
            model_path = await model_generator.generate_textured_model(depth_map, input_path, quality, OUTPUT_DIR, back_path)
        else:
            raise HTTPException(status_code=400, detail="Invalid model type")

        file_size = os.path.getsize(model_path)
        file_name = os.path.basename(model_path)

        return {
            "success": True,
            "model_path": str(model_path),
            "file_name": file_name,
            "file_size": file_size,
            "model_type": model_type,
            "quality": quality
        }

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
    finally:
        cleanup_temp_files(temp_dir)

@app.get("/debug/files")
async def list_output_files():
    files = [f.name for f in OUTPUT_DIR.iterdir()] if OUTPUT_DIR.exists() else []
    return {"output_dir": str(OUTPUT_DIR), "files": files}

@app.get("/download/{filename}")
async def download_model(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream',
        headers={"Access-Control-Allow-Origin": "*"}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 