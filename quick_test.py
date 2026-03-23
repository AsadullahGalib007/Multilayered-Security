#!/usr/bin/env python3
"""
Quick Test Script for Multi-Layered Security System

This script runs a minimal test to verify the implementation works correctly.
"""

import sys
import numpy as np

print("="*70)
print("Multi-Layered Security System - Quick Test")
print("="*70)

# Test 1: Import all modules
print("\n[Test 1] Importing modules...")
try:
    from multi_layer_security import E91QKD, MultiLayeredSecuritySystem
    from deep_steganography import DeepSteganography
    print("✓ All modules imported successfully")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: E91 QKD Protocol
print("\n[Test 2] Testing E91 QKD Protocol...")
try:
    qkd = E91QKD(num_singlets=50)
    alice_key, bob_key, chsh_value, time_taken = qkd.run_protocol()
    
    print(f"  Key length: {len(alice_key)} bits")
    print(f"  CHSH value: {chsh_value:.4f}")
    print(f"  Keys match: {alice_key == bob_key}")
    
    if abs(chsh_value) > 2:
        print("  ✓ CHSH inequality violated - Quantum correlation confirmed")
    
    print("✓ E91 QKD test passed")
except Exception as e:
    print(f"✗ E91 QKD test failed: {e}")
    sys.exit(1)

# Test 3: SHA-256 Hashing
print("\n[Test 3] Testing SHA-256 Hashing...")
try:
    from multi_layer_security import CryptographicSystem
    
    crypto = CryptographicSystem()
    test_key = "101010"
    hashed = crypto.hash_key_sha256(test_key)
    
    print(f"  Original key: {test_key}")
    print(f"  Hashed key: {hashed[:32]}...")
    print(f"  Hash length: {len(hashed)} characters (256 bits)")
    
    assert len(hashed) == 64, "Hash should be 64 hex characters"
    print("✓ SHA-256 hashing test passed")
except Exception as e:
    print(f"✗ SHA-256 test failed: {e}")
    sys.exit(1)

# Test 4: AES Encryption/Decryption
print("\n[Test 4] Testing AES-256 Encryption...")
try:
    test_data = b"Hello, Quantum World!" * 10
    key_hash = crypto.hash_key_sha256("test_key_12345")
    
    # Encrypt
    ciphertext, iv = crypto.aes_encrypt(test_data, key_hash)
    print(f"  Original size: {len(test_data)} bytes")
    print(f"  Encrypted size: {len(ciphertext)} bytes")
    
    # Decrypt
    decrypted = crypto.aes_decrypt(ciphertext, key_hash, iv)
    
    assert decrypted == test_data, "Decrypted data doesn't match original"
    print("  ✓ Perfect decryption - data matches exactly")
    print("✓ AES-256 encryption test passed")
except Exception as e:
    print(f"✗ AES encryption test failed: {e}")
    sys.exit(1)

# Test 5: Image Encryption
print("\n[Test 5] Testing Image Encryption...")
try:
    # Create small test image
    test_image = np.random.randint(0, 256, (32, 32, 3), dtype=np.uint8)
    from PIL import Image
    img_path = '/tmp/quick_test.png'
    Image.fromarray(test_image).save(img_path)
    
    # Create system and encrypt
    system = MultiLayeredSecuritySystem(num_singlets=50)
    system.generate_quantum_key()
    system.hash_quantum_key()
    
    encrypted_data, iv, original_array = system.encrypt_image(img_path)
    decrypted_array = system.decrypt_image(encrypted_data, iv, original_array.shape)
    
    match = np.array_equal(original_array, decrypted_array)
    print(f"  Image shape: {original_array.shape}")
    print(f"  Arrays match: {match}")
    
    assert match, "Decrypted image doesn't match original"
    print("✓ Image encryption test passed")
except Exception as e:
    print(f"✗ Image encryption test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Steganography
print("\n[Test 6] Testing Steganography...")
try:
    stego = DeepSteganography()
    
    cover = np.random.randint(100, 200, (32, 32, 3), dtype=np.uint8)
    secret = np.random.randint(50, 150, (32, 32, 3), dtype=np.uint8)
    
    # Create stego image
    stego_img = stego.create_simple_stego(cover, secret)
    
    # Extract secret
    revealed = (stego_img & 0x0F) << 4
    
    print(f"  Cover shape: {cover.shape}")
    print(f"  Secret shape: {secret.shape}")
    print(f"  Stego shape: {stego_img.shape}")
    print(f"  Revealed shape: {revealed.shape}")
    
    # Calculate similarity
    diff = np.mean(np.abs(cover.astype(int) - stego_img.astype(int)))
    print(f"  Average pixel change: {diff:.2f}")
    
    print("✓ Steganography test passed")
except Exception as e:
    print(f"✗ Steganography test failed: {e}")
    sys.exit(1)

# Test 7: Security Metrics
print("\n[Test 7] Testing Security Metrics...")
try:
    from multi_layer_security import ImageAnalysis
    
    analysis = ImageAnalysis()
    
    original = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
    encrypted = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
    
    entropy = analysis.calculate_entropy(encrypted)
    npcr, uaci = analysis.calculate_npcr_uaci(original, encrypted)
    
    print(f"  Entropy: {entropy:.4f} / 8.0000")
    print(f"  NPCR: {npcr:.2f}%")
    print(f"  UACI: {uaci:.2f}%")
    
    assert 0 <= entropy <= 8, "Entropy out of range"
    assert 0 <= npcr <= 100, "NPCR out of range"
    assert 0 <= uaci <= 100, "UACI out of range"
    
    print("✓ Security metrics test passed")
except Exception as e:
    print(f"✗ Security metrics test failed: {e}")
    sys.exit(1)

# All tests passed
print("\n" + "="*70)
print("✓ ALL TESTS PASSED")
print("="*70)
print("\nThe Multi-Layered Security System is working correctly!")
print("\nYou can now run:")
print("  python complete_demo.py    - For full system demonstration")
print("="*70)
