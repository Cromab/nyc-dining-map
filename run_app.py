import os
import subprocess
import sys

def run_streamlit_app():
    filename = "🏠_Home.py"
    
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        sys.exit(1)
    
    try:
        subprocess.run(["streamlit", "run", filename], check=True)
    except subprocess.CalledProcessError as e:
        print("Error running streamlit app", e)

if __name__ == "__main__":
    run_streamlit_app()