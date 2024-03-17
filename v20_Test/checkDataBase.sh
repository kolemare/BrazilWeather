#!/bin/bash

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Specify the path to the virtual environment in the root directory
VENV_PATH="$SCRIPT_DIR/../venv"

if [ -d "$VENV_PATH" ]; then
    echo "Activating the virtual environment..."
    source "$VENV_PATH/bin/activate"

    # Run your Python script
    echo "Running your Python script..."
    python "$SCRIPT_DIR/checkDataBase.py"

    # Deactivate the virtual environment
    echo "Deactivating the virtual environment..."
    deactivate
else
    echo "Virtual environment not found at $VENV_PATH. Please set the correct path."
fi