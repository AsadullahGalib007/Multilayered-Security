# Multi-Layered Security System

Implementation of the research paper:  
**"Multi-Layered Security System: Integrating Quantum Key Distribution with Classical Cryptography to Enhance Steganographic Security"**  
by Arman Sykot, Md Shawmoon Azad, Wahida Rahman Tanha, BM Monjur Morshed, Syed Emad Uddin Shubha, and M.R.C. Mahdy

## Overview

This implementation demonstrates a novel cryptographic system that combines:

1. **Quantum Key Distribution (QKD)** using the E91 protocol
2. **Classical Hash Function** (SHA-256) for key processing
3. **Symmetric Encryption** (AES-256) for data protection
4. **Deep Steganography** for hiding encrypted data in images

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPLETE WORKFLOW                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. STEGANOGRAPHY                                           │
│     Secret Image + Cover Image → Stego Image                │
│                                                              │
│  2. QUANTUM KEY DISTRIBUTION (E91)                          │
│     Entangled Photon Pairs → Shared Secret Key              │
│     ↓ CHSH Test (Eavesdropper Detection)                   │
│                                                              │
│  3. KEY HASHING (SHA-256)                                   │
│     Secret Key → Fixed-Length Hashed Key (256 bits)         │
│                                                              │
│  4. ENCRYPTION (AES-256-CBC)                                │
│     Stego Image + Hashed Key → Encrypted Image              │
│                                                              │
│  5. CLASSICAL CHANNEL TRANSMISSION                          │
│     Encrypted Image → [Network] → Encrypted Image           │
│                                                              │
│  6. DECRYPTION (AES-256-CBC)                                │
│     Encrypted Image + Hashed Key → Stego Image              │
│                                                              │
│  7. REVEAL SECRET                                           │
│     Stego Image → Secret Image                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. E91 QKD Protocol (`multi_layer_security.py`)

The E91 protocol uses quantum entanglement to create a shared secret key:

- **Singlet States**: Creates Bell states |ψ⟩ = 1/√2(|01⟩ - |10⟩)
- **Measurement Bases**:
  - Alice: Z, (X+Z)/√2, X (angles: 0, π/4, π/2)
  - Bob: (X+Z)/√2, X, (X-Z)/√2 (angles: π/4, π/2, 3π/4)
- **CHSH Inequality Test**: Detects eavesdropping
  - E = ⟨a₁b₁⟩ - ⟨a₁b₃⟩ + ⟨a₃b₁⟩ + ⟨a₃b₃⟩
  - Quantum: E ≈ -2√2 ≈ -2.828
  - Classical: -2 ≤ E ≤ 2

### 2. SHA-256 Hashing

Converts variable-length quantum key to fixed 256-bit hash:

```
Binary Key → SHA-256 → 256-bit Hexadecimal Hash
```

### 3. AES-256 Encryption

Uses the hashed key for symmetric encryption:

- **Mode**: CBC (Cipher Block Chaining)
- **Key Size**: 256 bits
- **Block Size**: 128 bits
- **Rounds**: 14 rounds

### 4. Deep Steganography (`deep_steganography.py`)

CNN-based image hiding:

- **Preparation Network**: Prepares secret image (3→50 channels)
- **Hiding Network**: Embeds prepared secret in cover (53→3 channels)
- **Reveal Network**: Extracts secret from stego (3→3 channels)

Loss function: L = ||cover - stego|| + β||secret - revealed||

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install manually
pip install qiskit qiskit-aer pycryptodome torch pillow numpy matplotlib
```

## Usage

### Quick Start - Complete Demo

Run the complete multi-layered security system:

```bash
python complete_demo.py
```

This will:

1. Generate quantum keys using E91 protocol
2. Hash keys with SHA-256
3. Create steganographic images
4. Encrypt and decrypt data
5. Perform security analysis
6. Generate performance tables

### Individual Components

#### 1. E91 QKD Protocol Only

```python
from multi_layer_security import E91QKD

