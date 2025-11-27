#!/usr/bin/env python3
"""
Digital Signature Verification Tool for Deep-Live-Cam
Verifies cryptographic signatures on deepfake outputs
"""

import sys
import argparse
from pathlib import Path
from modules.digital_signature import SignatureManager
import json


def verify_signature(image_path: str, public_key_path: str, verbose: bool = False):
    """Verify digital signature on an image"""
    
    print(f"Verifying: {image_path}")
    print("-" * 60)
    
    # Check if image exists
    if not Path(image_path).exists():
        print(f"✗ Error: Image file not found: {image_path}")
        return False
    
    # Check if signature file exists
    sig_path = image_path + '.sig'
    if not Path(sig_path).exists():
        print(f"✗ No signature file found: {sig_path}")
        print(f"  This image is not digitally signed.")
        return False
    
    # Check if public key exists
    if not Path(public_key_path).exists():
        print(f"✗ Error: Public key not found: {public_key_path}")
        return False
    
    # Verify signature
    is_valid, sig_data = SignatureManager.verify_image_file(image_path, public_key_path)
    
    if is_valid:
        print("✓ SIGNATURE VALID")
        print()
        print("Digital Signature Information:")
        print("-" * 60)
        
        if sig_data:
            print(f"  Algorithm:       {sig_data.get('algorithm', 'Unknown')}")
            print(f"  Key Fingerprint: {sig_data.get('key_fingerprint', 'Unknown')}")
            
            if verbose and 'metadata' in sig_data:
                print()
                print("  Metadata:")
                metadata = sig_data['metadata']
                for key, value in metadata.items():
                    if key not in ['signature', 'key_fingerprint']:
                        print(f"    {key}: {value}")
        
        print()
        print("=" * 60)
        print("This image is cryptographically verified!")
        print("Authenticity: ✓ | Integrity: ✓ | Non-repudiation: ✓")
        print("=" * 60)
        return True
        
    else:
        print("SIGNATURE INVALID")
        print()
        print("WARNING: Signature verification failed!")
        print()
        print("Possible reasons:")
        print("  • Image has been modified after signing")
        print("  • Signature file has been tampered with")
        print("  • Wrong public key used for verification")
        print("  • Signature is corrupted")
        print()
        print("=" * 60)
        print("DO NOT TRUST THIS IMAGE")
        print("=" * 60)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Verify digital signatures on deepfake outputs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify with public key
  python verify_signature.py output.jpg --public-key keys/signing_key_public.pem

  # Verify with verbose output
  python verify_signature.py output.jpg --public-key keys/signing_key_public.pem --verbose

  # Batch verify multiple images
  python verify_signature.py image1.jpg image2.jpg --public-key keys/signing_key_public.pem

Notes:
  - The .sig file must be present alongside the image
  - You need the public key that corresponds to the private key used for signing
  - Signature verification ensures:
    ✓ Authenticity (who created it)
    ✓ Integrity (hasn't been modified)
    ✓ Non-repudiation (creator cannot deny it)
        """
    )
    
    parser.add_argument(
        'images',
        nargs='+',
        help='Image file(s) to verify'
    )
    
    parser.add_argument(
        '--public-key', '-k',
        required=True,
        help='Path to public key for verification'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed metadata'
    )
    
    args = parser.parse_args()
    
    # Verify each image
    results = []
    for image_path in args.images:
        if len(args.images) > 1:
            print()
        
        is_valid = verify_signature(image_path, args.public_key, args.verbose)
        results.append((image_path, is_valid))
        
        if len(args.images) > 1:
            print()
    
    # Summary for multiple images
    if len(args.images) > 1:
        print()
        print("=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        
        valid_count = sum(1 for _, valid in results if valid)
        invalid_count = len(results) - valid_count
        
        print(f"Total images:   {len(results)}")
        print(f"Valid:          {valid_count} ✓")
        print(f"Invalid:        {invalid_count} ✗")
        print()
        
        if invalid_count > 0:
            print("Invalid images:")
            for path, valid in results:
                if not valid:
                    print(f"  ✗ {path}")
            print()
            return 1
    
    # Return exit code
    return 0 if all(valid for _, valid in results) else 1


if __name__ == '__main__':
    sys.exit(main())

