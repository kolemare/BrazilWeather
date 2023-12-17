#!/bin/bash

# Update package list
echo "Updating package list..."
sudo apt update -y

# Install Python 3.10 if it's not installed
if ! command -v python3.10 &> /dev/null; then
    echo "Python 3.10 not found. Installing Python 3.10..."
    sudo apt install -y python3.10
fi

# Install python3.10-venv to ensure the venv module works correctly
echo "Installing python3.10-venv..."
sudo apt install -y python3.10-venv

# Set the name of the virtual environment
VENV_NAME="venv"

# Create virtual environment
echo "Creating virtual environment..."
python3.10 -m venv $VENV_NAME

# Check if the activate script exists
if [ ! -f "$VENV_NAME/bin/activate" ]; then
    echo "The virtual environment was not created successfully."
    echo "The 'activate' script does not exist in the 'bin' directory."
    exit 1
fi

# Activate the virtual environment
echo "Activating the virtual environment..."
source $VENV_NAME/bin/activate

# Upgrade pip to the latest version
pip install --upgrade pip

# Install required libraries
echo "Installing required libraries..."
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2

# Deactivate the virtual environment
echo "Deactivating the virtual environment..."
deactivate

echo "Virtual environment setup is complete."
