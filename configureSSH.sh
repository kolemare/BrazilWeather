#!/bin/bash

# SSH Configuration
SSH_DIR="$HOME/.ssh"
KEY_FILE="$SSH_DIR/id_rsa"

# Check and install SSH server if not already installed
if ! systemctl is-active --quiet ssh; then
    echo "Installing SSH server..."
    sudo apt-get update
    sudo apt-get install -y openssh-server
    sudo systemctl start ssh
    echo "SSH server installed and started."
fi

# Create SSH directory if it doesn't exist
if [ ! -d "$SSH_DIR" ]; then
    echo "Creating SSH directory..."
    mkdir -p "$SSH_DIR"
    chmod 700 "$SSH_DIR"
fi

# Generate SSH key if it doesn't exist
if [ ! -f "$KEY_FILE" ]; then
    echo "Generating SSH key..."
    ssh-keygen -t rsa -P '' -f "$KEY_FILE"
    echo "SSH key generated."
fi

# Add key to authorized_keys for passwordless SSH to localhost
if ! grep -q "$(cat "$KEY_FILE.pub")" "$SSH_DIR/authorized_keys" 2>/dev/null; then
    echo "Configuring passwordless SSH to localhost..."
    cat "$KEY_FILE.pub" >> "$SSH_DIR/authorized_keys"
    chmod 600 "$SSH_DIR/authorized_keys"
    echo "Passwordless SSH to localhost configured."
else
    echo "Passwordless SSH to localhost is already configured."
fi

echo "SSH configuration completed."