# Create QKD instance
qkd = E91QKD(num_singlets=250)

# Generate shared key
alice_key, bob_key, chsh_value, time_taken = qkd.run_protocol()

print(f"Key length: {len(alice_key)} bits")
print(f"CHSH value: {chsh_value:.4f}")
print(f"Eavesdropper detected: {abs(chsh_value) <= 2}")
```

#### 2. Complete Security System

```python
from multi_layer_security import MultiLayeredSecuritySystem

# Initialize system
system = MultiLayeredSecuritySystem(num_singlets=500)

# Generate and hash quantum key
qkd_results = system.generate_quantum_key()
hashed_key = system.hash_quantum_key()

# Encrypt image
encrypted_data, iv, original_array = system.encrypt_image('image.png')

# Decrypt image
decrypted_array = system.decrypt_image(encrypted_data, iv, original_array.shape)

# Security analysis
metrics = system.analyze_encryption_security(original_array, encrypted_data, original_array.shape)
```

#### 3. Deep Steganography Only

```python
from deep_steganography import DeepSteganography
import numpy as np

# Create steganography system
stego = DeepSteganography()

# Create or load images
cover = np.random.randint(0, 256, (128, 128, 3), dtype=np.uint8)
secret = np.random.randint(0, 256, (128, 128, 3), dtype=np.uint8)

# Hide secret in cover
stego_image = stego.create_simple_stego(cover, secret)

