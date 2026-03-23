# Getting Started with Multi-Layered Security System

This implementation replicates the research paper:  
**"Multi-Layered Security System: Integrating Quantum Key Distribution with Classical Cryptography to Enhance Steganographic Security"**

## 📦 Quick Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install qiskit qiskit-aer pycryptodome pillow numpy matplotlib torch
```

### Step 2: Run Quick Test

Verify everything works:
```bash
python quick_test.py
```

You should see:
```
======================================================================
Multi-Layered Security System - Quick Test
======================================================================

[Test 1] Importing modules...
✓ All modules imported successfully

[Test 2] Testing E91 QKD Protocol...
✓ E91 QKD test passed

[Test 3] Testing SHA-256 Hashing...
✓ SHA-256 hashing test passed

... (more tests)

======================================================================
✓ ALL TESTS PASSED
======================================================================
```

### Step 3: Run Complete Demo

```bash
python complete_demo.py
```

This runs the complete workflow:
1. ✓ Creates test images
2. ✓ Generates quantum keys (E91 protocol)
3. ✓ Hashes keys (SHA-256)
4. ✓ Creates steganographic images
5. ✓ Encrypts with AES-256
6. ✓ Decrypts and verifies
7. ✓ Performs security analysis

## 📝 Files Included

| File | Description |
|------|-------------|
| `multi_layer_security.py` | E91 QKD + SHA-256 + AES encryption |
| `deep_steganography.py` | CNN-based steganography networks |
| `complete_demo.py` | Complete system demonstration |
| `quick_test.py` | Quick verification tests |
| `requirements.txt` | Python dependencies |
| `README.md` | Comprehensive documentation |
| `GETTING_STARTED.md` | This file |

## 🎯 Usage Examples

### Example 1: Generate Quantum Key

```python
from multi_layer_security import E91QKD

# Create E91 QKD instance with 250 singlet states
qkd = E91QKD(num_singlets=250)

# Generate shared secret key
alice_key, bob_key, chsh_value, time_taken = qkd.run_protocol()

print(f"Key length: {len(alice_key)} bits")
print(f"CHSH value: {chsh_value:.4f}")

# Check for eavesdropper
if abs(chsh_value) > 2:
    print("✓ Secure - No eavesdropper detected")
else:
    print("⚠ Warning - Possible eavesdropping")
```

### Example 2: Encrypt an Image

```python
from multi_layer_security import MultiLayeredSecuritySystem

# Initialize system
system = MultiLayeredSecuritySystem(num_singlets=500)

# Generate quantum key and hash it
system.generate_quantum_key()
system.hash_quantum_key()

# Encrypt your image
encrypted_data, iv, original = system.encrypt_image('your_image.png')

# Later... decrypt it
decrypted = system.decrypt_image(encrypted_data, iv, original.shape)
```

### Example 3: Hide Secret in Image

```python
from deep_steganography import DeepSteganography
from PIL import Image
import numpy as np

# Create steganography system
stego = DeepSteganography()

# Load images
cover = np.array(Image.open('cover.png'))
secret = np.array(Image.open('secret.png'))

# Hide secret in cover
stego_image = stego.create_simple_stego(cover, secret)

# Save stego image
Image.fromarray(stego_image).save('stego.png')

# Later... reveal secret
revealed = (stego_image & 0x0F) << 4
Image.fromarray(revealed).save('revealed.png')
```

### Example 4: Complete Workflow

```python
from complete_demo import CompleteSecurityDemo

# Create demo system
demo = CompleteSecurityDemo(num_singlets=250)

# Run complete workflow (steganography + QKD + encryption)
results = demo.full_workflow('secret.png', 'cover.png')

# Check results
print(f"Key length: {results['key_length']} bits")
print(f"CHSH value: {results['chsh_value']:.4f}")
print(f"Encryption time: {results['encryption_time']:.5f}s")
print(f"Entropy: {results['security_metrics']['encrypted_entropy']:.4f}")
```

## 🔍 What Each Component Does

### 1. **E91 QKD Protocol** (`multi_layer_security.py`)
- Creates entangled photon pairs (Bell states)
- Alice and Bob measure in different bases
- CHSH test detects eavesdroppers
- Generates shared secret key

### 2. **SHA-256 Hashing** (`multi_layer_security.py`)
- Converts variable-length quantum key to fixed 256 bits
- Provides cryptographic hash for AES key
- Ensures avalanche effect (small input change → large output change)

### 3. **AES-256 Encryption** (`multi_layer_security.py`)
- Industry-standard symmetric encryption
- 256-bit key, 14 rounds
- CBC mode with random IV
- Encrypts steganographic images

### 4. **Deep Steganography** (`deep_steganography.py`)
- Hides secret image inside cover image
- CNN-based networks (preparation, hiding, revealing)
- Simplified LSB method for quick demo
- Full CNN training available for production

## 📊 Expected Performance

Based on the research paper:

**Key Generation:**
- 250 singlets → ~57 bit key in ~5.4 seconds
- 500 singlets → ~106 bit key in ~8.7 seconds

**Encryption:**
- 128×128 image → ~0.001 seconds
- 512×512 image → ~0.003 seconds

**Security Metrics:**
- Entropy: ~7.99/8.00 (nearly perfect randomness)
- NPCR: ~99.6% (pixel change rate)
- UACI: ~55% (intensity change)

## ❓ Common Issues

### Issue 1: "No module named 'qiskit'"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue 2: "CHSH value too low"
**Solution**: This can happen due to quantum simulation noise. Try:
- Increasing number of singlets
- Running multiple times (statistical variation)

### Issue 3: "Decryption fails"
**Solution**: Ensure you're using the exact same key for encryption/decryption
```python
# Wrong:
system1.encrypt_image('image.png')
system2.decrypt_image(...)  # Different system, different key!

# Right:
encrypted, iv, shape = system.encrypt_image('image.png')
decrypted = system.decrypt_image(encrypted, iv, shape)  # Same system
```

### Issue 4: "Images don't match after steganography"
**Solution**: This is expected with LSB method - there's some lossy-ness
- Check PSNR value (should be >30 dB for good quality)
- For perfect recovery, train full CNN networks

## 🚀 Next Steps

1. ✅ Run `quick_test.py` to verify installation
2. ✅ Run `complete_demo.py` to see full system
3. ✅ Read `README.md` for detailed documentation
4. ✅ Experiment with different parameters
5. ✅ Integrate into your own projects

## 📚 Learn More

- **Qiskit Documentation**: https://qiskit.org/documentation/
- **AES Explained**: https://en.wikipedia.org/wiki/Advanced_Encryption_Standard
- **Quantum Entanglement**: https://en.wikipedia.org/wiki/Quantum_entanglement
- **Original Paper**: arXiv:2408.06964v1

## 💡 Tips for Best Results

1. **Use more singlets** for longer keys (but slower)
2. **Check CHSH value** - should be around -2.828 for secure channel
3. **Monitor entropy** - encrypted images should have ~8.0 entropy
4. **Test key sensitivity** - single bit change should completely alter output

## 📞 Support

For issues with this implementation:
1. Check `README.md` for detailed docs
2. Review error messages carefully
3. Ensure all dependencies are installed
4. Try running `quick_test.py` first

---

**Ready to secure your data with quantum cryptography!** 🔐⚛️
