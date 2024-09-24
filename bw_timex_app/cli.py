import subprocess
import sys
import os

def main():
    # Get the absolute path to the app.py script
    app_path = os.path.join(os.path.dirname(__file__), "project_selection.py")
    
    # Run the Streamlit app using subprocess
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
