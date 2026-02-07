import os
import sys
import subprocess

# Function to handle module import
def ensure_module(module_name):
    try:
        __import__(module_name)
    except ModuleNotFoundError:
        print(f"{module_name} is not installed. Installing now...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.run([sys.executable, "-m", "pip", "install", module_name])

# Ensure Ollama is installed
ensure_module('Ollama')

# Import the Ollama module correctly
import ollama  # Renamed import to avoid conflict with variable name

def main():
    print(sys.path)
    # Your further code logic using ollama goes here
    pass

if __name__ == "__main__":
    main()