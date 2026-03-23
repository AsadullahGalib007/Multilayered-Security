# 🚀 Quick Reference Card

## Installation Methods - Choose One

### ⭐ Method 1: Automated Setup (Recommended)

#### Windows (Command Prompt/PowerShell)
```cmd
# Option A: Batch script (Command Prompt)
setup_conda_env.bat

# Option B: PowerShell script
.\setup_conda_env.ps1
```

#### Linux/Mac (Terminal)
```bash
chmod +x setup_conda_env.sh
./setup_conda_env.sh
```

---

### 📝 Method 2: Using environment.yml
```bash
conda env create -f environment.yml
conda activate quantum-security
python quick_test.py
```

---

### 🛠️ Method 3: Using Makefile (Linux/Mac)
```bash
make setup
conda activate quantum-security
make test
make demo
```

---

### 💻 Method 4: Manual Installation
```bash
# Create environment
conda create -n quantum-security python=3.10 -y

# Activate
conda activate quantum-security

# Install packages
conda install -c conda-forge -y numpy scipy matplotlib pillow opencv tqdm jupyter
conda install -c pytorch -y pytorch torchvision cpuonly
pip install qiskit qiskit-aer pycryptodome

# Test
python quick_test.py
```

---

## Common Commands

### Environment Management
```bash
# Activate environment
conda activate quantum-security

# Deactivate
conda deactivate

# List environments
conda env list

# Remove environment
conda env remove -n quantum-security
```

### Running Programs
```bash
# Quick test
python quick_test.py

# Complete demo
python complete_demo.py

# Jupyter notebook
jupyter notebook
```

### Package Management
```bash
# List packages
conda list

# Update all
conda update --all

# Install new package
pip install package-name
```

---

## File Overview

| File | Purpose |
|------|---------|
| `environment.yml` | Conda environment specification |
| `setup_conda_env.sh` | Automated setup (Linux/Mac) |
| `setup_conda_env.bat` | Automated setup (Windows CMD) |
| `setup_conda_env.ps1` | Automated setup (Windows PowerShell) |
| `Makefile` | Make commands (Linux/Mac) |
| `requirements.txt` | Pip requirements |
| `activate_env.*` | Quick activation scripts |

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "conda not found" | Install Anaconda/Miniconda, restart terminal |
| "Import error" | Activate environment: `conda activate quantum-security` |
| "Environment exists" | Remove: `conda env remove -n quantum-security` |
| GPU not detected | Install CUDA PyTorch: `conda install pytorch torchvision pytorch-cuda=11.8 -c pytorch -c nvidia` |
| Out of memory | Use smaller test images or fewer singlets |

---

## Activation Scripts

After setup, quickly activate with:

**Windows:**
- `activate_env.bat` (Command Prompt)
- `.\activate_env.ps1` (PowerShell)

**Linux/Mac:**
- `source activate_env.sh`

---

## Make Commands (Linux/Mac)

```bash
make setup      # Create environment
make test       # Run tests
make demo       # Run demo
make jupyter    # Start Jupyter
make clean      # Remove environment
make update     # Update packages
```

---

## Verification Checklist

- [ ] Conda installed: `conda --version`
- [ ] Environment created: `conda env list | grep quantum-security`
- [ ] Environment activated: prompt shows `(quantum-security)`
- [ ] Python 3.10+: `python --version`
- [ ] Qiskit works: `python -c "import qiskit"`
- [ ] PyTorch works: `python -c "import torch"`
- [ ] Tests pass: `python quick_test.py`

---

## System Requirements

**Minimum:**
- RAM: 4 GB
- Storage: 2 GB
- Python: 3.10+

**Recommended:**
- RAM: 8 GB+
- Storage: 5 GB
- Multi-core CPU
- GPU: Optional (NVIDIA with CUDA)

---

## Important Notes

1. **First Time Setup:**
   - Install Conda first (Anaconda or Miniconda)
   - Restart terminal after Conda installation
   - Run setup script
   - Activate environment before use

2. **Every Session:**
   - Must activate environment: `conda activate quantum-security`
   - Or use activation script: `activate_env.*`

3. **GPU Support:**
   - Requires NVIDIA GPU with CUDA
   - Use `setup_conda_env.ps1 -GPU` or modify environment.yml
   - Verify: `python -c "import torch; print(torch.cuda.is_available())"`

---

## Getting Help

1. Read `INSTALLATION.md` for detailed guide
2. Run diagnostics: `conda info && conda list`
3. Check environment: `conda activate quantum-security && python --version`
4. Test imports: `python quick_test.py`

---

## Next Steps After Installation

1. ✅ Activate environment
2. ✅ Run `python quick_test.py`
3. ✅ Run `python complete_demo.py`
4. ✅ Explore `README.md` for usage examples
5. ✅ Try `jupyter notebook` for interactive use

---

**Quick Start (3 Commands):**
```bash
conda env create -f environment.yml
conda activate quantum-security
python complete_demo.py
```

🎉 **That's it! You're ready to go!**
