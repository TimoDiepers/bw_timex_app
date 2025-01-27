import subprocess
import sys
import os

def main():
    app_path = os.path.join(os.path.dirname(__file__), "welcome.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
