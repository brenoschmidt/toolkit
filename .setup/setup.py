import os
import sys
import subprocess

SETUP_DIR = os.path.dirname(os.path.abspath(__file__))  # Path to .setup/
PROJECT_DIR = os.path.abspath(os.path.join(SETUP_DIR, ".."))  # Root project folder
VENV_DIR = os.path.join(PROJECT_DIR, ".venv")  # Hidden virtual environment path

PYTHON_EXEC = sys.executable  # Detects current Python version

def run_command(command):
    """Run a shell command and handle errors."""
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print("❌ Error: Command failed.")
        sys.exit(1)

def setup_virtualenv():
    """Ensure the virtual environment is correctly set up."""
    if not os.path.exists(VENV_DIR):
        print("🔧 Creating virtual environment (.venv)...")
        run_command(f"{PYTHON_EXEC} -m venv {VENV_DIR}")

    # Determine paths for activation and pip
    if sys.platform == "win32":
        activate_script = os.path.join(VENV_DIR, "Scripts", "activate")
        pip_exec = os.path.join(VENV_DIR, "Scripts", "pip")
    else:
        activate_script = os.path.join(VENV_DIR, "bin", "activate")
        pip_exec = os.path.join(VENV_DIR, "bin", "pip")

    #pip install --upgrade --force-reinstall -r requirements.txt
    print("✅ Virtual environment is set up.")
    print("🔄 Installing dependencies...")
    run_command(f"{pip_exec} install -r --upgrade {os.path.join(SETUP_DIR, 'requirements.txt')}")

    print("\n🚀 Setup complete! Activate the environment using:")
    print(f"  Windows: {activate_script}")
    print(f"  macOS/Linux: source {activate_script}\n")

def main():
    if os.path.exists(os.path.join(VENV_DIR, "Scripts", "activate")) \
            or os.path.exists(os.path.join(VENV_DIR, "bin", "activate")):
        return
    else:
        setup_virtualenv()
if __name__ == "__main__":
    main()
