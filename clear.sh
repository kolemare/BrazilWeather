#!/bin/bash

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

# Check the argument and act accordingly
case $1 in
    --all)
        delete_folder "dataset"
        delete_folder "hadoop"
        delete_folder "kafka"
        delete_folder "venv"
        delete_folder "airflow"
        ;;
    --dataset)
        delete_folder "dataset"
        ;;
    --hadoop)
        delete_folder "hadoop"
        ;;
    --kafka)
        delete_folder "kafka"
        ;;
    --venv)
        delete_folder "venv"
        ;;
    *)
        # Default action: remove hadoop, kafka, venv, and airflow
        delete_folder "hadoop"
        delete_folder "kafka"
        delete_folder "venv"
        delete_folder "airflow"
        ;;
esac