import os
import subprocess
import sys

def create_virtualenv(venv_path):
    """Create a virtual environment."""
    if not os.path.exists(venv_path):
        print("Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_path])
        print("Virtual environment created.")
    else:
        print("Virtual environment already exists.")

def install_requirements(venv_path, requirements_file):
    """Install the requirements using pip inside the virtual environment."""
    pip_path = os.path.join(venv_path, "Scripts", "pip") if os.name == "nt" else os.path.join(venv_path, "bin", "pip")
    
    print("Installing requirements...")
    subprocess.check_call([pip_path, "install", "-r", requirements_file])
    print("Requirements installed successfully.")

def generate_requirements(script_path, output_file="requirements.txt"):
    """Generate a requirements file for the script."""
    print("Generating requirements...")
    required_packages = [
        "tqdm",
        "watchdog",
        "safetensors"
    ]
    with open(output_file, "w") as f:
        for package in required_packages:
            f.write(f"{package}\n")
    print(f"Requirements file '{output_file}' created.")

if __name__ == "__main__":
    # Configuration
    script_name = "tagfreq_class.py"
    venv_directory = "venv"
    requirements_file = "requirements.txt"

    # Ensure requirements.txt exists
    generate_requirements(script_name, requirements_file)

    # Create virtual environment
    create_virtualenv(venv_directory)

    # Install requirements
    install_requirements(venv_directory, requirements_file)

    print(f"Setup complete! Activate the virtual environment by running:")
    if os.name == "nt":
        print(f"  {venv_directory}\\Scripts\\activate")
    else:
        print(f"  source {venv_directory}/bin/activate")
    print(f"Then, you can run '{script_name}' inside the virtual environment.")
