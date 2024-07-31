#!/bin/bash

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependen#!/bin/bash

# Create a virtual environment
python3 -m venv venv

# Check if the virtual environment was created successfully
if [ ! -d "venv" ]; then
    echo "Failed to create virtual environment"
    exit 1
fi

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

echo "Setup complete. To activate the virtual environment, run 'source venv/bin/activate'."
cies
pip install -r requirements.txt

echo "Setup complete. To activate the virtual environment, run 'source venv/bin/activate'."
