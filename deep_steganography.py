"""
Deep Steganography Module
CNN-based image hiding and revealing networks

Based on "Hiding Images in Plain Sight: Deep Steganography" approach
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import matplotlib.pyplot as plt


class PrepNetwork(nn.Module):
    """
    Preparation Network: Prepares the secret image for hiding
    """
    def __init__(self):
        super(PrepNetwork, self).__init__()
        
        self.conv1 = nn.Conv2d(3, 50, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(50, 50, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(50, 50, kernel_size=3, padding=1)
        self.conv4 = nn.Conv2d(50, 50, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = self.relu(self.conv3(x))
        x = self.relu(self.conv4(x))
        return x


class HidingNetwork(nn.Module):
    """
    Hiding Network: Embeds prepared secret image into cover image
    """
    def __init__(self):
        super(HidingNetwork, self).__init__()
        
        # Input: concatenated cover (3 channels) + prepared secret (50 channels) = 53 channels
        self.conv1 = nn.Conv2d(53, 50, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(50, 50, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(50, 50, kernel_size=3, padding=1)
        self.conv4 = nn.Conv2d(50, 50, kernel_size=3, padding=1)
        self.conv5 = nn.Conv2d(50, 3, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        
    def forward(self, cover, prepared_secret):
        # Concatenate cover and prepared secret
        x = torch.cat([cover, prepared_secret], dim=1)
        
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = self.relu(self.conv3(x))
        x = self.relu(self.conv4(x))
        x = self.conv5(x)  # No activation on last layer
        
        return x


class RevealNetwork(nn.Module):
    """
    Reveal Network: Extracts secret image from stego image
    """
    def __init__(self):
        super(RevealNetwork, self).__init__()
        
        self.conv1 = nn.Conv2d(3, 50, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(50, 50, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(50, 50, kernel_size=3, padding=1)
        self.conv4 = nn.Conv2d(50, 50, kernel_size=3, padding=1)
        self.conv5 = nn.Conv2d(50, 3, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        
    def forward(self, stego):
        x = self.relu(self.conv1(stego))
        x = self.relu(self.conv2(x))
        x = self.relu(self.conv3(x))
        x = self.relu(self.conv4(x))
        x = self.conv5(x)  # No activation on last layer
        
        return x


class DeepSteganography:
    """
    Complete Deep Steganography System
    """
    def __init__(self, device='cpu', beta=1.0):
        """
        Initialize deep steganography networks
        
        Args:
            device: 'cpu' or 'cuda'
            beta: Trade-off parameter between cover and secret reconstruction
        """
        self.device = torch.device(device)
        self.beta = beta
        
        # Initialize networks
        self.prep_net = PrepNetwork().to(self.device)
        self.hiding_net = HidingNetwork().to(self.device)
        self.reveal_net = RevealNetwork().to(self.device)
        
        # For pre-trained models
        self.is_trained = False
        
    def loss_function(self, cover, secret, stego, revealed):
        """
        Combined loss function: L = ||cover - stego|| + β||secret - revealed||
        
        Args:
            cover: Original cover image
            secret: Original secret image
            stego: Generated stego image
            revealed: Revealed secret image
            
        Returns:
            tuple: (total_loss, cover_loss, secret_loss)
        """
        # Cover reconstruction loss
        cover_loss = torch.mean((cover - stego) ** 2)
        
        # Secret reconstruction loss
        secret_loss = torch.mean((secret - revealed) ** 2)
        
        # Total loss
        total_loss = cover_loss + self.beta * secret_loss
        
        return total_loss, cover_loss, secret_loss
    
    def train_networks(self, cover_images, secret_images, epochs=100, learning_rate=0.001):
        """
        Train the steganography networks
        
        Args:
            cover_images: List of cover images (numpy arrays)
            secret_images: List of secret images (numpy arrays)
            epochs: Number of training epochs
            learning_rate: Learning rate
        """
        print(f"Training Deep Steganography networks for {epochs} epochs...")
        
        # Combine all networks for joint training
        parameters = list(self.prep_net.parameters()) + \
                    list(self.hiding_net.parameters()) + \
                    list(self.reveal_net.parameters())
        
        optimizer = optim.Adam(parameters, lr=learning_rate)
        
        # Training loop
        for epoch in range(epochs):
            epoch_loss = 0
            epoch_cover_loss = 0
            epoch_secret_loss = 0
            
            # Simple batch training (one pair at a time for simplicity)
            for cover_img, secret_img in zip(cover_images, secret_images):
                # Convert to tensors
                cover = self.image_to_tensor(cover_img).to(self.device)
                secret = self.image_to_tensor(secret_img).to(self.device)
                
                # Forward pass
                prepared = self.prep_net(secret)
                stego = self.hiding_net(cover, prepared)
                revealed = self.reveal_net(stego)
                
                # Calculate loss
                loss, cover_loss, secret_loss = self.loss_function(cover, secret, stego, revealed)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
                epoch_cover_loss += cover_loss.item()
                epoch_secret_loss += secret_loss.item()
            
            # Print progress
            if (epoch + 1) % 10 == 0:
                avg_loss = epoch_loss / len(cover_images)
                avg_cover = epoch_cover_loss / len(cover_images)
                avg_secret = epoch_secret_loss / len(cover_images)
                print(f"Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.6f} "
                      f"(Cover: {avg_cover:.6f}, Secret: {avg_secret:.6f})")
        
        self.is_trained = True
        print("Training complete!")
    
    def hide_image(self, cover_image, secret_image):
        """
        Hide secret image in cover image
        
        Args:
            cover_image: Cover image (numpy array or PIL Image)
            secret_image: Secret image (numpy array or PIL Image)
            
        Returns:
            numpy.ndarray: Stego image
        """
        self.prep_net.eval()
        self.hiding_net.eval()
        
        with torch.no_grad():
            # Convert to tensors
            cover = self.image_to_tensor(cover_image).to(self.device)
            secret = self.image_to_tensor(secret_image).to(self.device)
            
            # Generate stego image
            prepared = self.prep_net(secret)
            stego = self.hiding_net(cover, prepared)
            
            # Convert back to numpy
            stego_image = self.tensor_to_image(stego)
        
        return stego_image
    
    def reveal_image(self, stego_image):
        """
        Reveal secret image from stego image
        
        Args:
            stego_image: Stego image (numpy array or PIL Image)
            
        Returns:
            numpy.ndarray: Revealed secret image
        """
        self.reveal_net.eval()
        
        with torch.no_grad():
            # Convert to tensor
            stego = self.image_to_tensor(stego_image).to(self.device)
            
            # Reveal secret
            revealed = self.reveal_net(stego)
            
            # Convert back to numpy
            secret_image = self.tensor_to_image(revealed)
        
        return secret_image
    
    def image_to_tensor(self, image):
        """
        Convert image to PyTorch tensor
        
        Args:
            image: numpy array or PIL Image
            
        Returns:
            torch.Tensor: Image tensor (1, C, H, W)
        """
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Normalize to [0, 1]
        image = image.astype(np.float32) / 255.0
        
        # Convert to tensor and add batch dimension
        # (H, W, C) -> (C, H, W) -> (1, C, H, W)
        tensor = torch.from_numpy(image.transpose(2, 0, 1)).unsqueeze(0)
        
        return tensor
    
    def tensor_to_image(self, tensor):
        """
        Convert PyTorch tensor to image
        
        Args:
            tensor: Image tensor (1, C, H, W)
            
        Returns:
            numpy.ndarray: Image array (H, W, C)
        """
        # Remove batch dimension and move to CPU
        # (1, C, H, W) -> (C, H, W) -> (H, W, C)
        image = tensor.squeeze(0).cpu().numpy().transpose(1, 2, 0)
        
        # Clip to [0, 1] and convert to uint8
        image = np.clip(image, 0, 1)
        image = (image * 255).astype(np.uint8)
        
        return image
    
    def create_simple_stego(self, cover_image, secret_image):
        """
        Create stego image using simple LSB method (for comparison/testing)
        
        Args:
            cover_image: Cover image array
            secret_image: Secret image array
            
        Returns:
            numpy.ndarray: Stego image
        """
        # Ensure images are same size
        if cover_image.shape != secret_image.shape:
            secret_image = np.array(Image.fromarray(secret_image).resize(
                (cover_image.shape[1], cover_image.shape[0])
            ))
        
        # Simple LSB embedding (embed secret in LSBs of cover)
        stego = cover_image.copy()
        
        # Embed secret's MSBs into cover's LSBs
        # Take top 4 bits of secret and bottom 4 bits of cover
        stego = (cover_image & 0xF0) | (secret_image >> 4)
        
        return stego
    
    def save_model(self, filepath):
        """Save trained model"""
        torch.save({
            'prep_net': self.prep_net.state_dict(),
            'hiding_net': self.hiding_net.state_dict(),
            'reveal_net': self.reveal_net.state_dict(),
            'beta': self.beta
        }, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load trained model"""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.prep_net.load_state_dict(checkpoint['prep_net'])
        self.hiding_net.load_state_dict(checkpoint['hiding_net'])
        self.reveal_net.load_state_dict(checkpoint['reveal_net'])
        self.beta = checkpoint['beta']
        self.is_trained = True
        print(f"Model loaded from {filepath}")


