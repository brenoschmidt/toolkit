
import os
import sys
import subprocess

VENV_DIR = "venv"
PYTHON_EXEC = sys.executable  # Gets the correct Python interpreter

def run_command(command):
    """Run a shell command and handle errors."""
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print("❌ Error: Command failed.")
        sys.exit(1)

def setup_virtualenv():
    """Ensure the virtual environment is correctly set up."""
    if not os.path.exists(VENV_DIR):
        print("🔧 Creating virtual environment...")
        run_command(f"{PYTHON_EXEC} -m venv {VENV_DIR}")

    # Activate environment and install dependencies
    if sys.platform == "win32":
        activate_script = os.path.join(VENV_DIR, "Scripts", "activate")
        pip_exec = os.path.join(VENV_DIR, "Scripts", "pip")
    else:
        activate_script = os.path.join(VENV_DIR, "bin", "activate")
        pip_exec = os.path.join(VENV_DIR, "bin", "pip")

    print("✅ Virtual environment is set up.")
    print("🔄 Installing dependencies...")
    run_command(f"{pip_exec} install -r requirements.txt")

    print("\n🚀 Setup complete! Activate the environment using:")
    print(f"  Windows: {activate_script}")
    print(f"  macOS/Linux: source {activate_script}\n")

if __name__ == "__main__":
    setup_virtualenv()
