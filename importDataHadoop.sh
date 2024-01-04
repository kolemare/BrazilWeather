#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Set the path to your virtual environment
VENV_PATH="$SCRIPT_DIR/venv"

# Check if the virtual environment path exists
if [ -d "$VENV_PATH" ]; then
    echo "Activating the virtual environment..."
    source "$VENV_PATH/bin/activate"

    # Run your Python script
    echo "Running your Python script..."
    python "$SCRIPT_DIR/importDataHadoop.py"

    # Deactivate the virtual environment
    echo "Deactivating the virtual environment..."
    deactivate
else
    echo "Virtual environment not found at $VENV_PATH. Please set the correct path."
fi