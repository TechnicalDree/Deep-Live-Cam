#!/usr/bin/env python3
"""
Utility to verify and extract watermarks from deepfake outputs
"""

import sys
import cv2
import argparse
from modules.watermark import DeepfakeWatermark
import json

def verify_image(image_path: str):
    """Verify if image contains watermark"""
    print(f"Checking: {image_path}")
    print("-" * 50)
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image")
        return
    
    # Create watermark instance
    watermarker = DeepfakeWatermark()
    
    # Verify watermark
    is_watermarked, metadata = watermarker.verify_watermark(image)
    
    if is_watermarked:
        print("✓ WATERMARK DETECTED")
        print("\nExtracted Metadata:")
        print(json.dumps(metadata, indent=2))
        print("\n" + "=" * 50)
        print("This is a confirmed deepfake from Deep-Live-Cam")
        print("=" * 50)
    else:
        print("✗ NO WATERMARK DETECTED")
        print("\nThis image may not be from Deep-Live-Cam or")
        print("the watermark was removed/corrupted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify deepfake watermarks")
    parser.add_argument("image", help="Path to image file to verify")
    args = parser.parse_args()
    
    verify_image(args.image)

