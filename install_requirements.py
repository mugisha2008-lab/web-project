import subprocess
import sys
import os

def install_requirements():
    """Install Python requirements"""
    try:
        print("Installing Python dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False

if __name__ == "__main__":
    if install_requirements():
        print("Starting backend server...")
        try:
            subprocess.check_call([sys.executable, "app.py"])
        except KeyboardInterrupt:
            print("\nServer stopped by user.")
        except Exception as e:
            print(f"Error starting server: {e}")