def demonstrate_steganography():
    """
    Demonstrate the deep steganography system
    """
    print("="*70)
    print("Deep Steganography Demonstration")
    print("="*70)
    
    # Create steganography system
    stego_system = DeepSteganography(device='cpu', beta=1.0)
    
    # Create sample images
    print("\nCreating sample images...")
    cover = np.random.randint(100, 200, (64, 64, 3), dtype=np.uint8)
    secret = np.random.randint(50, 150, (64, 64, 3), dtype=np.uint8)
    
    # For demonstration, use simple LSB method (deep learning requires training)
    print("\nUsing simplified steganography (LSB-based)...")
    stego_image = stego_system.create_simple_stego(cover, secret)
    
    print(f"Cover image shape: {cover.shape}")
    print(f"Secret image shape: {secret.shape}")
    print(f"Stego image shape: {stego_image.shape}")
    
    # Calculate difference
    diff = np.abs(cover.astype(int) - stego_image.astype(int))
    print(f"\nAverage pixel difference: {np.mean(diff):.2f}")
    print(f"Maximum pixel difference: {np.max(diff)}")
    
    # Simple extraction (for LSB method)
    revealed = (stego_image & 0x0F) << 4
    
    print(f"Revealed image shape: {revealed.shape}")
    
    # Calculate similarity
    secret_diff = np.abs(secret.astype(int) - revealed.astype(int))
    print(f"Secret recovery error: {np.mean(secret_diff):.2f}")
    
    return stego_system, cover, secret, stego_image, revealed


if __name__ == "__main__":
    system, cover, secret, stego, revealed = demonstrate_steganography()
    print("\n✓ Deep Steganography demonstration complete!")
