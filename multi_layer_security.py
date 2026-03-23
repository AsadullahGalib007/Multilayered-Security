"""
Multi-Layered Security System: Integrating Quantum Key Distribution 
with Classical Cryptography to Enhance Steganographic Security

Implementation of the research paper by Arman Sykot et al.
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import matplotlib.pyplot as plt
from PIL import Image
import os
import io
import warnings
warnings.filterwarnings('ignore')

class E91QKD:
    """
    Implementation of E91 Quantum Key Distribution Protocol
    Based on entangled photon pairs and CHSH inequality testing
    """
    
    def __init__(self, num_singlets=100):
        """
        Initialize E91 QKD protocol
        
        Args:
            num_singlets: Number of singlet states to generate
        """
        self.num_singlets = num_singlets
        self.simulator = AerSimulator()
        
        # Alice's measurement bases (in radians)
        self.alice_bases = {
            'a1': 0,           # Z basis
            'a2': np.pi/4,     # (X+Z)/√2 basis
            'a3': np.pi/2      # X basis
        }
        
        # Bob's measurement bases (in radians)
        self.bob_bases = {
            'b1': np.pi/4,     # (X+Z)/√2 basis
            'b2': np.pi/2,     # X basis
            'b3': 3*np.pi/4    # (X-Z)/√2 basis
        }
        
    def create_singlet_state(self):
        """
        Create an entangled singlet state |ψ⟩ = 1/√2(|01⟩ - |10⟩)
        
        Returns:
            QuantumCircuit: Circuit creating singlet state
        """
        qr = QuantumRegister(2, 'q')
        cr = ClassicalRegister(2, 'c')
        circuit = QuantumCircuit(qr, cr)
        
        # Create singlet state: |ψ⟩ = 1/√2(|01⟩ - |10⟩)
        circuit.x(qr[0])  # Flip first qubit to |1⟩
        circuit.h(qr[0])  # Create superposition
        circuit.cx(qr[0], qr[1])  # Entangle
        circuit.z(qr[0])  # Phase flip to create singlet
        
        return circuit
    
    def measure_in_basis(self, circuit, qubit_idx, angle):
        """
        Measure qubit in rotated basis
        
        Args:
            circuit: Quantum circuit
            qubit_idx: Index of qubit to measure
            angle: Rotation angle for measurement basis
        """
        # Rotate to measurement basis
        circuit.ry(-2*angle, qubit_idx)
        circuit.measure(qubit_idx, qubit_idx)
        
    def run_protocol(self):
        """
        Execute E91 protocol and generate shared key
        
        Returns:
            tuple: (alice_key, bob_key, chsh_value, key_generation_time)
        """
        import time
        start_time = time.time()
        
        alice_results = []
        bob_results = []
        alice_basis_choices = []
        bob_basis_choices = []
        
        # Generate measurements for all singlet states
        for i in range(self.num_singlets):
            # Randomly choose bases
            alice_basis = np.random.choice(['a1', 'a2', 'a3'])
            bob_basis = np.random.choice(['b1', 'b2', 'b3'])
            
            alice_basis_choices.append(alice_basis)
            bob_basis_choices.append(bob_basis)
            
            # Create singlet state
            circuit = self.create_singlet_state()
            
            # Apply measurements
            self.measure_in_basis(circuit, 0, self.alice_bases[alice_basis])
            self.measure_in_basis(circuit, 1, self.bob_bases[bob_basis])
            
            # Execute circuit
            compiled_circuit = transpile(circuit, self.simulator)
            job = self.simulator.run(compiled_circuit, shots=1)
            result = job.result()
            counts = result.get_counts()
            
            # Get measurement results
            measurement = list(counts.keys())[0]
            alice_results.append(int(measurement[1]))
            bob_results.append(int(measurement[0]))
        
        # Generate key from matching bases (a2, b2 both measure in X basis)
        raw_key_alice = []
        raw_key_bob = []
        
        # Separate results for CHSH test and key generation
        chsh_measurements = {'a1b1': [], 'a1b3': [], 'a3b1': [], 'a3b3': []}
        
        for i in range(self.num_singlets):
            alice_b = alice_basis_choices[i]
            bob_b = bob_basis_choices[i]
            
            # Key generation: when both use compatible bases
            if alice_b == 'a2' and bob_b == 'b2':
                raw_key_alice.append(alice_results[i])
                raw_key_bob.append(bob_results[i])
            
            # CHSH test measurements
            if alice_b == 'a1' and bob_b == 'b1':
                chsh_measurements['a1b1'].append((alice_results[i], bob_results[i]))
            elif alice_b == 'a1' and bob_b == 'b3':
                chsh_measurements['a1b3'].append((alice_results[i], bob_results[i]))
            elif alice_b == 'a3' and bob_b == 'b1':
                chsh_measurements['a3b1'].append((alice_results[i], bob_results[i]))
            elif alice_b == 'a3' and bob_b == 'b3':
                chsh_measurements['a3b3'].append((alice_results[i], bob_results[i]))
        
        # Calculate CHSH value
        chsh_value = self.calculate_chsh(chsh_measurements)
        
        # Convert keys to binary strings
        alice_key = ''.join(map(str, raw_key_alice))
        bob_key = ''.join(map(str, raw_key_bob))
        
        end_time = time.time()
        key_generation_time = end_time - start_time
        
        return alice_key, bob_key, chsh_value, key_generation_time
    
    def calculate_chsh(self, measurements):
        """
        Calculate CHSH inequality value
        E = ⟨a1b1⟩ - ⟨a1b3⟩ + ⟨a3b1⟩ + ⟨a3b3⟩
        
        For quantum systems: E = -2√2 ≈ -2.828
        For classical systems: -2 ≤ E ≤ 2
        
        Args:
            measurements: Dictionary of measurement pairs
            
        Returns:
            float: CHSH value
        """
        def correlation(pairs):
            if len(pairs) == 0:
                return 0
            # Calculate correlation: (+1 if same, -1 if different)
            corr = sum([1 if a == b else -1 for a, b in pairs]) / len(pairs)
            return corr
        
        E_a1b1 = correlation(measurements['a1b1'])
        E_a1b3 = correlation(measurements['a1b3'])
        E_a3b1 = correlation(measurements['a3b1'])
        E_a3b3 = correlation(measurements['a3b3'])
        
        chsh_value = E_a1b1 - E_a1b3 + E_a3b1 + E_a3b3
        
        return chsh_value


class CryptographicSystem:
    """
    Classical cryptographic system using SHA-256 and AES
    """
    
    @staticmethod
    def hash_key_sha256(binary_key):
        """
        Hash binary key using SHA-256
        
        Args:
            binary_key: Binary string key
            
        Returns:
            str: Hexadecimal hash value (256 bits)
        """
        # Convert binary string to bytes
        key_bytes = binary_key.encode('utf-8')
        
        # Compute SHA-256 hash
        hash_object = hashlib.sha256(key_bytes)
        hash_hex = hash_object.hexdigest()
        
        return hash_hex
    
    @staticmethod
    def aes_encrypt(plaintext_data, key_hash):
        """
        Encrypt data using AES-256 in CBC mode
        
        Args:
            plaintext_data: Data to encrypt (bytes)
            key_hash: 256-bit key as hex string
            
        Returns:
            tuple: (ciphertext, iv)
        """
        # Convert hex key to bytes (first 32 bytes for AES-256)
        key = bytes.fromhex(key_hash)[:32]
        
        # Create cipher
        cipher = AES.new(key, AES.MODE_CBC)
        
        # Pad and encrypt
        padded_data = pad(plaintext_data, AES.block_size)
        ciphertext = cipher.encrypt(padded_data)
        
        return ciphertext, cipher.iv
    
    @staticmethod
    def aes_decrypt(ciphertext, key_hash, iv):
        """
        Decrypt data using AES-256 in CBC mode
        
        Args:
            ciphertext: Encrypted data
            key_hash: 256-bit key as hex string
            iv: Initialization vector
            
        Returns:
            bytes: Decrypted data
        """
        # Convert hex key to bytes
        key = bytes.fromhex(key_hash)[:32]
        
        # Create cipher
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Decrypt and unpad
        padded_data = cipher.decrypt(ciphertext)
        plaintext = unpad(padded_data, AES.block_size)
        
        return plaintext


class ImageAnalysis:
    """
    Image analysis tools for security evaluation
    """
    
    @staticmethod
    def calculate_entropy(image_array):
        """
        Calculate Shannon entropy of image
        
        Args:
            image_array: Numpy array of image data
            
        Returns:
            float: Entropy value
        """
        # Flatten image and calculate histogram
        flat_image = image_array.flatten()
        hist, _ = np.histogram(flat_image, bins=256, range=(0, 255))
        
        # Calculate probabilities
        hist = hist / hist.sum()
        
        # Remove zero probabilities
        hist = hist[hist > 0]
        
        # Calculate entropy
        entropy = -np.sum(hist * np.log2(hist))
        
        return entropy
    
    @staticmethod
    def calculate_npcr_uaci(original_image, encrypted_image):
        """
        Calculate NPCR (Number of Pixel Change Rate) and 
        UACI (Unified Average Changing Intensity)
        
        Args:
            original_image: Original image array
            encrypted_image: Encrypted image array
            
        Returns:
            tuple: (npcr, uaci)
        """
        # Ensure same shape
        if original_image.shape != encrypted_image.shape:
            raise ValueError("Images must have same dimensions")
        
        # Calculate D matrix (1 if different, 0 if same)
        D = (original_image != encrypted_image).astype(int)
        
        # Calculate NPCR
        npcr = (np.sum(D) / D.size) * 100
        
        # Calculate UACI
        diff = np.abs(original_image.astype(float) - encrypted_image.astype(float))
        uaci = (np.sum(diff) / (D.size * 255)) * 100
        
        return npcr, uaci


class MultiLayeredSecuritySystem:
    """
    Complete Multi-Layered Security System integrating:
    - E91 QKD Protocol
    - SHA-256 Hashing
    - AES Encryption
    - Image Processing
    """
    
    def __init__(self, num_singlets=500):
        """
        Initialize the multi-layered security system
        
        Args:
            num_singlets: Number of singlet states for E91 protocol
        """
        self.qkd = E91QKD(num_singlets)
        self.crypto = CryptographicSystem()
        self.analysis = ImageAnalysis()
        
        self.shared_key = None
        self.hashed_key = None
        self.chsh_value = None
        
    def generate_quantum_key(self):
        """
        Generate shared key using E91 QKD protocol
        
        Returns:
            dict: Results including key, CHSH value, and timing
        """
        print("Generating quantum key using E91 protocol...")
        alice_key, bob_key, chsh_value, time_taken = self.qkd.run_protocol()
        
        # Verify keys match (they should in simulation)
        key_length = len(alice_key)
        
        print(f"Alice's key length: {len(alice_key)} bits")
        print(f"Bob's key length: {len(bob_key)} bits")
        print(f"Keys match: {alice_key == bob_key}")
        print(f"CHSH value: {chsh_value:.4f}")
        print(f"Key generation time: {time_taken:.4f} seconds")
        print(f"Key generation rate: {key_length/time_taken:.2f} bps")
        
        # Check CHSH inequality
        if abs(chsh_value) > 2:
            print("✓ CHSH inequality violated - Quantum correlation confirmed!")
            print("✓ No eavesdropper detected")
        else:
            print("⚠ Warning: CHSH inequality not violated - Possible eavesdropping!")
        
        self.shared_key = alice_key
        self.chsh_value = chsh_value
        
        return {
            'key': alice_key,
            'key_length': key_length,
            'chsh_value': chsh_value,
            'generation_time': time_taken,
            'generation_rate': key_length/time_taken
        }
    
    def hash_quantum_key(self):
        """
        Hash the quantum key using SHA-256
        
        Returns:
            str: Hashed key (256-bit hex)
        """
        if self.shared_key is None:
            raise ValueError("Must generate quantum key first!")
        
        print("\nHashing quantum key with SHA-256...")
        self.hashed_key = self.crypto.hash_key_sha256(self.shared_key)
        print(f"Original key: {self.shared_key[:50]}..." if len(self.shared_key) > 50 else f"Original key: {self.shared_key}")
        print(f"Hashed key: {self.hashed_key}")
        
        return self.hashed_key
    
    def encrypt_image(self, image_path):
        """
        Encrypt an image using AES with the hashed quantum key
        
        Args:
            image_path: Path to image file
            
        Returns:
            tuple: (encrypted_data, iv, original_image_array)
        """
        if self.hashed_key is None:
            raise ValueError("Must hash quantum key first!")
        
        print(f"\nEncrypting image: {image_path}")
        
        # Load and convert image to bytes
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # Convert to bytes
        img_bytes = img_array.tobytes()
        
        # Encrypt
        import time
        start = time.time()
        encrypted_data, iv = self.crypto.aes_encrypt(img_bytes, self.hashed_key)
        encryption_time = time.time() - start
        
        print(f"Image shape: {img_array.shape}")
        print(f"Encryption time: {encryption_time:.5f} seconds")
        print(f"Original size: {len(img_bytes)} bytes")
        print(f"Encrypted size: {len(encrypted_data)} bytes")
        
        return encrypted_data, iv, img_array
    
    def decrypt_image(self, encrypted_data, iv, shape, mode='RGB'):
        """
        Decrypt image data
        
        Args:
            encrypted_data: Encrypted image bytes
            iv: Initialization vector
            shape: Original image shape
            mode: Image mode (RGB, L, etc.)
            
        Returns:
            numpy.ndarray: Decrypted image array
        """
        if self.hashed_key is None:
            raise ValueError("Must hash quantum key first!")
        
        print("\nDecrypting image...")
        
        import time
        start = time.time()
        decrypted_data = self.crypto.aes_decrypt(encrypted_data, self.hashed_key, iv)
        decryption_time = time.time() - start
        
        # Convert back to array
        img_array = np.frombuffer(decrypted_data, dtype=np.uint8).reshape(shape)
        
        print(f"Decryption time: {decryption_time:.5f} seconds")
        print(f"Decrypted shape: {img_array.shape}")
        
        return img_array
    
    def analyze_encryption_security(self, original_image, encrypted_bytes, image_shape):
        """
        Analyze encryption security metrics
        
        Args:
            original_image: Original image array
            encrypted_bytes: Encrypted data
            image_shape: Shape of image
            
        Returns:
            dict: Security metrics
        """
        print("\n=== Security Analysis ===")
        
        # Create encrypted image array for analysis
        # Truncate or pad to match original size
        target_size = np.prod(image_shape)
        encrypted_array = np.frombuffer(encrypted_bytes[:target_size], dtype=np.uint8)
        
        if len(encrypted_array) < target_size:
            # Pad if necessary
            encrypted_array = np.pad(encrypted_array, 
                                    (0, target_size - len(encrypted_array)), 
                                    mode='constant')
        
        encrypted_image = encrypted_array.reshape(image_shape)
        
        # Calculate entropy
        original_entropy = self.analysis.calculate_entropy(original_image)
        encrypted_entropy = self.analysis.calculate_entropy(encrypted_image)
        
        print(f"Original image entropy: {original_entropy:.4f}")
        print(f"Encrypted image entropy: {encrypted_entropy:.4f}")
        
        # Calculate NPCR and UACI
        npcr, uaci = self.analysis.calculate_npcr_uaci(original_image, encrypted_image)
        
        print(f"NPCR: {npcr:.2f}%")
        print(f"UACI: {uaci:.2f}%")
        
        return {
            'original_entropy': original_entropy,
            'encrypted_entropy': encrypted_entropy,
            'npcr': npcr,
            'uaci': uaci
        }
    
    def demonstrate_key_sensitivity(self, image_path):
        """
        Demonstrate key sensitivity by attempting decryption with altered key
        
        Args:
            image_path: Path to test image
        """
        print("\n=== Key Sensitivity Analysis ===")
        
        # Encrypt image with original key
        encrypted_data, iv, original_array = self.encrypt_image(image_path)
        
        # Save original key
        original_key = self.hashed_key
        
        # Create altered key (flip one bit in binary representation)
        altered_binary_key = self.shared_key[:-1] + ('0' if self.shared_key[-1] == '1' else '1')
        altered_hashed_key = self.crypto.hash_key_sha256(altered_binary_key)
        
        print(f"\nOriginal hashed key: {original_key[:32]}...")
        print(f"Altered hashed key:  {altered_hashed_key[:32]}...")
        
        # Try to decrypt with altered key
        self.hashed_key = altered_hashed_key
        try:
            wrong_decrypted = self.decrypt_image(encrypted_data, iv, original_array.shape)
            print("\n⚠ Decryption succeeded with wrong key (data corrupted)")
            
            # Calculate difference
            diff = np.sum(original_array != wrong_decrypted)
            total_pixels = original_array.size
            print(f"Pixels different: {diff}/{total_pixels} ({100*diff/total_pixels:.2f}%)")
            
        except Exception as e:
            print(f"\n✓ Decryption failed with wrong key: {str(e)}")
        
        # Restore original key
        self.hashed_key = original_key
        
        # Decrypt with correct key
        correct_decrypted = self.decrypt_image(encrypted_data, iv, original_array.shape)
        
        # Verify perfect decryption
        if np.array_equal(original_array, correct_decrypted):
            print("✓ Perfect decryption with correct key")
        else:
            print("⚠ Decryption mismatch")


def create_test_image(size=(64, 64, 3), filename='test_image.png'):
    """
    Create a test image for demonstration
    
    Args:
        size: Image dimensions (height, width, channels)
        filename: Output filename
    """
    # Create a colorful test pattern
    img_array = np.random.randint(0, 256, size, dtype=np.uint8)
    
    # Add some structure
    for i in range(0, size[0], 8):
        for j in range(0, size[1], 8):
            color = np.random.randint(0, 256, 3)
            img_array[i:i+8, j:j+8] = color
    
    img = Image.fromarray(img_array)
    BASE_DIR = os.getcwd()
    save_path = os.path.join(BASE_DIR, f"{filename}")
    img.save(save_path)
    print(f"Created test image: {save_path}")
    
    return save_path


def main():
    """
    Main demonstration of the Multi-Layered Security System
    """
    print("="*70)
    print("Multi-Layered Security System")
    print("Integrating QKD with Classical Cryptography")
    print("="*70)
    
    # Create system with 250 singlet states
    system = MultiLayeredSecuritySystem(num_singlets=250)
    
    # Step 1: Generate Quantum Key using E91 Protocol
    print("\n" + "="*70)
    print("STEP 1: Quantum Key Distribution (E91 Protocol)")
    print("="*70)
    qkd_results = system.generate_quantum_key()
    
    # Step 2: Hash the Quantum Key
    print("\n" + "="*70)
    print("STEP 2: Key Hashing (SHA-256)")
    print("="*70)
    hashed_key = system.hash_quantum_key()
    
    # Step 3: Create and encrypt test image
    print("\n" + "="*70)
    print("STEP 3: Image Encryption (AES-256)")
    print("="*70)
    
    # Create test image
    test_image_path = create_test_image(size=(128, 128, 3), filename='test_image.png')
    
    # Encrypt image
    encrypted_data, iv, original_array = system.encrypt_image(test_image_path)
    
    # Step 4: Security Analysis
    print("\n" + "="*70)
    print("STEP 4: Security Analysis")
    print("="*70)
    metrics = system.analyze_encryption_security(original_array, encrypted_data, original_array.shape)
    
    # Step 5: Decrypt and verify
    print("\n" + "="*70)
    print("STEP 5: Decryption and Verification")
    print("="*70)
    decrypted_array = system.decrypt_image(encrypted_data, iv, original_array.shape)
    
    # Verify perfect decryption
    if np.array_equal(original_array, decrypted_array):
        print("✓ Perfect decryption - original and decrypted images match exactly!")
    else:
        print("⚠ Decryption mismatch")
    
    # Step 6: Key Sensitivity Test
    print("\n" + "="*70)
    print("STEP 6: Key Sensitivity Test")
    print("="*70)
    system.demonstrate_key_sensitivity(test_image_path)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"QKD Key Length: {qkd_results['key_length']} bits")
    print(f"Key Generation Rate: {qkd_results['generation_rate']:.2f} bps")
    print(f"CHSH Value: {qkd_results['chsh_value']:.4f} (Quantum: ~-2.828)")
    print(f"Hashed Key Length: 256 bits (SHA-256)")
    print(f"Encryption: AES-256-CBC")
    print(f"Encrypted Image Entropy: {metrics['encrypted_entropy']:.4f}/8.0")
    print(f"NPCR: {metrics['npcr']:.2f}% (Target: ~99.6%)")
    print(f"UACI: {metrics['uaci']:.2f}% (Target: ~33.4%)")
    print("="*70)
    
    return system, metrics


if __name__ == "__main__":
    system, metrics = main()
    print("\n✓ Multi-Layered Security System demonstration complete!")
