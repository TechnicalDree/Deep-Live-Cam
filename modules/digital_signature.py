"""
Digital Signature System for Deep-Live-Cam
Provides cryptographic signatures for deepfake outputs using RSA/ECDSA
"""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
import base64
import json
import os
from typing import Tuple, Optional, Dict
from pathlib import Path
import hashlib


class DigitalSigner:
    """
    Digital signature system for verifiable authorship and integrity
    Supports both RSA and ECDSA algorithms
    """
    
    def __init__(self, algorithm: str = 'RSA'):
        """
        Initialize digital signer
        
        Args:
            algorithm: 'RSA' or 'ECDSA' (default: RSA)
        """
        self.algorithm = algorithm.upper()
        self.private_key = None
        self.public_key = None
        
        if self.algorithm not in ['RSA', 'ECDSA']:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    def generate_keypair(self, key_size: int = 2048):
        """
        Generate new cryptographic key pair
        
        Args:
            key_size: For RSA, key size in bits (2048, 3072, 4096)
                     For ECDSA, ignored (uses SECP256R1)
        
        Returns:
            Tuple of (private_key, public_key)
        """
        if self.algorithm == 'RSA':
            if key_size not in [2048, 3072, 4096]:
                print(f"Warning: Unusual key size {key_size}. Recommended: 2048, 3072, or 4096")
            
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()
            
        elif self.algorithm == 'ECDSA':
            self.private_key = ec.generate_private_key(
                ec.SECP256R1(),  # NIST P-256 curve
                default_backend()
            )
            self.public_key = self.private_key.public_key()
        
        return self.private_key, self.public_key
    
    def save_private_key(self, filepath: str, password: Optional[str] = None):
        """
        Save private key to file (PEM format)
        
        Args:
            filepath: Path to save key
            password: Optional password to encrypt key
        """
        if self.private_key is None:
            raise ValueError("No private key loaded or generated")
        
        if password:
            encryption = serialization.BestAvailableEncryption(password.encode())
        else:
            encryption = serialization.NoEncryption()
        
        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption
        )
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(pem)
        
        # Set restrictive permissions (owner only)
        os.chmod(filepath, 0o600)
    
    def save_public_key(self, filepath: str):
        """Save public key to file (PEM format)"""
        if self.public_key is None:
            raise ValueError("No public key loaded or generated")
        
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(pem)
    
    def load_private_key(self, filepath: str, password: Optional[str] = None):
        """
        Load private key from file
        
        Args:
            filepath: Path to key file
            password: Password if key is encrypted
        """
        with open(filepath, 'rb') as f:
            pem_data = f.read()
        
        pwd = password.encode() if password else None
        
        self.private_key = serialization.load_pem_private_key(
            pem_data,
            password=pwd,
            backend=default_backend()
        )
        
        # Derive public key from private key
        if self.algorithm == 'RSA':
            self.public_key = self.private_key.public_key()
        elif self.algorithm == 'ECDSA':
            self.public_key = self.private_key.public_key()
    
    def load_public_key(self, filepath: str):
        """Load public key from file"""
        with open(filepath, 'rb') as f:
            pem_data = f.read()
        
        self.public_key = serialization.load_pem_public_key(
            pem_data,
            backend=default_backend()
        )
    
    def sign_data(self, data: bytes, metadata: Optional[Dict] = None) -> str:
        """
        Create digital signature for data
        
        Args:
            data: Raw bytes to sign
            metadata: Optional metadata to include in signature
        
        Returns:
            Base64-encoded signature
        """
        if self.private_key is None:
            raise ValueError("No private key loaded. Cannot sign.")
        
        # Prepare payload: data + metadata
        payload = data
        if metadata:
            # Canonicalize metadata (sorted JSON)
            metadata_bytes = json.dumps(metadata, sort_keys=True).encode()
            payload = data + metadata_bytes
        
        # Create signature based on algorithm
        if self.algorithm == 'RSA':
            signature = self.private_key.sign(
                payload,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        elif self.algorithm == 'ECDSA':
            signature = self.private_key.sign(
                payload,
                ec.ECDSA(hashes.SHA256())
            )
        
        return base64.b64encode(signature).decode('utf-8')
    
    def verify_signature(self, data: bytes, signature_b64: str, 
                        metadata: Optional[Dict] = None) -> bool:
        """
        Verify digital signature
        
        Args:
            data: Original data that was signed
            signature_b64: Base64-encoded signature
            metadata: Metadata that was included in signature
        
        Returns:
            True if signature is valid, False otherwise
        """
        if self.public_key is None:
            raise ValueError("No public key loaded. Cannot verify.")
        
        try:
            signature = base64.b64decode(signature_b64)
            
            # Reconstruct payload
            payload = data
            if metadata:
                metadata_bytes = json.dumps(metadata, sort_keys=True).encode()
                payload = data + metadata_bytes
            
            # Verify based on algorithm
            if self.algorithm == 'RSA':
                self.public_key.verify(
                    signature,
                    payload,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
            elif self.algorithm == 'ECDSA':
                self.public_key.verify(
                    signature,
                    payload,
                    ec.ECDSA(hashes.SHA256())
                )
            
            return True
            
        except InvalidSignature:
            return False
        except Exception as e:
            print(f"Signature verification error: {e}")
            return False
    
    def get_public_key_fingerprint(self) -> str:
        """
        Get fingerprint (hash) of public key for identification
        
        Returns:
            Hex string of SHA256 hash of public key
        """
        if self.public_key is None:
            raise ValueError("No public key loaded")
        
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return hashlib.sha256(pem).hexdigest()[:16]  # First 16 chars


class SignatureManager:
    """
    High-level manager for digital signatures
    Handles signature files, metadata, and verification
    """
    
    @staticmethod
    def create_signature_file(image_path: str, signature: str, 
                             metadata: Dict, public_key_fingerprint: str):
        """
        Create a .sig file alongside the image
        
        Args:
            image_path: Path to the signed image
            signature: Base64-encoded signature
            metadata: Metadata used in signing
            public_key_fingerprint: Fingerprint of signing key
        """
        sig_path = image_path + '.sig'
        
        sig_data = {
            'signature': signature,
            'metadata': metadata,
            'algorithm': 'RSA',  # or detect from signer
            'key_fingerprint': public_key_fingerprint,
            'image_path': os.path.basename(image_path)
        }
        
        with open(sig_path, 'w') as f:
            json.dump(sig_data, f, indent=2)
    
    @staticmethod
    def load_signature_file(sig_path: str) -> Optional[Dict]:
        """Load signature data from .sig file"""
        try:
            with open(sig_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            print(f"Error: Corrupted signature file: {sig_path}")
            return None
    
    @staticmethod
    def verify_image_file(image_path: str, public_key_path: str) -> Tuple[bool, Optional[Dict]]:
        """
        Verify an image file's signature
        
        Args:
            image_path: Path to image
            public_key_path: Path to public key for verification
        
        Returns:
            Tuple of (is_valid, signature_data)
        """
        sig_path = image_path + '.sig'
        
        # Load signature file
        sig_data = SignatureManager.load_signature_file(sig_path)
        if sig_data is None:
            return False, None
        
        # Load image data
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
        except FileNotFoundError:
            print(f"Error: Image file not found: {image_path}")
            return False, sig_data
        
        # Create signer and load public key
        algorithm = sig_data.get('algorithm', 'RSA')
        signer = DigitalSigner(algorithm=algorithm)
        
        try:
            signer.load_public_key(public_key_path)
        except FileNotFoundError:
            print(f"Error: Public key not found: {public_key_path}")
            return False, sig_data
        
        # Verify signature
        is_valid = signer.verify_signature(
            image_data,
            sig_data['signature'],
            sig_data.get('metadata')
        )
        
        return is_valid, sig_data


# Convenience functions
def generate_keypair(output_dir: str = '.', key_name: str = 'signing_key',
                    algorithm: str = 'RSA', key_size: int = 2048,
                    password: Optional[str] = None) -> Tuple[str, str]:
    """
    Generate and save a new keypair
    
    Returns:
        Tuple of (private_key_path, public_key_path)
    """
    signer = DigitalSigner(algorithm=algorithm)
    signer.generate_keypair(key_size=key_size)
    
    private_path = os.path.join(output_dir, f"{key_name}_private.pem")
    public_path = os.path.join(output_dir, f"{key_name}_public.pem")
    
    signer.save_private_key(private_path, password=password)
    signer.save_public_key(public_path)
    
    print(f"✓ Generated {algorithm} keypair:")
    print(f"  Private key: {private_path}")
    print(f"  Public key:  {public_path}")
    print(f"  Fingerprint: {signer.get_public_key_fingerprint()}")
    
    if not password:
        print("\n Warning: Private key is NOT encrypted!")
        print("   Consider using --password for production use.")
    
    return private_path, public_path

