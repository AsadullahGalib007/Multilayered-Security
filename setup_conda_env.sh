#!/bin/bash
################################################################################
# Setup Script for Multi-Layered Security System
# For Linux/Mac
#
# This script will:
# 1. Check if conda is installed
# 2. Create a new conda environment
# 3. Install all required packages
# 4. Verify the installation
#
# Usage: bash setup_conda_env.sh
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENV_NAME="quantum-security"
PYTHON_VERSION="3.10"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

################################################################################
# Check Prerequisites
################################################################################

check_conda() {
    print_header "Checking Prerequisites"
    
    if ! command -v conda &> /dev/null; then
        print_error "Conda is not installed!"
        echo ""
        echo "Please install Miniconda or Anaconda first:"
        echo "  Miniconda: https://docs.conda.io/en/latest/miniconda.html"
        echo "  Anaconda:  https://www.anaconda.com/products/distribution"
        exit 1
    fi
    
    print_success "Conda is installed"
    conda --version
}

################################################################################
# Create Environment
################################################################################

create_environment() {
    print_header "Creating Conda Environment: $ENV_NAME"
    
    # Check if environment already exists
    if conda env list | grep -q "^$ENV_NAME "; then
        print_warning "Environment '$ENV_NAME' already exists"
        read -p "Do you want to remove it and create a new one? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Removing existing environment..."
            conda env remove -n $ENV_NAME -y
            print_success "Removed existing environment"
        else
            print_info "Using existing environment"
            return 0
        fi
    fi
    
    # Check if environment.yml exists
    if [ -f "environment.yml" ]; then
        print_info "Creating environment from environment.yml..."
        conda env create -f environment.yml
        print_success "Environment created from environment.yml"
    else
        print_info "Creating environment manually..."
        
        # Create base environment
        conda create -n $ENV_NAME python=$PYTHON_VERSION -y
        print_success "Base environment created"
        
        # Activate environment
        eval "$(conda shell.bash hook)"
        conda activate $ENV_NAME
        
        # Install conda packages
        print_info "Installing conda packages..."
        conda install -c conda-forge -y \
            numpy scipy matplotlib pillow opencv tqdm jupyter ipykernel
        
        # Install PyTorch (CPU version)
        print_info "Installing PyTorch (CPU version)..."
        conda install -c pytorch -y pytorch torchvision cpuonly
        
        # Install pip packages
        print_info "Installing pip packages..."
        pip install --no-cache-dir \
            qiskit>=1.0.0 \
            qiskit-aer>=0.13.0 \
            pycryptodome>=3.19.0
        
        print_success "All packages installed"
    fi
}

################################################################################
# Verify Installation
################################################################################

verify_installation() {
    print_header "Verifying Installation"
    
    # Activate environment
    eval "$(conda shell.bash hook)"
    conda activate $ENV_NAME
    
    # Test imports
    python << 'EOF'
import sys
print(f"Python version: {sys.version}")
print("\nTesting package imports...")

packages = [
    ("numpy", "NumPy"),
    ("scipy", "SciPy"),
    ("matplotlib", "Matplotlib"),
    ("PIL", "Pillow"),
    ("cv2", "OpenCV"),
    ("torch", "PyTorch"),
    ("torchvision", "TorchVision"),
    ("qiskit", "Qiskit"),
    ("qiskit_aer", "Qiskit Aer"),
    ("Crypto", "PyCryptodome"),
]

success = True
for module, name in packages:
    try:
        __import__(module)
        print(f"  ✓ {name}")
    except ImportError as e:
        print(f"  ✗ {name}: {e}")
        success = False

if success:
    print("\n✓ All packages imported successfully!")
    sys.exit(0)
else:
    print("\n✗ Some packages failed to import")
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        print_success "Verification complete!"
    else
        print_error "Verification failed!"
        return 1
    fi
}

################################################################################
# Run Quick Test
################################################################################

run_quick_test() {
    print_header "Running Quick Test"
    
    if [ -f "quick_test.py" ]; then
        print_info "Running quick_test.py..."
        python quick_test.py
        
        if [ $? -eq 0 ]; then
            print_success "Quick test passed!"
        else
            print_warning "Quick test had some issues (this may be normal if dependencies are missing)"
        fi
    else
        print_warning "quick_test.py not found, skipping test"
    fi
}

################################################################################
# Create Activation Script
################################################################################

create_activation_script() {
    print_header "Creating Activation Scripts"
    
    # Create activation script
    cat > activate_env.sh << EOF
#!/bin/bash
# Quick activation script for quantum-security environment

# Initialize conda for bash
eval "\$(conda shell.bash hook)"

# Activate environment
conda activate $ENV_NAME

echo "✓ Activated conda environment: $ENV_NAME"
echo ""
echo "Python: \$(python --version)"
echo "Location: \$(which python)"
echo ""
echo "You can now run:"
echo "  python quick_test.py       - Run verification tests"
echo "  python complete_demo.py    - Run complete demonstration"
echo ""
echo "To deactivate: conda deactivate"
EOF
    
    chmod +x activate_env.sh
    print_success "Created activate_env.sh"
    
    # Create Jupyter kernel
    print_info "Registering Jupyter kernel..."
    eval "$(conda shell.bash hook)"
    conda activate $ENV_NAME
    python -m ipykernel install --user --name $ENV_NAME --display-name "Python ($ENV_NAME)"
    print_success "Jupyter kernel registered"
}

################################################################################
# Print Summary
################################################################################

print_summary() {
    print_header "Setup Complete!"
    
    echo ""
    echo "Environment Name: $ENV_NAME"
    echo ""
    echo "To activate the environment:"
    echo -e "  ${GREEN}conda activate $ENV_NAME${NC}"
    echo ""
    echo "Or use the quick activation script:"
    echo -e "  ${GREEN}source activate_env.sh${NC}"
    echo ""
    echo "To deactivate:"
    echo -e "  ${GREEN}conda deactivate${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Activate the environment"
    echo "  2. Run: python quick_test.py"
    echo "  3. Run: python complete_demo.py"
    echo ""
    echo "For Jupyter notebooks:"
    echo "  jupyter notebook"
    echo "  (Select kernel: Python ($ENV_NAME))"
    echo ""
}

################################################################################
# Main Script
################################################################################

main() {
    print_header "Multi-Layered Security System - Conda Setup"
    echo ""
    
    # Run setup steps
    check_conda
    echo ""
    
    create_environment
    echo ""
    
    verify_installation
    echo ""
    
    create_activation_script
    echo ""
    
    # Optional: Run quick test
    read -p "Do you want to run the quick test now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_quick_test
        echo ""
    fi
    
    print_summary
}

# Run main function
main

exit 0
