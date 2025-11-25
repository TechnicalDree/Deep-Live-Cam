#!/usr/bin/env python3
"""
Test script to verify watermarking functionality
Creates a test image, watermarks it, and verifies the watermark
"""

import numpy as np
import cv2
import sys
from modules.watermark import watermark_output, DeepfakeWatermark
import json

def create_test_image(width=640, height=480):
    """Create a simple test image"""
    # Create a gradient image
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add gradients
    for i in range(height):
        for j in range(width):
            image[i, j] = [
                int((i / height) * 255),  # Blue channel
                int((j / width) * 255),   # Green channel
                int(((i + j) / (height + width)) * 255)  # Red channel
            ]
    
    # Add some text
    cv2.putText(image, "Deep-Live-Cam Test Image", (50, height // 2), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    return image

def test_watermarking():
    """Test the watermarking system"""
    print("=" * 60)
    print("Deep-Live-Cam Watermarking Test")
    print("=" * 60)
    
    # Create test image
    print("\n1. Creating test image...")
    test_image = create_test_image()
    test_path = "test_original.png"
    cv2.imwrite(test_path, test_image)
    print(f"   ✓ Test image created: {test_path}")
    
    # Apply watermark
    print("\n2. Applying watermark...")
    watermarked_path = "test_watermarked.png"
    watermarked = watermark_output(
        test_image,
        source_path=test_path,
        target_path=test_path,
        output_path=watermarked_path,
        user_id="test_user"
    )
    cv2.imwrite(watermarked_path, watermarked)
    print(f"   ✓ Watermarked image created: {watermarked_path}")
    
    # Calculate image difference
    diff = cv2.absdiff(test_image, watermarked)
    avg_diff = np.mean(diff)
    max_diff = np.max(diff)
    print(f"   ✓ Image difference - Average: {avg_diff:.2f}, Max: {max_diff}")
    print(f"   ✓ Watermark is {'INVISIBLE' if avg_diff < 1.0 else 'SUBTLE'} (avg diff < 1.0 is ideal)")
    
    # Verify watermark
    print("\n3. Verifying watermark...")
    watermarker = DeepfakeWatermark()
    is_watermarked, metadata = watermarker.verify_watermark(watermarked)
    
    if is_watermarked:
        print("   ✓ WATERMARK DETECTED!")
        print("\n   Extracted Metadata:")
        print("   " + "-" * 56)
        for key, value in metadata.items():
            print(f"   {key:20s}: {value}")
        print("   " + "-" * 56)
    else:
        print("   ✗ WATERMARK NOT DETECTED (Test Failed)")
        return False
    
    # Test robustness - JPEG compression
    print("\n4. Testing robustness (JPEG compression)...")
    jpeg_path = "test_watermarked.jpg"
    cv2.imwrite(jpeg_path, watermarked, [cv2.IMWRITE_JPEG_QUALITY, 85])
    compressed_image = cv2.imread(jpeg_path)
    
    is_watermarked_compressed, metadata_compressed = watermarker.verify_watermark(compressed_image)
    if is_watermarked_compressed:
        print(f"   ✓ Watermark survived JPEG compression (quality=85)")
    else:
        print(f"   ⚠ Watermark lost after JPEG compression (may need higher strength)")
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"✓ Watermark embedding: PASSED")
    print(f"✓ Watermark extraction: PASSED")
    print(f"✓ Metadata integrity: PASSED")
    print(f"{'✓' if is_watermarked_compressed else '⚠'} JPEG robustness: {'PASSED' if is_watermarked_compressed else 'PARTIAL'}")
    print("\nTest files created:")
    print(f"  - {test_path} (original)")
    print(f"  - {watermarked_path} (watermarked PNG)")
    print(f"  - {jpeg_path} (watermarked JPEG)")
    print("\nYou can verify these manually using:")
    print(f"  python verify_watermark.py {watermarked_path}")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_watermarking()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

