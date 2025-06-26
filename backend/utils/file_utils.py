import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional
import logging
from fastapi import UploadFile

logger = logging.getLogger(__name__)

def save_upload_file(upload_file: UploadFile, destination_dir: Path) -> Path:
    """
    Save an uploaded file to the specified directory
    
    Args:
        upload_file: The uploaded file
        destination_dir: Directory to save the file
        
    Returns:
        Path to the saved file
    """
    try:
        # Create destination directory if it doesn't exist
        destination_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(upload_file.filename).suffix
        unique_filename = f"{tempfile.gettempprefix()}_{os.urandom(8).hex()}{file_extension}"
        file_path = destination_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        logger.info(f"File saved to: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error saving uploaded file: {str(e)}")
        raise RuntimeError(f"Failed to save uploaded file: {str(e)}")

def cleanup_temp_files(temp_dir: Path):
    """
    Clean up temporary files and directories
    
    Args:
        temp_dir: Directory to clean up
    """
    try:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned up temporary directory: {temp_dir}")
    except Exception as e:
        logger.error(f"Error cleaning up temporary files: {str(e)}")

def ensure_directory_exists(directory_path: Path):
    """
    Ensure a directory exists, create it if it doesn't
    
    Args:
        directory_path: Path to the directory
    """
    try:
        directory_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory_path}")
    except Exception as e:
        logger.error(f"Error creating directory: {str(e)}")
        raise RuntimeError(f"Failed to create directory: {str(e)}")

def get_file_size(file_path: Path) -> int:
    """
    Get the size of a file in bytes
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes
    """
    try:
        return os.path.getsize(file_path)
    except Exception as e:
        logger.error(f"Error getting file size: {str(e)}")
        return 0

def is_valid_image_file(file_path: Path) -> bool:
    """
    Check if a file is a valid image
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file is a valid image, False otherwise
    """
    try:
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
        return file_path.suffix.lower() in valid_extensions
    except Exception as e:
        logger.error(f"Error checking file validity: {str(e)}")
        return False

def create_temp_directory() -> Path:
    """
    Create a temporary directory
    
    Returns:
        Path to the created temporary directory
    """
    try:
        temp_dir = Path(tempfile.mkdtemp())
        logger.info(f"Created temporary directory: {temp_dir}")
        return temp_dir
    except Exception as e:
        logger.error(f"Error creating temporary directory: {str(e)}")
        raise RuntimeError(f"Failed to create temporary directory: {str(e)}")

def copy_file_to_destination(source_path: Path, destination_path: Path) -> bool:
    """
    Copy a file to a destination
    
    Args:
        source_path: Path to the source file
        destination_path: Path to the destination
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure destination directory exists
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(source_path, destination_path)
        logger.info(f"File copied from {source_path} to {destination_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error copying file: {str(e)}")
        return False

def get_file_info(file_path: Path) -> dict:
    """
    Get information about a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    try:
        if not file_path.exists():
            return {"error": "File not found"}
        
        stat = file_path.stat()
        return {
            "name": file_path.name,
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "extension": file_path.suffix.lower(),
            "is_valid_image": is_valid_image_file(file_path)
        }
        
    except Exception as e:
        logger.error(f"Error getting file info: {str(e)}")
        return {"error": str(e)}

def cleanup_old_files(directory: Path, max_age_hours: int = 24):
    """
    Clean up files older than specified age
    
    Args:
        directory: Directory to clean
        max_age_hours: Maximum age in hours
    """
    try:
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for file_path in directory.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    logger.info(f"Cleaned up old file: {file_path}")
                    
    except Exception as e:
        logger.error(f"Error cleaning up old files: {str(e)}") 