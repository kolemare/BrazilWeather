#!/bin/bash

# Get the directory of the script
SCRIPT_DIR=$(dirname "$(realpath "$BASH_SOURCE")")

# Function to delete a folder if it exists
delete_folder() {
    FOLDER=$1
    if [ -d "$FOLDER" ]; then
        echo "Removing $FOLDER..."
        rm -rf "$FOLDER"
    else
        echo "$FOLDER does not exist or has already been removed."
    fi
}

# Function to delete the contents of a folder if it exists
delete_contents() {
    FOLDER=$1
    if [ -d "$FOLDER" ]; then
        echo "Removing contents of $FOLDER..."
        rm -rf "$FOLDER"/*
    else
        echo "$FOLDER does not exist."
    fi
}

# Check the argument and act accordingly
case $1 in
    --all)
        delete_contents "$SCRIPT_DIR/../v30_Dataset"
        delete_folder "$SCRIPT_DIR/../v40_Libraries/hadoop"
        delete_folder "$SCRIPT_DIR/../v40_Libraries/kafka"
        delete_folder "$SCRIPT_DIR/../venv"
        delete_folder "$SCRIPT_DIR/../v40_Libraries/airflow"
        ;;
    --dataset)
        delete_contents "$SCRIPT_DIR/../v30_Dataset"
        ;;
    --hadoop)
        delete_folder "$SCRIPT_DIR/../v40_Libraries/hadoop"
        ;;
    --kafka)
        delete_folder "$SCRIPT_DIR/../v40_Libraries/kafka"
        ;;
    --venv)
        delete_folder "$SCRIPT_DIR/../venv"
        ;;
    *)
        # Default action: remove hadoop, kafka, venv, and airflow
        delete_folder "$SCRIPT_DIR/../v40_Libraries/hadoop"
        delete_folder "$SCRIPT_DIR/../v40_Libraries/kafka"
        delete_folder "$SCRIPT_DIR/../venv"
        delete_folder "$SCRIPT_DIR/../v40_Libraries/airflow"
        ;;
esac