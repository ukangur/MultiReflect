#!/bin/bash

# MultiReflect-2 Setup Script

echo "=== Starting MultiReflect-2 Setup ==="

# Step 1: Create and activate the 'multi_reflect' environment
echo "Step 1: Creating and activating the 'multi_reflect' conda environment..."
conda create --name multi_reflect python=3.9 -y
source activate multi_reflect

# Step 2: Install dependencies from requirements.txt
echo "Step 2: Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Error: requirements.txt not found!"
    exit 1
fi

# Step 3: Download necessary language model for spaCy (if applicable)
echo "Step 3: Downloading spaCy language model (en)..."
python -m spacy download en

# Step 4: Run the main script
echo "Step 4: Running the main script..."
if [ -f "main.py" ]; then
    python main.py
else
    echo "Error: main.py not found!"
    exit 1
fi

echo "=== MultiReflect-2 Setup Complete ==="