# Reveal secret
revealed = (stego_image & 0x0F) << 4
```

## Performance Metrics

Based on the paper's experimental results:

### Key Generation Rate (E91 Protocol)

| Singlet States | Key Length | Time (s) | Rate (bps) |
| -------------- | ---------- | -------- | ---------- |
| 25             | 7          | 4.39     | 1.59       |
| 100            | 25         | 4.66     | 5.37       |
| 250            | 57         | 5.42     | 10.52      |
| 500            | 106        | 8.66     | 12.24      |

### Entropy Analysis

| Image Size | Target Entropy | Typical Result |
| ---------- | -------------- | -------------- |
| 64×64      | 8.0000         | 7.9842         |
| 128×128    | 8.0000         | 7.9894         |
| 256×256    | 8.0000         | 7.9986         |
| 512×512    | 8.0000         | 7.9995         |

### Security Metrics

| Metric | Target Value | Typical Result |
| ------ | ------------ | -------------- |
| NPCR   | ~99.6%       | 99.5-99.8%     |
| UACI   | ~33.4%       | 54.4-57.7%     |

### Encryption Performance

| Image Size | Encryption Time | Decryption Time |
| ---------- | --------------- | --------------- |
| 64×64      | 0.00098 s       | 0.00100 s       |
| 128×128    | 0.00100 s       | 0.00001 s       |
| 256×256    | 0.00100 s       | 0.00200 s       |
| 512×512    | 0.00300 s       | 0.00399 s       |

## Security Analysis

### 1. Quantum Security (E91 Protocol)

- **Entanglement-based**: Uses Bell states for quantum correlation
- **Eavesdropper Detection**: CHSH inequality violation indicates secure channel
- **Information-Theoretic Security**: Based on laws of quantum mechanics

### 2. Classical Security

- **SHA-256**: Provides 256-bit hash with strong collision resistance
- **AES-256**: Industry-standard symmetric encryption
- **Key Sensitivity**: Single bit change completely alters output

### 3. Steganographic Security

- **Hidden Transmission**: Secret embedded within innocuous cover image
- **Multiple Layers**: Encryption + Steganography = Defense in Depth

## Mathematical Foundations

### E91 Protocol

**Bell State (Singlet)**:

```
|ψ⁻⟩ = 1/√2(|01⟩ - |10⟩)
```

**CHSH Inequality**:

```
E = ⟨a₁b₁⟩ - ⟨a₁b₃⟩ + ⟨a₃b₁⟩ + ⟨a₃b₃⟩
```

**Security Condition**:

- No eavesdropper: |E| > 2 (typically ≈ 2.828)
- Eavesdropper present: |E| ≤ 2

### SHA-256

**Hash Function**:

```
H(x) = SHA-256(x)
Output: 256-bit hexadecimal string
```

Properties:

- Deterministic
- Quick computation
- Avalanche effect
- Collision resistance

### AES-256

**Encryption**:

```
C = AESₑₙ𝒸ᵣᵧₚₜ(P, K)
```

**Decryption**:

```
P = AESᵢₑ𝒸ᵣᵧₚₜ(C, K)
```

Where:

- P = Plaintext
- C = Ciphertext
- K = 256-bit key

### Deep Steganography

**Loss Function**:

```
L(c, c′, s, s′) = ||c - c′|| + β||s - s′||
```

Where:

- c = cover image
- c′ = stego image
- s = secret image
- s′ = revealed secret
- β = trade-off parameter

## File Structure

```
.
├── multi_layer_security.py    # Main QKD + Crypto implementation
├── deep_steganography.py      # CNN-based steganography
├── complete_demo.py            # Complete system demonstration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── Output Files (generated):
├── test_image.png             # Test images
├── secret_image.png           # Secret to hide
├── cover_image.png            # Cover image
├── stego_image.png            # Steganographic image
└── revealed_secret.png        # Revealed secret
```

## Key Features

✓ **E91 QKD Protocol**: Quantum-secure key generation  
✓ **CHSH Test**: Eavesdropper detection  
✓ **SHA-256**: Cryptographic hashing  
✓ **AES-256-CBC**: Strong encryption  
✓ **Deep Steganography**: CNN-based image hiding  
✓ **Security Analysis**: Entropy, NPCR, UACI metrics  
✓ **Key Sensitivity**: Demonstrates avalanche effect  
✓ **Complete Workflow**: End-to-end demonstration

## Limitations

1. **Simulation Environment**: Uses Qiskit simulator, not real quantum hardware
2. **Simplified Steganography**: LSB method used instead of full CNN training
3. **No Network Layer**: Classical channel transmission is simulated
4. **Key Distribution**: ~25% of qubits used for key, 75% for CHSH test
5. **Performance**: Quantum simulation is slower than real hardware

## Future Enhancements

- [ ] Integration with real quantum hardware (IBM Quantum)
- [ ] Full deep learning training for steganography networks
- [ ] Network protocol implementation
- [ ] Error correction and privacy amplification
- [ ] Multi-party QKD protocols
- [ ] Advanced noise models
- [ ] GUI interface

## Research Paper Details

**Title**: Multi-Layered Security System: Integrating Quantum Key Distribution with Classical Cryptography to Enhance Steganographic Security

**Authors**: Arman Sykot, Md Shawmoon Azad, Wahida Rahman Tanha, BM Monjur Morshed, Syed Emad Uddin Shubha, M.R.C. Mahdy

**Institution**: Department of Electrical and Computer Engineering, North South University, Dhaka, Bangladesh

**arXiv**: 2408.06964v1 [quant-ph] 13 Aug 2024

## Citation

If you use this implementation, please cite the original paper:

```bibtex
@article{sykot2024multilayered,
  title={Multi-Layered Security System: Integrating Quantum Key Distribution with Classical Cryptography to Enhance Steganographic Security},
  author={Sykot, Arman and Azad, Md Shawmoon and Tanha, Wahida Rahman and Morshed, BM Monjur and Shubha, Syed Emad Uddin and Mahdy, M.R.C.},
  journal={arXiv preprint arXiv:2408.06964},
  year={2024}
}
```

## License

This implementation is provided for educational and research purposes.

## Contact

For questions or issues with this implementation, please open an issue on the repository.

## Acknowledgments

- Original research by Arman Sykot et al.
- Qiskit by IBM Quantum
- PyTorch for deep learning
- PyCryptodome for cryptographic primitives

---

# **Note**: This is an educational implementation demonstrating the concepts from the research paper. For production use, additional security measures and optimizations would be required.
