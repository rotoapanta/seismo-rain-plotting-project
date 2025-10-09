#!/bin/bash
# This script sets up the project environment, assuming you are in the project directory.

echo "===================================================="
echo "         Environment Setup Script"
echo "===================================================="
echo ""

echo "[1] Creating conda environment named 'seismic-rain-plotting-env'..."
conda create --name seismic-rain-plotting-env python=3.11 -y
echo ""
echo "[1] Complete."
echo ""

echo "[2] Installing dependencies from requirements.txt..."
# Using conda run to execute pip in the new environment
conda run -n seismic-rain-plotting-env pip install -r requirements.txt
echo ""
echo "[2] Complete."
echo ""

echo "[3] Verifying installed packages..."
conda run -n seismic-rain-plotting-env python -m pip list
echo ""
echo "[3] Complete."
echo ""

echo "===================================================="
echo "                 Setup complete!"
echo "===================================================="
echo "To activate the new environment, run the following command:"
echo "conda activate seismic-rain-plotting-env"
