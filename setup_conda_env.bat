@echo off
REM ##############################################################################
REM Setup Script for Multi-Layered Security System
REM For Windows
REM
REM This script will:
REM 1. Check if conda is installed
REM 2. Create a new conda environment
REM 3. Install all required packages
REM 4. Verify the installation
REM
REM Usage: setup_conda_env.bat
REM ##############################################################################

setlocal enabledelayedexpansion

REM Configuration
set ENV_NAME=quantum-security
set PYTHON_VERSION=3.10

REM ##############################################################################
REM Helper Functions
REM ##############################################################################

:print_header
echo ================================================================
echo %~1
echo ================================================================
goto :eof

:print_success
echo [32m[+] %~1[0m
goto :eof

:print_error
echo [31m[!] %~1[0m
goto :eof

:print_warning
echo [33m[!] %~1[0m
goto :eof

:print_info
echo [34m[i] %~1[0m
goto :eof

REM ##############################################################################
REM Check Prerequisites
REM ##############################################################################

:check_conda
call :print_header "Checking Prerequisites"

where conda >nul 2>nul
if %errorlevel% neq 0 (
    call :print_error "Conda is not installed!"
    echo.
    echo Please install Miniconda or Anaconda first:
    echo   Miniconda: https://docs.conda.io/en/latest/miniconda.html
    echo   Anaconda:  https://www.anaconda.com/products/distribution
    pause
    exit /b 1
)

call :print_success "Conda is installed"
conda --version
echo.
goto :eof

REM ##############################################################################
REM Create Environment
REM ##############################################################################

:create_environment
call :print_header "Creating Conda Environment: %ENV_NAME%"

REM Check if environment already exists
conda env list | findstr /C:"%ENV_NAME%" >nul 2>nul
if %errorlevel% equ 0 (
    call :print_warning "Environment '%ENV_NAME%' already exists"
    set /p "REMOVE=Do you want to remove it and create a new one? (y/N): "
    if /i "!REMOVE!"=="y" (
        call :print_info "Removing existing environment..."
        conda env remove -n %ENV_NAME% -y
        call :print_success "Removed existing environment"
    ) else (
        call :print_info "Using existing environment"
        goto :eof
    )
)

REM Check if environment.yml exists
if exist environment.yml (
    call :print_info "Creating environment from environment.yml..."
    conda env create -f environment.yml
    call :print_success "Environment created from environment.yml"
) else (
    call :print_info "Creating environment manually..."
    
    REM Create base environment
    conda create -n %ENV_NAME% python=%PYTHON_VERSION% -y
    call :print_success "Base environment created"
    
    REM Activate environment
    call conda activate %ENV_NAME%
    
    REM Install conda packages
    call :print_info "Installing conda packages..."
    conda install -c conda-forge -y numpy scipy matplotlib pillow opencv tqdm jupyter ipykernel
    
    REM Install PyTorch (CPU version)
    call :print_info "Installing PyTorch (CPU version)..."
    conda install -c pytorch -y pytorch torchvision cpuonly
    
    REM Install pip packages
    call :print_info "Installing pip packages..."
    pip install --no-cache-dir qiskit>=1.0.0 qiskit-aer>=0.13.0 pycryptodome>=3.19.0
    
    call :print_success "All packages installed"
)

echo.
goto :eof

REM ##############################################################################
REM Verify Installation
REM ##############################################################################

:verify_installation
call :print_header "Verifying Installation"

REM Activate environment
call conda activate %ENV_NAME%

REM Test imports
python -c "import sys; print(f'Python version: {sys.version}')"
echo.
echo Testing package imports...

python -c "^
import sys; ^
packages = [ ^
    ('numpy', 'NumPy'), ^
    ('scipy', 'SciPy'), ^
    ('matplotlib', 'Matplotlib'), ^
    ('PIL', 'Pillow'), ^
    ('cv2', 'OpenCV'), ^
    ('torch', 'PyTorch'), ^
    ('torchvision', 'TorchVision'), ^
    ('qiskit', 'Qiskit'), ^
    ('qiskit_aer', 'Qiskit Aer'), ^
    ('Crypto', 'PyCryptodome'), ^
]; ^
success = True; ^
for module, name in packages: ^
    try: ^
        __import__(module); ^
        print(f'  [+] {name}'); ^
    except ImportError as e: ^
        print(f'  [!] {name}: {e}'); ^
        success = False; ^
if success: ^
    print('\n[+] All packages imported successfully!'); ^
    sys.exit(0); ^
else: ^
    print('\n[!] Some packages failed to import'); ^
    sys.exit(1); ^
"

if %errorlevel% equ 0 (
    call :print_success "Verification complete!"
) else (
    call :print_error "Verification failed!"
    goto :eof
)

echo.
goto :eof

REM ##############################################################################
REM Run Quick Test
REM ##############################################################################

:run_quick_test
call :print_header "Running Quick Test"

if exist quick_test.py (
    call :print_info "Running quick_test.py..."
    python quick_test.py
    
    if %errorlevel% equ 0 (
        call :print_success "Quick test passed!"
    ) else (
        call :print_warning "Quick test had some issues"
    )
) else (
    call :print_warning "quick_test.py not found, skipping test"
)

echo.
goto :eof

REM ##############################################################################
REM Create Activation Script
REM ##############################################################################

:create_activation_script
call :print_header "Creating Activation Scripts"

REM Create activation script
(
echo @echo off
echo REM Quick activation script for quantum-security environment
echo.
echo call conda activate %ENV_NAME%
echo.
echo echo [32m[+] Activated conda environment: %ENV_NAME%[0m
echo echo.
echo python --version
echo echo.
echo echo You can now run:
echo echo   python quick_test.py       - Run verification tests
echo echo   python complete_demo.py    - Run complete demonstration
echo echo.
echo echo To deactivate: conda deactivate
echo.
echo cmd /k
) > activate_env.bat

call :print_success "Created activate_env.bat"

REM Create Jupyter kernel
call :print_info "Registering Jupyter kernel..."
call conda activate %ENV_NAME%
python -m ipykernel install --user --name %ENV_NAME% --display-name "Python (%ENV_NAME%)"
call :print_success "Jupyter kernel registered"

echo.
goto :eof

REM ##############################################################################
REM Print Summary
REM ##############################################################################

:print_summary
call :print_header "Setup Complete!"

echo.
echo Environment Name: %ENV_NAME%
echo.
echo To activate the environment:
echo   conda activate %ENV_NAME%
echo.
echo Or use the quick activation script:
echo   activate_env.bat
echo.
echo To deactivate:
echo   conda deactivate
echo.
echo Next steps:
echo   1. Activate the environment
echo   2. Run: python quick_test.py
echo   3. Run: python complete_demo.py
echo.
echo For Jupyter notebooks:
echo   jupyter notebook
echo   (Select kernel: Python (%ENV_NAME%^)^)
echo.
goto :eof

REM ##############################################################################
REM Main Script
REM ##############################################################################

:main
call :print_header "Multi-Layered Security System - Conda Setup"
echo.

REM Run setup steps
call :check_conda
call :create_environment
call :verify_installation
call :create_activation_script

REM Optional: Run quick test
set /p "RUN_TEST=Do you want to run the quick test now? (y/N): "
if /i "!RUN_TEST!"=="y" (
    call :run_quick_test
)

call :print_summary

pause
exit /b 0

REM Run main function
:eof
call :main
