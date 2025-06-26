# 2D to 3D Image Converter

A web application that converts 2D images to 3D models using advanced depth estimation techniques and machine learning.

## Features

- Upload 2D images via a simple drag-and-drop interface
- Convert images to 3D models with realistic depth
- Three visualization modes:
  - 3D Mesh: Detailed mesh with texture mapping
  - Point Cloud: 3D point cloud representation with depth-based positioning
  - Textured Model: 3D model with normal and displacement mapping
- Multiple quality settings (low, medium, high)
- Download generated 3D models in GLB/PLY format
- Responsive design that works on desktop and mobile
- Real-time processing status updates

## Tech Stack

### Frontend
- React.js with Next.js App Router
- Three.js and React Three Fiber for 3D rendering
- Tailwind CSS for styling
- TypeScript for type safety
- Radix UI components

### Backend
- Python with FastAPI
- PyTorch for ML models
- MiDaS for depth estimation
- OpenCV for image processing
- Trimesh for 3D mesh generation
- PyRender for 3D rendering

## Installation

### Prerequisites

- Python 3.8+ with pip
- Node.js 18+ with npm/pnpm
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/rajeshbakthavachalam/2D-to-3D-Image-Converter.git
   cd 2D-to-3D-Image-Converter
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend server**
   ```bash
   # Option 1: Use the startup script
   python start_backend.py
   
   # Option 2: Run directly
   cd backend
   python run.py
   ```

   The backend API will be available at `http://localhost:8000`
   API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to the frontend directory**
   ```bash
   cd 2d-to-3d-converter
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   pnpm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   # or
   pnpm dev
   ```

   The frontend will be available at `http://localhost:3000`

## Usage

1. **Open the application** in your browser at `http://localhost:3000`

2. **Upload an image** by dragging and dropping or clicking the upload area

3. **Configure conversion options**:
   - **Model Type**: Choose between 3D Mesh, Point Cloud, or Textured Model
   - **Quality**: Select Low (fast), Medium, or High (slow) quality

4. **Click "Convert to 3D"** to start the conversion process

5. **Monitor progress** through the real-time status updates

6. **Download the generated model** once processing is complete

## API Endpoints

### Health Check
- `GET /health` - Check API health and service status

### Image Conversion
- `POST /convert` - Convert 2D image to 3D model
  - Parameters:
    - `file`: Image file (multipart/form-data)
    - `model_type`: Type of 3D model (mesh, point_cloud, textured)
    - `quality`: Quality setting (low, medium, high)

### Model Download
- `GET /download/{filename}` - Download generated 3D model

## Model Types

### 3D Mesh
- Creates a detailed triangular mesh from the depth map
- Includes texture mapping from the original image
- Exported as GLB format
- Best for detailed visualization and 3D printing

### Point Cloud
- Generates a 3D point cloud representation
- Each point represents a pixel with depth information
- Exported as PLY format
- Good for data analysis and processing

### Textured Model
- Creates a 3D model with advanced texturing
- Includes normal mapping for realistic lighting
- Exported as GLB format
- Best for realistic rendering and visualization

## Quality Settings

### Low Quality
- Fastest processing time
- Reduced resolution and mesh complexity
- Suitable for quick previews

### Medium Quality
- Balanced processing time and quality
- Recommended for most use cases
- Good detail preservation

### High Quality
- Slowest processing time
- Maximum resolution and mesh complexity
- Best for final output and detailed analysis

## Troubleshooting

### Common Issues

1. **CUDA/GPU Issues**
   - The application will automatically fall back to CPU if CUDA is not available
   - Processing will be slower but still functional

2. **Memory Issues**
   - Use lower quality settings for large images
   - Ensure sufficient RAM (8GB+ recommended)

3. **Installation Issues**
   - Make sure you're using Python 3.8+
   - Try upgrading pip: `pip install --upgrade pip`
   - For MiDaS installation issues, try: `pip install git+https://github.com/isl-org/MiDaS.git`

4. **Port Conflicts**
   - Backend runs on port 8000 by default
   - Frontend runs on port 3000 by default
   - Change ports in the respective configuration files if needed

### Performance Tips

- Use GPU acceleration if available (CUDA-compatible GPU)
- Process smaller images for faster results
- Use lower quality settings for batch processing
- Close other applications to free up memory

## Development

### Project Structure
```
2D-to-3D-Image-Converter/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── services/           # Business logic
│   │   ├── image_processor.py
│   │   └── model_generator.py
│   └── utils/              # Utility functions
│       └── file_utils.py
├── 2d-to-3d-converter/     # Next.js frontend
│   ├── app/                # App router pages
│   ├── components/         # React components
│   └── lib/                # Utilities and API client
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [MiDaS](https://github.com/isl-org/MiDaS) for depth estimation
- [Trimesh](https://github.com/mikedh/trimesh) for 3D mesh processing
- [Three.js](https://threejs.org/) for 3D rendering
- [Next.js](https://nextjs.org/) for the frontend framework
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework

# Demo Image : 
![image](https://github.com/user-attachments/assets/9ebd4285-8192-4bcb-9130-520d8eacf8c0)



