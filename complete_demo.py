"""
Complete Multi-Layered Security System Demonstration
Integrating E91 QKD + SHA-256 + AES + Deep Steganography

Using standard test images (Lena, Baboon, etc.) for reproducibility
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import time
import sys
import os
import shutil
import json
from datetime import datetime

# Import our custom modules
from multi_layer_security import (
    E91QKD, 
    CryptographicSystem, 
    ImageAnalysis,
    MultiLayeredSecuritySystem,
)
from deep_steganography import DeepSteganography


def download_standard_image(image_name='lena', size=(512, 512)):
    """
    Download or use standard test images
    
    Args:
        image_name: Name of image ('lena', 'baboon', 'peppers', 'airplane', 'boat')
        size: Desired size (will resize if needed)
    
    Returns:
        str: Path to saved image
    """
    try:
        # Try to use scikit-image standard images
        from skimage import data
        from skimage.transform import resize
        
        image_map = {
            'camera': data.camera,
            'astronaut': data.astronaut,
            'coffee': data.coffee,
            'chelsea': data.chelsea,  # cat
            'rocket': data.rocket,
        }
        
        if image_name in image_map:
            img_array = image_map[image_name]()
            
            # Convert to RGB if grayscale
            if len(img_array.shape) == 2:
                img_array = np.stack([img_array] * 3, axis=-1)
            
            # Resize if needed
            if img_array.shape[:2] != size:
                img_array = (resize(img_array, size, anti_aliasing=True) * 255).astype(np.uint8)
            
            # Save
            filename = f'{image_name}_{size[0]}x{size[1]}.png'
            Image.fromarray(img_array).save(filename)
            print(f"✓ Loaded standard image: {image_name}")
            return filename
            
    except ImportError:
        print("Note: scikit-image not available, using manual download method")
    
    # Alternative: Download from USC-SIPI database or use PIL
    try:
        import urllib.request
        
        # USC-SIPI Image Database URLs
        urls = {
            'lena': 'https://sipi.usc.edu/database/download.php?vol=misc&img=4.2.04',
            'baboon': 'https://sipi.usc.edu/database/download.php?vol=misc&img=4.2.03',
            'peppers': 'https://sipi.usc.edu/database/download.php?vol=misc&img=4.2.07',
        }
        
        if image_name in urls:
            filename = f'{image_name}_{size[0]}x{size[1]}.png'
            print(f"Downloading {image_name}...")
            
            # Download and save
            urllib.request.urlretrieve(urls[image_name], filename)
            
            # Resize if needed
            img = Image.open(filename)
            if img.size != size:
                img = img.resize(size, Image.LANCZOS)
            img.save(filename)
            
            print(f"✓ Downloaded and saved: {filename}")
            return filename
            
    except Exception as e:
        print(f"Could not download {image_name}: {e}")
    
    # Fallback: Create structured test image
    print(f"Creating structured test image as fallback...")
    return create_structured_test_image(size, image_name)


def create_structured_test_image(size=(512, 512, 3), name='test'):
    """
    Create a structured test image (better than random noise)
    
    Args:
        size: Image dimensions
        name: Image name
    
    Returns:
        str: Path to saved image
    """
    height, width = size[0], size[1]
    channels = size[2] if len(size) > 2 else 3
    
    # Create gradient + pattern image
    img_array = np.zeros((height, width, channels), dtype=np.uint8)
    
    # Add gradients
    for i in range(height):
        for j in range(width):
            img_array[i, j, 0] = int(255 * i / height)  # Red gradient
            img_array[i, j, 1] = int(255 * j / width)   # Green gradient
            img_array[i, j, 2] = int(255 * ((i + j) / (height + width)))  # Blue gradient
    
    # Add checkerboard pattern
    block_size = 32
    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            if ((i // block_size) + (j // block_size)) % 2 == 0:
                img_array[i:i+block_size, j:j+block_size] //= 2
    
    filename = f'{name}_{height}x{width}.png'
    Image.fromarray(img_array).save(filename)
    print(f"✓ Created structured test image: {filename}")
    
    return filename


class CompleteSecurityDemo:
    """
    Complete demonstration of the multi-layered security system
    """
    
    def __init__(self, num_singlets=500):
        """
        Initialize the complete system
        
        Args:
            num_singlets: Number of singlet states for QKD
        """
        self.num_singlets = num_singlets
        self.qkd_system = MultiLayeredSecuritySystem(num_singlets)
        self.stego_system = DeepSteganography(device='cpu', beta=1.0)
        
    def calculate_psnr(self, img1, img2):
        """Calculate Peak Signal-to-Noise Ratio"""
        mse = np.mean((img1.astype(float) - img2.astype(float)) ** 2)
        if mse == 0:
            return float('inf')
        max_pixel = 255.0
        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
        return psnr
    
    def full_workflow(self, secret_image_path, cover_image_path):
        """
        Execute complete workflow:
        1. Create steganographic image
        2. Generate quantum key (E91 QKD)
        3. Hash key (SHA-256)
        4. Encrypt stego image (AES)
        5. Transmit over classical channel
        6. Decrypt stego image
        7. Reveal secret image
        
        Args:
            secret_image_path: Path to secret image
            cover_image_path: Path to cover image
        """
        print("\n" + "="*80)
        print(" "*20 + "COMPLETE SECURITY WORKFLOW")
        print("="*80)
        
        results = {}
        
        # ===================================================================
        # PHASE 1: STEGANOGRAPHY - Hide Secret in Cover
        # ===================================================================
        print("\n" + "─"*80)
        print("PHASE 1: STEGANOGRAPHY - Hiding Secret Image")
        print("─"*80)
        
        # Load images
        secret_img = np.array(Image.open(secret_image_path))
        cover_img = np.array(Image.open(cover_image_path))
        
        # Ensure same size
        if secret_img.shape != cover_img.shape:
            secret_img = np.array(Image.fromarray(secret_img).resize(
                (cover_img.shape[1], cover_img.shape[0])
            ))
        
        print(f"Secret image: {secret_image_path}")
        print(f"Cover image: {cover_image_path}")
        print(f"Image shape: {cover_img.shape}")
        
        # Create stego image (using simple method for demo)
        stego_img = self.stego_system.create_simple_stego(cover_img, secret_img)
        
        # Calculate stego quality
        stego_diff = np.mean(np.abs(cover_img.astype(int) - stego_img.astype(int)))
        print(f"Average pixel change in cover: {stego_diff:.2f}")
        print(f"Stego image PSNR: {self.calculate_psnr(cover_img, stego_img):.2f} dB")
        
        # Save stego image
        stego_path = 'stego_image.png'
        Image.fromarray(stego_img).save(stego_path)
        print(f"✓ Stego image created: {stego_path}")
        
        results['stego_image'] = stego_img
        results['stego_psnr'] = self.calculate_psnr(cover_img, stego_img)
        results['secret_image_name'] = os.path.basename(secret_image_path)
        results['cover_image_name'] = os.path.basename(cover_image_path)
        
        # ===================================================================
        # PHASE 2: QUANTUM KEY DISTRIBUTION (E91)
        # ===================================================================
        print("\n" + "─"*80)
        print("PHASE 2: QUANTUM KEY DISTRIBUTION (E91 Protocol)")
        print("─"*80)
        
        qkd_results = self.qkd_system.generate_quantum_key()
        results.update(qkd_results)
        
        # ===================================================================
        # PHASE 3: KEY HASHING (SHA-256)
        # ===================================================================
        print("\n" + "─"*80)
        print("PHASE 3: KEY HASHING (SHA-256)")
        print("─"*80)
        
        hashed_key = self.qkd_system.hash_quantum_key()
        results['hashed_key'] = hashed_key
        
        # ===================================================================
        # PHASE 4: ENCRYPTION (AES-256)
        # ===================================================================
        print("\n" + "─"*80)
        print("PHASE 4: ENCRYPTION OF STEGO IMAGE (AES-256)")
        print("─"*80)
        
        # Encrypt stego image
        start_time = time.time()
        encrypted_data, iv, _ = self.qkd_system.encrypt_image(stego_path)
        encryption_time = time.time() - start_time
        
        print(f"Encryption time: {encryption_time:.5f} seconds")
        results['encryption_time'] = encryption_time
        results['encrypted_data'] = encrypted_data
        results['iv'] = iv
        
        # Security analysis
        metrics = self.qkd_system.analyze_encryption_security(
            stego_img, encrypted_data, stego_img.shape
        )
        results['security_metrics'] = metrics
        
        # ===================================================================
        # PHASE 5: CLASSICAL CHANNEL TRANSMISSION
        # ===================================================================
        print("\n" + "─"*80)
        print("PHASE 5: TRANSMISSION OVER CLASSICAL CHANNEL")
        print("─"*80)
        print("Simulating transmission...")
        print(f"Data size: {len(encrypted_data)} bytes")
        print("✓ Encrypted stego image transmitted")
        
        # ===================================================================
        # PHASE 6: DECRYPTION (AES-256)
        # ===================================================================
        print("\n" + "─"*80)
        print("PHASE 6: DECRYPTION OF STEGO IMAGE")
        print("─"*80)
        
        start_time = time.time()
        decrypted_stego = self.qkd_system.decrypt_image(
            encrypted_data, iv, stego_img.shape
        )
        decryption_time = time.time() - start_time
        
        print(f"Decryption time: {decryption_time:.5f} seconds")
        
        # Verify decryption
        if np.array_equal(stego_img, decrypted_stego):
            print("✓ Perfect decryption - stego image recovered exactly!")
        else:
            diff = np.sum(stego_img != decrypted_stego)
            print(f"⚠ Decryption error: {diff} pixels different")
        
        results['decryption_time'] = decryption_time
        
        # ===================================================================
        # PHASE 7: REVEAL SECRET IMAGE
        # ===================================================================
        print("\n" + "─"*80)
        print("PHASE 7: REVEALING SECRET IMAGE FROM STEGO")
        print("─"*80)
        
        # Extract secret from decrypted stego
        revealed_secret = (decrypted_stego & 0x0F) << 4
        
        # Calculate recovery quality
        recovery_error = np.mean(np.abs(
            secret_img.astype(int) - revealed_secret.astype(int)
        ))
        recovery_psnr = self.calculate_psnr(secret_img, revealed_secret)
        
        print(f"Secret recovery error: {recovery_error:.2f}")
        print(f"Secret recovery PSNR: {recovery_psnr:.2f} dB")
        
        # Save revealed secret
        revealed_path = 'revealed_secret.png'
        Image.fromarray(revealed_secret).save(revealed_path)
        print(f"✓ Secret image revealed: {revealed_path}")
        
        results['revealed_secret'] = revealed_secret
        results['recovery_psnr'] = recovery_psnr
        
        # Print summary
        self.print_summary(results, stego_img.shape)
        
        return results
    
    def print_summary(self, results, image_shape):
        """Print comprehensive summary of all results"""
        print("\n" + "="*80)
        print(" "*30 + "FINAL SUMMARY")
        print("="*80)
        
        # Pre-calculate formatted values
        gen_rate_str = f"{results['generation_rate']:.2f}"
        chsh_str = f"{results['chsh_value']:.4f}"
        enc_time_str = f"{results['encryption_time']:.5f}"
        dec_time_str = f"{results['decryption_time']:.5f}"
        enc_entropy_str = f"{results['security_metrics']['encrypted_entropy']:.4f}"
        npcr_str = f"{results['security_metrics']['npcr']:.2f}"
        uaci_str = f"{results['security_metrics']['uaci']:.2f}"
        stego_psnr_str = f"{results['stego_psnr']:.2f}"
        recovery_psnr_str = f"{results['recovery_psnr']:.2f}"
        
        print(f"\n┌─ TEST IMAGES ─────────────────────────────────────────────────┐")
        print(f"│ Secret Image: {results['secret_image_name']:<46} │")
        print(f"│ Cover Image: {results['cover_image_name']:<47} │")
        print(f"│ Image Size: {image_shape[0]}x{image_shape[1]}x{image_shape[2]}{' '*(46-len(f'{image_shape[0]}x{image_shape[1]}x{image_shape[2]}'))}│")
        print("└───────────────────────────────────────────────────────────────┘")
        
        print("\n┌─ QUANTUM KEY DISTRIBUTION ────────────────────────────────────┐")
        print(f"│ Protocol: E91 (Entanglement-based)                            │")
        print(f"│ Singlet States: {self.num_singlets:<47} │")
        print(f"│ Key Length: {results['key_length']} bits{' '*(47-len(str(results['key_length']))-5)}│")
        print(f"│ Generation Rate: {gen_rate_str} bps{' '*(41-len(gen_rate_str))}│")
        print(f"│ CHSH Value: {chsh_str} (Quantum: ~-2.828){' '*(23-len(chsh_str))}│")
        print(f"│ Security Status: {'✓ Eavesdropper-free' if abs(results['chsh_value']) > 2 else '⚠ Potential eavesdropping':<43} │")
        print("└───────────────────────────────────────────────────────────────┘")
        
        print("\n┌─ KEY HASHING ─────────────────────────────────────────────────┐")
        print(f"│ Algorithm: SHA-256                                            │")
        print(f"│ Output Length: 256 bits                                       │")
        print(f"│ Hash: {results['hashed_key'][:28]}...{' '*(21-len(results['hashed_key'][:28]))}│")
        print("└───────────────────────────────────────────────────────────────┘")
        
        print("\n┌─ ENCRYPTION ──────────────────────────────────────────────────┐")
        print(f"│ Algorithm: AES-256-CBC                                        │")
        print(f"│ Image Size: {image_shape[0]}x{image_shape[1]}x{image_shape[2]}{' '*(46-len(f'{image_shape[0]}x{image_shape[1]}x{image_shape[2]}'))}│")
        print(f"│ Encryption Time: {enc_time_str} seconds{' '*(36-len(enc_time_str))}│")
        print(f"│ Decryption Time: {dec_time_str} seconds{' '*(36-len(dec_time_str))}│")
        print("└───────────────────────────────────────────────────────────────┘")
        
        metrics = results['security_metrics']
        print("\n┌─ SECURITY METRICS ────────────────────────────────────────────┐")
        print(f"│ Encrypted Image Entropy: {enc_entropy_str} / 8.0000{' '*(25-len(enc_entropy_str))}│")
        print(f"│ NPCR: {npcr_str}% (Target: ~99.6%){' '*(35-len(npcr_str))}│")
        print(f"│ UACI: {uaci_str}% (Target: ~33.4%){' '*(35-len(uaci_str))}│")
        print("└───────────────────────────────────────────────────────────────┘")
        
        print("\n┌─ STEGANOGRAPHY ───────────────────────────────────────────────┐")
        print(f"│ Method: LSB-based (Simplified)                                │")
        print(f"│ Stego Quality (PSNR): {stego_psnr_str} dB{' '*(34-len(stego_psnr_str))}│")
        print(f"│ Secret Recovery (PSNR): {recovery_psnr_str} dB{' '*(31-len(recovery_psnr_str))}│")
        print("└───────────────────────────────────────────────────────────────┘")
        
        print("\n" + "="*80)
        print(" "*25 + "✓ ALL PHASES COMPLETED")
        print("="*80)


def save_results_to_drive(demo, results, key_gen_results=None, entropy_results=None, base_path=None):
    """Save all results to organized folder structure
    
    Args:
        demo: CompleteSecurityDemo instance
        results: Dictionary of workflow results
        key_gen_results: Optional list of key generation performance results
        entropy_results: Optional list of entropy analysis results
        base_path: Optional base directory path. If None, tries to detect Google Drive
                  or uses current directory
    """
    print("\n" + "="*80)
    print("SAVING RESULTS")
    print("="*80)
    
    # Create timestamped folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Determine base path
    if base_path is None:
        # Use current directory
        base_path = os.getcwd()
        print("📍 Using current directory")
    
    # Create output folder
    output_folder = os.path.join(base_path, f"Multi_Layered_Security_Results_{timestamp}")
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"\n📂 Created output folder: {output_folder}")
    
    # Create subfolders
    images_folder = os.path.join(output_folder, "images")
    logs_folder = os.path.join(output_folder, "logs")
    results_folder = os.path.join(output_folder, "results")
    
    os.makedirs(images_folder, exist_ok=True)
    os.makedirs(logs_folder, exist_ok=True)
    os.makedirs(results_folder, exist_ok=True)
    
    print("  ├── images/")
    print("  ├── logs/")
    print("  └── results/")
    
    # Save all PNG images from current directory
    print("\n🖼️  Saving images...")
    image_files = [f for f in os.listdir('.') if f.endswith('.png')]
    for img_file in image_files:
        shutil.copy(img_file, os.path.join(images_folder, img_file))
        print(f"  ✓ Saved: {img_file}")
    
    # Save matplotlib figures
    print("\n📊 Saving plots...")
    if plt.get_fignums():
        for i, fignum in enumerate(plt.get_fignums()):
            fig = plt.figure(fignum)
            plot_filename = os.path.join(images_folder, f"plot_{i+1}.png")
            fig.savefig(plot_filename, dpi=300, bbox_inches='tight')
            print(f"  ✓ Saved: plot_{i+1}.png")
    
    # Create comprehensive results summary
    print("\n📝 Creating results summary...")
    
    results_summary = {
        "experiment_info": {
            "timestamp": timestamp,
            "notebook": "Multi-Layered Security System",
            "research_paper": "Arman Sykot et al., arXiv:2408.06964v1",
            "test_images": {
                "secret": results.get('secret_image_name', 'unknown'),
                "cover": results.get('cover_image_name', 'unknown')
            }
        }
    }
    
    # Add main workflow results
    if 'key_length' in results:
        results_summary["qkd_results"] = {
            "singlet_states": demo.num_singlets,
            "key_length": int(results['key_length']),
            "generation_rate": float(results['generation_rate']),
            "chsh_value": float(results['chsh_value']),
            "hashed_key_preview": results['hashed_key'][:32] + "..."
        }
        print("  ✓ Added QKD results")
    
    if 'security_metrics' in results:
        results_summary["security_metrics"] = {
            k: float(v) if isinstance(v, (np.floating, np.integer, float, int)) else str(v)
            for k, v in results['security_metrics'].items()
        }
        print("  ✓ Added security metrics")
    
    if 'encryption_time' in results:
        results_summary["performance"] = {
            "encryption_time_seconds": float(results['encryption_time']),
            "decryption_time_seconds": float(results['decryption_time']),
            "stego_psnr_db": float(results['stego_psnr']),
            "recovery_psnr_db": float(results['recovery_psnr'])
        }
        print("  ✓ Added performance metrics")
    
    # Add key generation performance results if available
    if key_gen_results:
        results_summary["key_generation_performance"] = [
            {
                "singlets": int(r[0]),
                "key_length": int(r[1]),
                "time_seconds": float(r[2]),
                "rate_bps": float(r[3])
            }
            for r in key_gen_results
        ]
        print("  ✓ Added key generation performance")
    
    # Add entropy analysis results if available
    if entropy_results:
        results_summary["entropy_analysis"] = [
            {
                "image_size": f"{r[0][0]}x{r[0][1]}",
                "original_entropy": float(r[1]),
                "encrypted_entropy": float(r[2]),
                "improvement_percent": float((r[2] - r[1]) / r[1] * 100) if r[1] > 0 else 0
            }
            for r in entropy_results
        ]
        print("  ✓ Added entropy analysis")
    
    # Save results as JSON
    results_json_path = os.path.join(results_folder, "results_summary.json")
    with open(results_json_path, 'w') as f:
        json.dump(results_summary, f, indent=2)
    print(f"\n💾 Saved JSON summary: results_summary.json")
    
    # Create detailed text report
    report_path = os.path.join(logs_folder, "experiment_report.txt")
    with open(report_path, 'w') as f:
        f.write("="*80 + "\n")
        f.write("MULTI-LAYERED SECURITY SYSTEM - EXPERIMENT REPORT\n")
        f.write("="*80 + "\n\n")
        f.write(f"Date & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Research Paper: Arman Sykot et al., arXiv:2408.06964v1\n\n")
        
        f.write("─"*80 + "\n")
        f.write("SYSTEM COMPONENTS\n")
        f.write("─"*80 + "\n")
        f.write("1. E91 Quantum Key Distribution Protocol\n")
        f.write("2. SHA-256 Cryptographic Hashing\n")
        f.write("3. AES-256 Symmetric Encryption (CBC mode)\n")
        f.write("4. Deep Steganography (CNN-based)\n\n")
        
        if 'test_images' in results_summary['experiment_info']:
            f.write("─"*80 + "\n")
            f.write("TEST IMAGES\n")
            f.write("─"*80 + "\n")
            f.write(f"Secret Image: {results_summary['experiment_info']['test_images']['secret']}\n")
            f.write(f"Cover Image: {results_summary['experiment_info']['test_images']['cover']}\n\n")
        
        if 'qkd_results' in results_summary:
            f.write("─"*80 + "\n")
            f.write("QUANTUM KEY DISTRIBUTION RESULTS\n")
            f.write("─"*80 + "\n")
            for key, value in results_summary['qkd_results'].items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
        
        if 'security_metrics' in results_summary:
            f.write("─"*80 + "\n")
            f.write("SECURITY METRICS\n")
            f.write("─"*80 + "\n")
            for key, value in results_summary['security_metrics'].items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
        
        if 'performance' in results_summary:
            f.write("─"*80 + "\n")
            f.write("PERFORMANCE METRICS\n")
            f.write("─"*80 + "\n")
            for key, value in results_summary['performance'].items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
        
        if 'key_generation_performance' in results_summary:
            f.write("─"*80 + "\n")
            f.write("KEY GENERATION PERFORMANCE\n")
            f.write("─"*80 + "\n")
            f.write(f"{'Singlets':<15} {'Key Length':<15} {'Time (s)':<15} {'Rate (bps)':<15}\n")
            f.write("─"*80 + "\n")
            for result in results_summary['key_generation_performance']:
                f.write(f"{result['singlets']:<15} {result['key_length']:<15} "
                       f"{result['time_seconds']:<15.4f} {result['rate_bps']:<15.2f}\n")
            f.write("\n")
        
        if 'entropy_analysis' in results_summary:
            f.write("─"*80 + "\n")
            f.write("ENTROPY ANALYSIS\n")
            f.write("─"*80 + "\n")
            f.write(f"{'Image Size':<20} {'Original':<20} {'Encrypted':<20} {'Improvement %':<15}\n")
            f.write("─"*80 + "\n")
            for result in results_summary['entropy_analysis']:
                f.write(f"{result['image_size']:<20} {result['original_entropy']:<20.4f} "
                       f"{result['encrypted_entropy']:<20.4f} {result['improvement_percent']:<15.2f}\n")
            f.write("\n")
        
        f.write("="*80 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*80 + "\n")
    
    print(f"📄 Saved text report: experiment_report.txt")
    
    # Create README file
    readme_path = os.path.join(output_folder, "README.txt")
    with open(readme_path, 'w') as f:
        f.write("Multi-Layered Security System - Experiment Results\n")
        f.write("="*60 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("Test Images:\n")
        if 'test_images' in results_summary['experiment_info']:
            f.write(f"  - Secret: {results_summary['experiment_info']['test_images']['secret']}\n")
            f.write(f"  - Cover: {results_summary['experiment_info']['test_images']['cover']}\n\n")
        f.write("Contents:\n")
        f.write("  - images/: All generated images (cover, secret, stego, encrypted)\n")
        f.write("  - logs/: Experiment reports and detailed logs\n")
        f.write("  - results/: JSON summary of all results\n\n")
        f.write("Research Paper:\n")
        f.write("  Title: Multi-Layered Security System\n")
        f.write("  Authors: Arman Sykot et al.\n")
        f.write("  arXiv: 2408.06964v1\n")
    
    print(f"📋 Created README.txt")
    
    # Summary of saved files
    print("\n" + "="*80)
    print("SAVE COMPLETE!")
    print("="*80)
    print(f"\n📁 All results saved to:")
    print(f"   {output_folder}")
    print(f"\n📊 Summary:")
    print(f"   Images saved: {len(image_files)} files")
    print(f"   Plots saved: {len(plt.get_fignums())} plots")
    print(f"   Reports: 1 text report, 1 JSON summary")
    print("="*80)
    
    return output_folder


def run_complete_demonstration(secret_image='camera', cover_image='astronaut', size=(256, 256)):
    """
    Run complete demonstration of the multi-layered security system
    
    Args:
        secret_image: Name of secret image ('camera', 'astronaut', 'coffee', etc.)
        cover_image: Name of cover image
        size: Image size (width, height)
    """
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + " "*15 + "MULTI-LAYERED SECURITY SYSTEM DEMONSTRATION" + " "*20 + "█")
    print("█" + " "*78 + "█")
    print("█" + " "*10 + "Integrating Quantum Key Distribution with Classical" + " "*17 + "█")
    print("█" + " "*15 + "Cryptography to Enhance Steganographic Security" + " "*16 + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    
    # Create demo system
    demo = CompleteSecurityDemo(num_singlets=250)
    
    # Get standard test images
    print("\n📸 Loading standard test images...")
    
    secret_path = download_standard_image(secret_image, size + (3,))
    cover_path = download_standard_image(cover_image, size + (3,))
    
    # Run complete workflow
    results = demo.full_workflow(secret_path, cover_path)
    
    print("\n✓ Complete demonstration finished successfully!")
    
    return demo, results


def run_comparison_table():
    """
    Generate comparison table similar to paper's Table 1
    Returns list of results for saving
    """
    print("\n" + "="*80)
    print("PERFORMANCE COMPARISON - Key Generation Rate")
    print("="*80)
    
    singlet_states = [25, 100, 250, 500]
    results = []
    
    print(f"\n{'Singlet States':<20} {'Key Length':<15} {'Time (s)':<15} {'Rate (bps)':<15}")
    print("-"*65)
    
    for num_singlets in singlet_states:
        qkd = E91QKD(num_singlets)
        alice_key, bob_key, chsh, gen_time = qkd.run_protocol()
        key_len = len(alice_key)
        rate = key_len / gen_time if gen_time > 0 else 0
        
        print(f"{num_singlets:<20} {key_len:<15} {gen_time:<15.4f} {rate:<15.2f}")
        results.append((num_singlets, key_len, gen_time, rate))
    
    print("="*80)
    return results


def run_entropy_analysis(test_images=['camera', 'astronaut', 'coffee']):
    """
    Generate entropy analysis table using standard images
    Returns list of results for saving
    """
    print("\n" + "="*80)
    print("SECURITY ANALYSIS - Image Entropy")
    print("="*80)
    
    pixel_sizes = [(64, 64), (128, 128), (256, 256)]
    analysis = ImageAnalysis()
    results = []
    
    print(f"\n{'Image Size':<20} {'Original Entropy':<20} {'Encrypted Entropy':<20}")
    print("-"*60)
    
    for size in pixel_sizes:
        # Use first test image
        img_path = download_standard_image(test_images[0], size + (3,))
        
        # Create system and encrypt
        system = MultiLayeredSecuritySystem(num_singlets=100)
        system.generate_quantum_key()
        system.hash_quantum_key()
        
        encrypted_data, iv, original_array = system.encrypt_image(img_path)
        
        # Calculate entropies
        original_entropy = analysis.calculate_entropy(original_array)
        
        # Create encrypted image array for analysis
        target_size = np.prod(original_array.shape)
        encrypted_array = np.frombuffer(encrypted_data[:target_size], dtype=np.uint8)
        if len(encrypted_array) < target_size:
            encrypted_array = np.pad(encrypted_array, (0, target_size - len(encrypted_array)))
        encrypted_img = encrypted_array.reshape(original_array.shape)
        encrypted_entropy = analysis.calculate_entropy(encrypted_img)
        
        print(f"{size[0]}x{size[1]:<16} {original_entropy:<20.4f} {encrypted_entropy:<20.4f}")
        results.append((size, original_entropy, encrypted_entropy))
    
    print("="*80)
    return results


if __name__ == "__main__":
    # ========================================================================
    # CONFIGURATION - Change these values as needed
    # ========================================================================
    
    # Test images to use
    # Available built-in: 'camera', 'astronaut', 'coffee', 'chelsea', 'rocket'
    # Available download: 'lena', 'baboon', 'peppers'
    SECRET_IMAGE = 'camera'    # Change this to use different secret image
    COVER_IMAGE = 'rocket'   # Change this to use different cover image
    IMAGE_SIZE = (512, 512)     # Change image size as needed (256, 512, etc.)
    
    # Save location (optional)
    # Option 1: Let code auto-detect (Google Drive if in Colab, current dir otherwise)
    SAVE_PATH = None
    
    # Option 2: Specify custom path for Google Drive
    # SAVE_PATH = '/content/drive/MyDrive/Quantum Computing/QKD/16. Paper Implementation/Project'
    
    # Option 3: Specify custom local path
    # SAVE_PATH = '/path/to/your/results/folder'
    
    # ========================================================================
    # RUN EXPERIMENTS
    # ========================================================================
    
    # Run complete demonstration
    demo, results = run_complete_demonstration(SECRET_IMAGE, COVER_IMAGE, IMAGE_SIZE)
    
    # Additional analyses
    print("\n\n" + "█"*80)
    print("█" + " "*25 + "ADDITIONAL ANALYSES" + " "*32 + "█")
    print("█"*80)
    
    key_gen_results = run_comparison_table()
    entropy_results = run_entropy_analysis()
    
    print("\n\n✓ All demonstrations and analyses complete!")
    print("\nThis implementation demonstrates the key concepts from:")
    print('"Multi-Layered Security System: Integrating Quantum Key Distribution')
    print('with Classical Cryptography to Enhance Steganographic Security"')
    print("by Arman Sykot et al.")
    
    # Save all results
    try:
        output_folder = save_results_to_drive(
            demo, results, key_gen_results, entropy_results, base_path=SAVE_PATH
        )
        print(f"\n✓✓✓ All results successfully saved!")
        print(f"📁 Location: {output_folder}")
    except Exception as e:
        print(f"\n⚠ Warning: Could not save results: {e}")
        print("Results are still available in the current directory.")