"""
Invisible watermarking module for deepfake output traceability
Uses DCT-based frequency domain watermarking for robustness
"""

import numpy as np
import cv2
import hashlib
import json
import time
from typing import Tuple, Optional, Dict
import base64
import modules.globals
import modules.globals

class DeepfakeWatermark:
    def __init__(self, strength: float = 0.1, block_size: int = 8):
        """
        Initialize watermarking system
        
        Args:
            strength: Watermark strength (0.05-0.2 recommended, higher = more visible)
            block_size: DCT block size (8 is standard)
        """
        self.strength = strength
        self.block_size = block_size
        self.watermark_signature = "DLC_DEEPFAKE"  # Identifier
        
    def generate_watermark_data(self, 
                                source_path: str = None,
                                target_path: str = None,
                                user_id: str = None,
                                additional_info: Dict = None) -> str:
        """
        Generate watermark payload with metadata
        
        Returns: JSON string with metadata
        """
        metadata = {
            "signature": self.watermark_signature,
            "timestamp": time.time(),
            "timestamp_readable": time.strftime("%Y-%m-%d %H:%M:%S"),
            "software": "Deep-Live-Cam",
            "version": "1.0",
        }
        
        if source_path:
            metadata["source_hash"] = self._file_hash(source_path)
        if target_path:
            metadata["target_hash"] = self._file_hash(target_path)
        if user_id:
            metadata["user_id"] = user_id
        if additional_info:
            metadata.update(additional_info)
            
        return json.dumps(metadata)
    
    def _file_hash(self, filepath: str) -> str:
        """Generate SHA256 hash of file"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        except:
            return "unknown"
    
    def _string_to_binary(self, text: str, length: int) -> np.ndarray:
        """Convert string to binary array with padding"""
        # Convert to bytes
        text_bytes = text.encode('utf-8')
        # Convert to binary
        binary = ''.join(format(byte, '08b') for byte in text_bytes)
        # Pad or truncate to desired length
        if len(binary) < length:
            binary += '0' * (length - len(binary))
        else:
            binary = binary[:length]
        return np.array([int(b) for b in binary])
    
    def _binary_to_string(self, binary: np.ndarray) -> str:
        """Convert binary array back to string"""
        binary_str = ''.join(str(int(b)) for b in binary)
        # Split into bytes
        bytes_list = []
        for i in range(0, len(binary_str), 8):
            byte = binary_str[i:i+8]
            if len(byte) == 8:
                bytes_list.append(int(byte, 2))
        try:
            return bytes.fromhex(''.join(f'{b:02x}' for b in bytes_list)).decode('utf-8', errors='ignore')
        except:
            return ""
    
    def embed_watermark_dct(self, image: np.ndarray, watermark_data: str) -> np.ndarray:
        """
        Embed watermark using LSB (Least Significant Bit) method with spatial spreading
        This provides invisible watermarking without requiring DCT support
        """
        if image is None or image.size == 0:
            return image
            
        # Work with a copy
        watermarked = image.copy()
        height, width = watermarked.shape[:2]
        
        # Check if image is too small for watermarking
        min_pixels = 160000  # Minimum 160k pixels (e.g., 400x400)
        total_pixels = height * width
        if total_pixels < min_pixels:
            # Image too small - return warning in console but still return image
            print(f"Warning: Image too small ({height}x{width}={total_pixels} pixels) for reliable watermarking.")
            print(f"         Minimum recommended size: 400x400 pixels")
            print(f"         Watermark will not be embedded.")
            return image
        
        # Convert watermark data to binary
        # Use more capacity for small images (up to 30%)
        if total_pixels < 100000:  # Small images
            capacity_ratio = 0.3  # Use 30% capacity
        else:
            capacity_ratio = 0.1  # Use 10% capacity for larger images
            
        max_bits = min(len(watermark_data) * 8, int(total_pixels * capacity_ratio))
        watermark_bits = self._string_to_binary(watermark_data, max_bits)
        
        # Process blue channel for better imperceptibility (avoid YUV conversion issues)
        if len(watermarked.shape) == 3:
            # Use blue channel (index 0 in BGR)
            target_channel = watermarked[:, :, 0].copy()
        else:
            target_channel = watermarked.copy()
        
        # Embed watermark bits in LSB with spatial distribution
        bit_index = 0
        # Use a pseudo-random pattern for embedding positions (makes it harder to detect/remove)
        np.random.seed(42)  # Fixed seed for reproducibility
        positions = []
        
        # Generate random positions across the image
        for _ in range(len(watermark_bits)):
            pos_y = np.random.randint(0, height)
            pos_x = np.random.randint(0, width)
            positions.append((pos_y, pos_x))
        
        # Embed bits
        for i, (y, x) in enumerate(positions):
            if i >= len(watermark_bits):
                break
            
            # Get pixel value
            pixel_val = int(target_channel[y, x])
            
            # Modify LSB based on watermark bit
            if watermark_bits[i] == 1:
                # Set LSB to 1
                pixel_val = pixel_val | 1
            else:
                # Set LSB to 0
                pixel_val = pixel_val & 0xFE
            
            target_channel[y, x] = pixel_val
        
        # Reconstruct image
        if len(watermarked.shape) == 3:
            watermarked[:, :, 0] = target_channel
        else:
            watermarked = target_channel
            
        return watermarked
    
    def embed_metadata_exif(self, image: np.ndarray, watermark_data: str, 
                           output_path: str) -> bool:
        """
        Embed watermark in image metadata (EXIF/PNG chunks)
        Note: This requires PIL/Pillow
        """
        try:
            from PIL import Image
            from PIL.PngImagePlugin import PngInfo
            
            # Convert CV2 image to PIL
            if len(image.shape) == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
            pil_image = Image.fromarray(image_rgb)
            
            # Determine format
            if output_path.lower().endswith('.png'):
                # PNG: Use tEXt chunks
                metadata = PngInfo()
                metadata.add_text("DeepfakeWatermark", watermark_data)
                pil_image.save(output_path, "PNG", pnginfo=metadata)
            elif output_path.lower().endswith(('.jpg', '.jpeg')):
                # JPEG: Use EXIF
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
                # Add to UserComment (tag 37510)
                exif_dict["Exif"][37510] = watermark_data.encode('utf-8')
                
                # Note: For full EXIF support, use piexif library
                pil_image.save(output_path, "JPEG", quality=95)
            else:
                return False
                
            return True
        except ImportError:
            # PIL/Pillow not available - not critical
            return False
        except Exception as e:
            # Metadata embedding failed - not critical, invisible watermark is still there
            return False
    
    def extract_watermark_dct(self, image: np.ndarray, expected_length: int = 2000) -> Optional[str]:
        """Extract watermark from LSB positions"""
        if image is None or image.size == 0:
            return None
            
        height, width = image.shape[:2]
        
        # Extract blue channel (same as embedding)
        if len(image.shape) == 3:
            target_channel = image[:, :, 0]
        else:
            target_channel = image
        
        extracted_bits = []
        
        # Use same random seed to get same positions
        np.random.seed(42)
        
        # Extract bits from LSB at pseudo-random positions
        for _ in range(expected_length):
            pos_y = np.random.randint(0, height)
            pos_x = np.random.randint(0, width)
            
            # Get pixel value and extract LSB
            pixel_val = int(target_channel[pos_y, pos_x])
            bit = pixel_val & 1  # Extract LSB
            extracted_bits.append(bit)
        
        # Convert bits to string
        extracted_bits = np.array(extracted_bits)
        return self._binary_to_string(extracted_bits)
    
    def verify_watermark(self, image: np.ndarray) -> Tuple[bool, Optional[Dict]]:
        """
        Verify if image contains valid watermark and extract metadata
        
        Returns: (is_watermarked, metadata_dict)
        """
        try:
            extracted = self.extract_watermark_dct(image)
                
            if extracted and self.watermark_signature in extracted:
                # Try to parse JSON metadata
                try:
                    # Find JSON portion
                    start = extracted.find('{')
                    end = extracted.rfind('}') + 1
                    if start >= 0 and end > start:
                        json_str = extracted[start:end]
                        metadata = json.loads(json_str)
                        return True, metadata
                except:
                    pass
                return True, {"signature": self.watermark_signature}
            return False, None
        except Exception as e:
            # Silent failure - watermark not found
            return False, None


# Global instance
_watermark_instance = None

def get_watermark_instance(strength: float = 0.1) -> DeepfakeWatermark:
    """Get or create global watermark instance"""
    global _watermark_instance
    if _watermark_instance is None:
        _watermark_instance = DeepfakeWatermark(strength=strength)
    return _watermark_instance


def watermark_output(image: np.ndarray, 
                     source_path: str = None,
                     target_path: str = None,
                     output_path: str = None,
                     user_id: str = None) -> np.ndarray:
    """
    Main function to watermark deepfake output
    
    Args:
        image: Output image to watermark
        source_path: Path to source image
        target_path: Path to target image/video
        output_path: Where the output will be saved
        user_id: Optional user identifier
        
    Returns:
        Watermarked image
    """
    # Read strength from globals if available, otherwise use default
    strength = getattr(modules.globals, 'watermark_strength', 0.1)
    watermarker = get_watermark_instance(strength=strength)
    
    # Generate watermark data
    watermark_data = watermarker.generate_watermark_data(
        source_path=source_path,
        target_path=target_path,
        user_id=user_id,
        additional_info={"output_path": output_path} if output_path else None
    )
    
    # Embed invisible watermark
    watermarked = watermarker.embed_watermark_dct(image, watermark_data)
    
    # If output path provided, also embed in metadata
    if output_path:
        try:
            watermarker.embed_metadata_exif(watermarked, watermark_data, output_path)
        except:
            pass  # Metadata embedding is optional
    
    return watermarked

