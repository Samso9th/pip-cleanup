"""Environment scanner for pip-cleanup."""
import os
import sys
from typing import List, Tuple
import subprocess

def is_valid_python_env(path: str, is_conda: bool = False, show_logs: bool = False) -> bool:
    """Check if path contains a valid Python environment."""
    # Try multiple possible locations for pip and python
    pip_locations = [
        os.path.join(path, "Scripts", "pip.exe") if os.name == "nt" else os.path.join(path, "bin", "pip"),
        os.path.join(path, "pip.exe") if os.name == "nt" else os.path.join(path, "pip"),
    ]
    
    python_locations = [
        os.path.join(path, "python.exe") if os.name == "nt" else os.path.join(path, "python"),
        os.path.join(path, "Scripts", "python.exe") if os.name == "nt" else os.path.join(path, "bin", "python"),
    ]
    
    if is_conda:
        # For conda environments, prefer the root directory python first
        python_locations.reverse()
    
    # Find pip and python executables
    pip_path = next((p for p in pip_locations if os.path.exists(p)), None)
    python_path = next((p for p in python_locations if os.path.exists(p)), None)
    
    # Debug output only if show_logs is True
    if show_logs:
        print(f"  Checking environment at: {path}")
        print(f"    Looking for pip in: {', '.join(pip_locations)}")
        print(f"    Looking for python in: {', '.join(python_locations)}")
        print(f"    Found pip at: {pip_path}")
        print(f"    Found python at: {python_path}")
    
    return pip_path is not None and python_path is not None

def get_env_name(path: str) -> str:
    """Get a friendly name for the environment."""
    try:
        # Try to get Python version
        python_path = os.path.join(path, "python.exe") if os.name == "nt" else os.path.join(path, "bin", "python")
        if not os.path.exists(python_path):
            python_path = os.path.join(path, "Scripts", "python.exe") if os.name == "nt" else os.path.join(path, "bin", "python")
            
        result = subprocess.run([python_path, "--version"], capture_output=True, text=True)
        version = result.stdout.strip() if result.stdout else "Unknown Python"
        
        # Get the last part of the path as env name
        env_name = os.path.basename(path)
        if env_name.lower() in ("scripts", "bin"):
            env_name = os.path.basename(os.path.dirname(path))
            
        return f"{env_name} ({version})"
    except:
        return os.path.basename(path)

def find_python_environments(show_logs: bool = False) -> List[Tuple[str, str]]:
    """Find all Python environments on the system."""
    environments = []
    
    # Add current environment
    environments.append((sys.prefix, "Current Environment"))
    
    # Common environment locations
    search_paths = []
    
    if os.name == "nt":  # Windows
        # Add standard Python paths
        search_paths.extend([
            os.path.expanduser("~\\AppData\\Local\\Programs\\Python"),  # Python installations
            os.path.expanduser("~\\.virtualenvs"),  # virtualenvwrapper
            os.path.expanduser("~\\AppData\\Local\\conda"),  # Conda environments
            os.path.join(os.getcwd(), "venv"),      # Local venv
            os.path.join(os.getcwd(), ".venv"),     # Local .venv
        ])
        
        # Add Anaconda/Miniconda paths
        conda_paths = [
            os.path.expanduser("~\\Anaconda3"),
            os.path.expanduser("~\\miniconda3"),
        ]
        
        for conda_path in conda_paths:
            if os.path.exists(conda_path):
                # Add base environment
                search_paths.append(conda_path)
                # Add envs directory
                envs_dir = os.path.join(conda_path, "envs")
                if os.path.exists(envs_dir):
                    if show_logs:
                        print(f"\nScanning Conda environments in: {envs_dir}")
                    try:
                        for env_name in os.listdir(envs_dir):
                            env_path = os.path.join(envs_dir, env_name)
                            if os.path.isdir(env_path) and is_valid_python_env(env_path, is_conda=True, show_logs=show_logs):
                                if show_logs:
                                    print(f"Found Conda environment: {env_name}")
                                environments.append((env_path, f"Conda: {env_name}"))
                    except Exception as e:
                        if show_logs:
                            print(f"Error scanning Conda envs: {e}")
    else:  # Unix-like
        search_paths.extend([
            "/usr/local/bin",
            "/usr/bin",
            os.path.expanduser("~/.virtualenvs"),
            os.path.join(os.getcwd(), "venv"),
            os.path.join(os.getcwd(), ".venv"),
        ])
        
        # Add Anaconda/Miniconda paths for Unix
        conda_paths = [
            os.path.expanduser("~/anaconda3"),
            os.path.expanduser("~/miniconda3"),
        ]
        
        for conda_path in conda_paths:
            if os.path.exists(conda_path):
                search_paths.append(conda_path)
                envs_dir = os.path.join(conda_path, "envs")
                if os.path.exists(envs_dir):
                    for env_name in os.listdir(envs_dir):
                        env_path = os.path.join(envs_dir, env_name)
                        if os.path.isdir(env_path) and is_valid_python_env(env_path, is_conda=True, show_logs=show_logs):
                            environments.append((env_path, f"Conda: {env_name}"))
    
    if show_logs:
        print("\nSearching in paths:")  # Debug output
    for path in search_paths:
        if show_logs:
            print(f"- {path}")
        if not os.path.exists(path):
            if show_logs:
                print("  (not found)")
            continue
            
        # Check if base_path itself is an environment
        if is_valid_python_env(path, show_logs=show_logs):
            if show_logs:
                print("  Found environment!")
            environments.append((path, get_env_name(path)))
            
        # Look for environments in subdirectories
        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path) and is_valid_python_env(full_path, show_logs=show_logs):
                    if show_logs:
                        print(f"  Found environment in {item}!")
                    environments.append((full_path, get_env_name(full_path)))
        except Exception as e:
            if show_logs:
                print(f"  Error scanning: {e}")
            continue
            
    # Look for local venv/virtualenv directories
    local_env_names = ["venv", ".venv", "env", ".env"]
    cwd = os.getcwd()
    for env_name in local_env_names:
        env_path = os.path.join(cwd, env_name)
        if os.path.isdir(env_path) and is_valid_python_env(env_path, show_logs=show_logs):
            environments.append((env_path, f"Local {env_name}"))
    
    return environments

def select_environment(environments: List[Tuple[str, str]]) -> str:
    """Let user select a Python environment."""
    while True:
        try:
            choice = input("\nEnter environment number or 'q' to quit [q]: ").strip()
            if not choice or choice.lower() == 'q':
                sys.exit(0)
                
            choice_num = int(choice)
            if 1 <= choice_num <= len(environments):
                return environments[choice_num - 1][0]
            else:
                print(f"Please enter a number between 1 and {len(environments)}")
        except ValueError:
            print("Please enter a valid number")
        except (KeyboardInterrupt, EOFError):
            print("\nAborted!")
            sys.exit(1)
