#!/bin/bash

# Build script for Deep-Live-Cam Docker image

set -e

echo "======================================"
echo "Deep-Live-Cam Docker Build Script"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Warning: docker-compose is not installed. You can still use 'docker run' commands."
    echo "Visit: https://docs.docker.com/compose/install/"
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p models input output temp

# Check for model files
echo ""
echo "Checking for required model files..."
MODELS_MISSING=0

if [ ! -f "models/GFPGANv1.4.pth" ]; then
    echo "  ✗ Missing: GFPGANv1.4.pth"
    MODELS_MISSING=1
else
    echo "  ✓ Found: GFPGANv1.4.pth"
fi

if [ ! -f "models/inswapper_128_fp16.onnx" ]; then
    echo "  ✗ Missing: inswapper_128_fp16.onnx"
    MODELS_MISSING=1
else
    echo "  ✓ Found: inswapper_128_fp16.onnx"
fi

if [ $MODELS_MISSING -eq 1 ]; then
    echo ""
    echo "Warning: Some model files are missing."
    echo "Download them with:"
    echo ""
    echo "  wget -P ./models https://huggingface.co/hacksider/deep-live-cam/resolve/main/GFPGANv1.4.pth"
    echo "  wget -P ./models https://huggingface.co/hacksider/deep-live-cam/resolve/main/inswapper_128_fp16.onnx"
    echo ""
    read -p "Continue building anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build the Docker image
echo ""
echo "Building Docker image (this may take several minutes)..."
echo ""

if command -v docker-compose &> /dev/null; then
    docker-compose build
else
    docker build -t deep-live-cam:cpu .
fi

echo ""
echo "======================================"
echo "Build completed successfully!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Ensure model files are in ./models/"
echo "2. Place input files in ./input/"
echo "3. Run with:"
echo ""
echo "   docker-compose run --rm deep-live-cam \\"
echo "     -s /app/input/source.jpg \\"
echo "     -t /app/input/target.mp4 \\"
echo "     -o /app/output/result.mp4 \\"
echo "     --execution-provider cpu"
echo ""
echo "See README-DOCKER.md for more examples."
echo ""

