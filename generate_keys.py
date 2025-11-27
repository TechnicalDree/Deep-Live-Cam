#!/usr/bin/env python3
"""
Key Generation Tool for Deep-Live-Cam Digital Signatures
Generates RSA or ECDSA keypairs for signing deepfake outputs
"""

import argparse
import sys
import getpass
from pathlib import Path
from modules.digital_signature import generate_keypair


def main():
    parser = argparse.ArgumentParser(
        description="Generate cryptographic keypair for signing deepfake outputs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate default RSA 2048-bit keypair
  python generate_keys.py

  # Generate with custom name and location
  python generate_keys.py --output keys/ --name my_signing_key

  # Generate with password protection (recommended)
  python generate_keys.py --password

  # Generate stronger 4096-bit RSA key
  python generate_keys.py --key-size 4096

  # Generate ECDSA key (faster, smaller)
  python generate_keys.py --algorithm ECDSA

Security Notes:
  - Keep your private key SECRET and SECURE
  - Share your public key freely for verification
  - Use password protection for production environments
  - Backup your private key in a secure location
        """
    )
    
    parser.add_argument(
        '--output', '-o',
        default='keys',
        help='Output directory for keys (default: keys/)'
    )
    
    parser.add_argument(
        '--name', '-n',
        default='signing_key',
        help='Base name for key files (default: signing_key)'
    )
    
    parser.add_argument(
        '--algorithm', '-a',
        choices=['RSA', 'ECDSA'],
        default='RSA',
        help='Signature algorithm (default: RSA)'
    )
    
    parser.add_argument(
        '--key-size', '-s',
        type=int,
        default=2048,
        choices=[2048, 3072, 4096],
        help='RSA key size in bits (default: 2048, only for RSA)'
    )
    
    parser.add_argument(
        '--password', '-p',
        action='store_true',
        help='Prompt for password to encrypt private key (recommended)'
    )
    
    parser.add_argument(
        '--password-stdin',
        action='store_true',
        help='Read password from stdin (for automation)'
    )
    
    args = parser.parse_args()
    
    # Get password if requested
    password = None
    if args.password:
        password = getpass.getpass("Enter password to encrypt private key: ")
        password_confirm = getpass.getpass("Confirm password: ")
        
        if password != password_confirm:
            print("Error: Passwords do not match!", file=sys.stderr)
            return 1
        
        if len(password) < 8:
            print("Warning: Password is short. Consider using at least 8 characters.")
    
    elif args.password_stdin:
        password = sys.stdin.readline().strip()
    
    # Create output directory
    Path(args.output).mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("Deep-Live-Cam Key Generation")
    print("="*60)
    print(f"Algorithm: {args.algorithm}")
    if args.algorithm == 'RSA':
        print(f"Key size:  {args.key_size} bits")
    print(f"Output:    {args.output}/")
    print(f"Base name: {args.name}")
    print(f"Encrypted: {'Yes' if password else 'No'}")
    print()
    
    try:
        # Generate keypair
        private_path, public_path = generate_keypair(
            output_dir=args.output,
            key_name=args.name,
            algorithm=args.algorithm,
            key_size=args.key_size,
            password=password
        )
        
        print()
        print("="*60)
        print("✓ Keypair generated successfully!")
        print("="*60)
        print()
        print("Next steps:")
        print(f"  1. Keep {private_path} PRIVATE and SECURE")
        print(f"  2. Share {public_path} for verification")
        print(f"  3. Use with: --private-key {private_path}")
        print()
        print("To sign deepfakes:")
        print(f"  python run.py -s source.jpg -t target.jpg -o output.jpg \\")
        print(f"    --sign --private-key {private_path}")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error generating keypair: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

