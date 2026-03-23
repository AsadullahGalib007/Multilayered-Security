# Multi-Layered Security System - Conda Setup Script (PowerShell)
# For Windows PowerShell
#
# Usage: .\setup_conda_env.ps1

param(
    [string]$EnvName = "quantum-security",
    [string]$PythonVersion = "3.10",
    [switch]$SkipTest,
    [switch]$GPU
)

# Colors
$ColorRed = "Red"
$ColorGreen = "Green"
$ColorYellow = "Yellow"
$ColorBlue = "Cyan"

# Helper Functions
function Print-Header {
    param([string]$Message)
    Write-Host "================================================================" -ForegroundColor $ColorBlue
    Write-Host $Message -ForegroundColor $ColorBlue
    Write-Host "================================================================" -ForegroundColor $ColorBlue
}

function Print-Success {
    param([string]$Message)
    Write-Host "[+] $Message" -ForegroundColor $ColorGreen
}

function Print-Error {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor $ColorRed
}

function Print-Warning {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor $ColorYellow
}

function Print-Info {
    param([string]$Message)
    Write-Host "[i] $Message" -ForegroundColor $ColorBlue
}

# Check if running as Administrator (optional but recommended)
function Test-Administrator {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check Prerequisites
function Test-CondaInstalled {
    Print-Header "Checking Prerequisites"
    
    try {
        $condaVersion = conda --version 2>&1
        Print-Success "Conda is installed: $condaVersion"
        return $true
    }
    catch {
        Print-Error "Conda is not installed!"
        Write-Host ""
        Write-Host "Please install Miniconda or Anaconda first:"
        Write-Host "  Miniconda: https://docs.conda.io/en/latest/miniconda.html"
        Write-Host "  Anaconda:  https://www.anaconda.com/products/distribution"
        Write-Host ""
        Write-Host "After installation, restart PowerShell and run this script again."
        return $false
    }
}

# Create Environment
function New-CondaEnvironment {
    Print-Header "Creating Conda Environment: $EnvName"
    
    # Check if environment exists
    $envExists = conda env list | Select-String -Pattern "^$EnvName\s"
    
    if ($envExists) {
        Print-Warning "Environment '$EnvName' already exists"
        $response = Read-Host "Remove and recreate? (y/N)"
        
        if ($response -eq 'y' -or $response -eq 'Y') {
            Print-Info "Removing existing environment..."
            conda env remove -n $EnvName -y
            Print-Success "Removed existing environment"
        }
        else {
            Print-Info "Using existing environment"
            return
        }
    }
    
    # Check for environment.yml
    if (Test-Path "environment.yml") {
        Print-Info "Creating environment from environment.yml..."
        conda env create -f environment.yml
        Print-Success "Environment created from environment.yml"
    }
    else {
        Print-Info "Creating environment manually..."
        
        # Create base environment
        conda create -n $EnvName python=$PythonVersion -y
        Print-Success "Base environment created"
        
        # Install conda packages
        Print-Info "Installing conda packages..."
        conda install -n $EnvName -c conda-forge -y `
            numpy scipy matplotlib pillow opencv tqdm jupyter ipykernel
        
        # Install PyTorch
        if ($GPU) {
            Print-Info "Installing PyTorch with CUDA support..."
            conda install -n $EnvName -c pytorch -c nvidia -y `
                pytorch torchvision pytorch-cuda=11.8
        }
        else {
            Print-Info "Installing PyTorch (CPU version)..."
            conda install -n $EnvName -c pytorch -y `
                pytorch torchvision cpuonly
        }
        
        # Install pip packages
        Print-Info "Installing pip packages..."
        conda run -n $EnvName pip install --no-cache-dir `
            "qiskit>=1.0.0" `
            "qiskit-aer>=0.13.0" `
            "pycryptodome>=3.19.0"
        
        Print-Success "All packages installed"
    }
}

# Verify Installation
function Test-Installation {
    Print-Header "Verifying Installation"
    
    $testScript = @"
import sys
print(f'Python version: {sys.version}')
print('\nTesting package imports...')

packages = [
    ('numpy', 'NumPy'),
    ('scipy', 'SciPy'),
    ('matplotlib', 'Matplotlib'),
    ('PIL', 'Pillow'),
    ('cv2', 'OpenCV'),
    ('torch', 'PyTorch'),
    ('torchvision', 'TorchVision'),
    ('qiskit', 'Qiskit'),
    ('qiskit_aer', 'Qiskit Aer'),
    ('Crypto', 'PyCryptodome'),
]

success = True
for module, name in packages:
    try:
        __import__(module)
        print(f'  [+] {name}')
    except ImportError as e:
        print(f'  [!] {name}: {e}')
        success = False

if success:
    print('\n[+] All packages imported successfully!')
    sys.exit(0)
else:
    print('\n[!] Some packages failed to import')
    sys.exit(1)
"@
    
    $testScript | conda run -n $EnvName python -c $input
    
    if ($LASTEXITCODE -eq 0) {
        Print-Success "Verification complete!"
        return $true
    }
    else {
        Print-Error "Verification failed!"
        return $false
    }
}

# Run Quick Test
function Invoke-QuickTest {
    Print-Header "Running Quick Test"
    
    if (Test-Path "quick_test.py") {
        Print-Info "Running quick_test.py..."
        conda run -n $EnvName python quick_test.py
        
        if ($LASTEXITCODE -eq 0) {
            Print-Success "Quick test passed!"
        }
        else {
            Print-Warning "Quick test had some issues"
        }
    }
    else {
        Print-Warning "quick_test.py not found, skipping test"
    }
}

# Create Activation Scripts
function New-ActivationScript {
    Print-Header "Creating Activation Scripts"
    
    # PowerShell activation script
    $psScript = @"
# Quick activation script for quantum-security environment
# PowerShell version

Write-Host "Activating conda environment: $EnvName" -ForegroundColor Green

conda activate $EnvName

Write-Host ""
python --version
Write-Host ""
Write-Host "You can now run:" -ForegroundColor Cyan
Write-Host "  python quick_test.py       - Run verification tests"
Write-Host "  python complete_demo.py    - Run complete demonstration"
Write-Host ""
Write-Host "To deactivate: conda deactivate" -ForegroundColor Yellow
Write-Host ""
"@
    
    $psScript | Out-File -FilePath "activate_env.ps1" -Encoding UTF8
    Print-Success "Created activate_env.ps1"
    
    # Batch activation script
    $batScript = @"
@echo off
call conda activate $EnvName
echo.
echo [32m[+] Activated conda environment: $EnvName[0m
echo.
python --version
echo.
echo You can now run:
echo   python quick_test.py       - Run verification tests
echo   python complete_demo.py    - Run complete demonstration
echo.
echo To deactivate: conda deactivate
echo.
cmd /k
"@
    
    $batScript | Out-File -FilePath "activate_env.bat" -Encoding ASCII
    Print-Success "Created activate_env.bat"
    
    # Register Jupyter kernel
    Print-Info "Registering Jupyter kernel..."
    conda run -n $EnvName python -m ipykernel install --user --name $EnvName --display-name "Python ($EnvName)"
    Print-Success "Jupyter kernel registered"
}

# Print Summary
function Show-Summary {
    Print-Header "Setup Complete!"
    
    Write-Host ""
    Write-Host "Environment Name: $EnvName" -ForegroundColor Green
    Write-Host ""
    Write-Host "To activate the environment:" -ForegroundColor Cyan
    Write-Host "  conda activate $EnvName"
    Write-Host ""
    Write-Host "Or use the quick activation scripts:"
    Write-Host "  PowerShell: .\activate_env.ps1"
    Write-Host "  Batch:      activate_env.bat"
    Write-Host ""
    Write-Host "To deactivate:" -ForegroundColor Cyan
    Write-Host "  conda deactivate"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Activate the environment"
    Write-Host "  2. Run: python quick_test.py"
    Write-Host "  3. Run: python complete_demo.py"
    Write-Host ""
    Write-Host "For Jupyter notebooks:" -ForegroundColor Cyan
    Write-Host "  jupyter notebook"
    Write-Host "  (Select kernel: Python ($EnvName))"
    Write-Host ""
}

# Main Script
function Main {
    Print-Header "Multi-Layered Security System - Conda Setup"
    Write-Host ""
    
    # Check for admin (optional warning)
    if (-not (Test-Administrator)) {
        Print-Warning "Not running as Administrator"
        Print-Info "Some operations may require elevated privileges"
        Write-Host ""
    }
    
    # Check conda
    if (-not (Test-CondaInstalled)) {
        exit 1
    }
    Write-Host ""
    
    # Create environment
    New-CondaEnvironment
    Write-Host ""
    
    # Verify installation
    if (-not (Test-Installation)) {
        Print-Error "Installation verification failed"
        exit 1
    }
    Write-Host ""
    
    # Create activation scripts
    New-ActivationScript
    Write-Host ""
    
    # Optional: Run quick test
    if (-not $SkipTest) {
        $response = Read-Host "Run quick test now? (y/N)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            Write-Host ""
            Invoke-QuickTest
            Write-Host ""
        }
    }
    
    # Show summary
    Show-Summary
}

# Run main function
try {
    Main
    exit 0
}
catch {
    Print-Error "An error occurred: $_"
    Write-Host $_.ScriptStackTrace
    exit 1
}
