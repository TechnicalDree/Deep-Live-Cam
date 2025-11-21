#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Deep-Live-Cam Docker Container ===${NC}"
echo "Version: 2.0c (CPU-only)"
echo ""

# Check if models directory exists and has required models
MODELS_DIR="/app/models"
REQUIRED_MODELS=("GFPGANv1.4.pth" "inswapper_128_fp16.onnx")
MISSING_MODELS=()

echo "Checking for required models..."
for model in "${REQUIRED_MODELS[@]}"; do
    if [ ! -f "$MODELS_DIR/$model" ]; then
        MISSING_MODELS+=("$model")
    else
        echo -e "  ${GREEN}✓${NC} Found: $model"
    fi
done

# If models are missing, print instructions
if [ ${#MISSING_MODELS[@]} -gt 0 ]; then
    echo -e "\n${YELLOW}Warning: Missing required models:${NC}"
    for model in "${MISSING_MODELS[@]}"; do
        echo -e "  ${RED}✗${NC} $model"
    done
    echo -e "\n${YELLOW}Please download the required models:${NC}"
    echo "  1. GFPGANv1.4.pth from:"
    echo "     https://huggingface.co/hacksider/deep-live-cam/resolve/main/GFPGANv1.4.pth"
    echo "  2. inswapper_128_fp16.onnx from:"
    echo "     https://huggingface.co/hacksider/deep-live-cam/resolve/main/inswapper_128_fp16.onnx"
    echo ""
    echo "Place them in the ./models directory on your host machine."
    echo ""
fi

# Create output directory if it doesn't exist
mkdir -p /app/output /app/temp

# Execute the command
echo -e "\n${GREEN}Starting Deep-Live-Cam...${NC}"
echo "Command: python run.py $@"
echo ""

exec python run.py "$@"

