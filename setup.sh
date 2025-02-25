#!/bin/bash

# Step 1: Update and install system dependencies
echo "Updating system and installing dependencies..."
sudo apt update
sudo apt install -y python3-venv ffmpeg imagemagick

# Step 2: Create a virtual environment
echo "Creating a virtual environment..."
python3 -m venv telegram-bot-env

# Step 3: Activate the virtual environment
echo "Activating the virtual environment..."
source telegram-bot-env/bin/activate

# Step 4: Upgrade pip and install Python packages
echo "Installing Python packages..."
pip install --upgrade pip
pip install python-telegram-bot gdown opencv-python numpy moviepy tqdm instagrapi

# Step 5: Create a requirements file
echo "Creating requirements.txt..."
pip freeze > requirements.txt

# Step 6: Deactivate the virtual environment
echo "Deactivating the virtual environment..."
deactivate

# Step 7: Provide instructions to the user
echo ""
echo "Setup complete! To run the bot, follow these steps:"
echo "1. Activate the virtual environment:"
echo "   source telegram-bot-env/bin/activate"
echo "2. Run the bot script:"
echo "   python3 your_script_name.py"
echo "3. Deactivate the virtual environment when done:"
echo "   deactivate"
