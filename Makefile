# Makefile for Multi-Layered Security System
# Simplifies common tasks for Linux/Mac users

.PHONY: help setup test demo clean install update activate jupyter

# Environment variables
ENV_NAME := quantum-security
PYTHON := python
CONDA := conda

# Default target
help:
	@echo "Multi-Layered Security System - Available Commands:"
	@echo ""
	@echo "  make setup      - Create conda environment and install all dependencies"
	@echo "  make install    - Install/reinstall packages in existing environment"
	@echo "  make test       - Run quick verification tests"
	@echo "  make demo       - Run complete demonstration"
	@echo "  make jupyter    - Start Jupyter notebook"
	@echo "  make activate   - Show activation command"
	@echo "  make update     - Update all packages"
	@echo "  make clean      - Remove environment and cached files"
	@echo ""
	@echo "First time setup:"
	@echo "  1. make setup"
	@echo "  2. conda activate $(ENV_NAME)"
	@echo "  3. make test"
	@echo "  4. make demo"
	@echo ""

# Create environment and install everything
setup:
	@echo "Creating conda environment: $(ENV_NAME)"
	@if [ -f environment.yml ]; then \
		$(CONDA) env create -f environment.yml; \
	else \
		$(CONDA) create -n $(ENV_NAME) python=3.10 -y; \
		$(CONDA) run -n $(ENV_NAME) $(CONDA) install -c conda-forge -y \
			numpy scipy matplotlib pillow opencv tqdm jupyter ipykernel; \
		$(CONDA) run -n $(ENV_NAME) $(CONDA) install -c pytorch -y pytorch torchvision cpuonly; \
		$(CONDA) run -n $(ENV_NAME) pip install \
			qiskit>=1.0.0 qiskit-aer>=0.13.0 pycryptodome>=3.19.0; \
	fi
	@echo ""
	@echo "✓ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  conda activate $(ENV_NAME)"
	@echo "  make test"

# Install/reinstall packages
install:
	@echo "Installing packages in $(ENV_NAME)..."
	@$(CONDA) run -n $(ENV_NAME) pip install --upgrade \
		qiskit qiskit-aer pycryptodome
	@echo "✓ Installation complete!"

# Run quick tests
test:
	@echo "Running verification tests..."
	@if [ -f quick_test.py ]; then \
		$(CONDA) run -n $(ENV_NAME) $(PYTHON) quick_test.py; \
	else \
		echo "quick_test.py not found!"; \
		exit 1; \
	fi

# Run complete demo
demo:
	@echo "Running complete demonstration..."
	@if [ -f complete_demo.py ]; then \
		$(CONDA) run -n $(ENV_NAME) $(PYTHON) complete_demo.py; \
	else \
		echo "complete_demo.py not found!"; \
		exit 1; \
	fi

# Start Jupyter notebook
jupyter:
	@echo "Starting Jupyter notebook..."
	@$(CONDA) run -n $(ENV_NAME) jupyter notebook

# Show activation command
activate:
	@echo "To activate the environment, run:"
	@echo ""
	@echo "  conda activate $(ENV_NAME)"
	@echo ""
	@echo "Or use:"
	@echo "  source activate_env.sh"

# Update all packages
update:
	@echo "Updating packages in $(ENV_NAME)..."
	@$(CONDA) run -n $(ENV_NAME) $(CONDA) update --all -y
	@$(CONDA) run -n $(ENV_NAME) pip install --upgrade \
		qiskit qiskit-aer pycryptodome
	@echo "✓ Update complete!"

# Clean environment and cache
clean:
	@echo "Removing conda environment: $(ENV_NAME)"
	@$(CONDA) env remove -n $(ENV_NAME) -y
	@$(CONDA) clean --all -y
	@echo "✓ Cleanup complete!"

# Check if environment exists
check-env:
	@$(CONDA) env list | grep -q $(ENV_NAME) || \
		(echo "Environment $(ENV_NAME) not found. Run 'make setup' first." && exit 1)

# Install with GPU support
setup-gpu:
	@echo "Creating conda environment with GPU support: $(ENV_NAME)"
	@$(CONDA) create -n $(ENV_NAME) python=3.10 -y
	@$(CONDA) run -n $(ENV_NAME) $(CONDA) install -c conda-forge -y \
		numpy scipy matplotlib pillow opencv tqdm jupyter ipykernel
	@$(CONDA) run -n $(ENV_NAME) $(CONDA) install -c pytorch -c nvidia -y \
		pytorch torchvision pytorch-cuda=11.8
	@$(CONDA) run -n $(ENV_NAME) pip install \
		qiskit>=1.0.0 qiskit-aer>=0.13.0 pycryptodome>=3.19.0
	@echo "✓ GPU setup complete!"

# Run individual components
run-qkd:
	@$(CONDA) run -n $(ENV_NAME) $(PYTHON) -c \
		"from multi_layer_security import E91QKD; \
		qkd = E91QKD(250); \
		k1, k2, chsh, t = qkd.run_protocol(); \
		print(f'Key: {k1[:20]}...'); \
		print(f'CHSH: {chsh:.4f}')"

run-crypto:
	@$(CONDA) run -n $(ENV_NAME) $(PYTHON) -c \
		"from multi_layer_security import CryptographicSystem; \
		crypto = CryptographicSystem(); \
		h = crypto.hash_key_sha256('test'); \
		print(f'Hash: {h[:32]}...')"

# Development targets
dev-install:
	@$(CONDA) run -n $(ENV_NAME) pip install \
		pytest black flake8 mypy ipython

format:
	@$(CONDA) run -n $(ENV_NAME) black *.py

lint:
	@$(CONDA) run -n $(ENV_NAME) flake8 *.py --max-line-length=100

# Info
info:
	@echo "Environment: $(ENV_NAME)"
	@echo "Python: $(PYTHON)"
	@echo "Conda: $(CONDA)"
	@echo ""
	@$(CONDA) env list | grep $(ENV_NAME) || echo "Environment not found"
	@echo ""
	@$(CONDA) run -n $(ENV_NAME) $(PYTHON) --version 2>/dev/null || echo "Environment not activated"
