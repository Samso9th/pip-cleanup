import os
import sys
import json as json_module
import subprocess
import click
from colorama import init, Fore, Style
from tabulate import tabulate
from typing import Dict, Set, List, Tuple
from .version import __version__
from .scanner import (
    get_installed_packages,
    find_imports_in_directory,
    get_package_size,
    format_size,
    get_project_requirements,
    generate_requirements
)

# Initialize colorama for Windows support
init()

def print_header():
    """Print the tool header."""
    click.echo("\n+--------------------------------------+")
    click.echo(Fore.GREEN + "|             PIP-CLEANUP              |" + Style.RESET_ALL)
    click.echo("|    Find and remove unused packages   |")
    click.echo("+--------------------------------------+\n")
    click.echo(Fore.GREEN + "Pip package remover tool by @samso9th\n" + Style.RESET_ALL)

def get_unused_packages(root_dir: str, exclude_dirs: set = None, quiet: bool = False) -> List[Tuple[str, str, str]]:
    """
    Get a list of unused packages with their versions and sizes.
    Returns a list of tuples (package_name, version, size).
    """
    if not quiet:
        if not sys.stdout.isatty():
            # Non-interactive mode, don't use emojis
            click.echo("Scanning for installed packages...")
        else:
            # Interactive mode with emojis
            click.echo(Fore.YELLOW + "\nScanning for installed packages..." + Style.RESET_ALL)
    
    installed_packages = get_installed_packages()
    
    if not quiet:
        if not sys.stdout.isatty():
            click.echo("Scanning for imports in your code...")
        else:
            click.echo(Fore.YELLOW + "Scanning for imports in your code..." + Style.RESET_ALL)
    
    used_packages = find_imports_in_directory(root_dir, exclude_dirs)
    
    if not quiet:
        if not sys.stdout.isatty():
            click.echo("Checking project requirements...")
        else:
            click.echo(Fore.YELLOW + "Checking project requirements..." + Style.RESET_ALL)
    
    required_packages = get_project_requirements(root_dir)
    
    # Get unused packages with their details
    unused_packages = []
    essential_packages = {'pip', 'setuptools', 'wheel', 'pip-cleanup'}
    
    for package, version in installed_packages.items():
        # Skip if package is:
        # 1. Being used in code
        # 2. Listed in requirements
        # 3. An essential package
        if (package not in used_packages and 
            package not in required_packages and 
            package not in essential_packages):
            size = get_package_size(package)
            size_str = format_size(size) if size else "Unknown"
            unused_packages.append((package, version, size_str))
    
    return sorted(unused_packages, key=lambda x: x[0].lower())

def display_packages(packages: List[Tuple[str, str, str]]):
    """Display packages in a formatted table."""
    if not packages:
        click.echo(Fore.GREEN + "\nNo unused packages found!" + Style.RESET_ALL)
        return
    
    headers = ["#", "Package", "Version", "Size"]
    table_data = [
        [idx + 1, Fore.CYAN + pkg + Style.RESET_ALL, ver, size]
        for idx, (pkg, ver, size) in enumerate(packages)
    ]
    
    click.echo("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))

def confirm_deletion(packages: List[Tuple[str, str, str]]) -> List[str]:
    """Get user confirmation for package deletion."""
    if not sys.stdout.isatty():
        click.echo("\nSkipping package deletion in non-interactive mode.")
        return []
    
    while True:
        click.echo("\nEnter package numbers to uninstall (comma-separated, e.g. 1,3,5), 'all', or 'q' to quit: ")
        choice = click.prompt("").strip().lower()
        
        if choice == 'q':
            return []
            
        if choice == 'all':
            return [pkg[0] for pkg in packages]
            
        try:
            indices = [int(i.strip()) - 1 for i in choice.split(',')]
            selected = []
            for idx in indices:
                if 0 <= idx < len(packages):
                    selected.append(packages[idx][0])
                else:
                    click.echo(Fore.RED + f"Invalid package number: {idx + 1}" + Style.RESET_ALL)
                    break
            else:
                if selected:
                    click.echo("\nSelected packages:")
                    for pkg in selected:
                        click.echo(f"  - {pkg}")
                    if click.confirm("\nProceed with uninstallation?"):
                        return selected
        except ValueError:
            click.echo(Fore.RED + "Invalid input. Please enter numbers separated by commas." + Style.RESET_ALL)

def uninstall_packages(packages: List[str]):
    """Uninstall the specified packages."""
    click.echo("\nUninstalling packages...")
    
    for pkg in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", pkg])
    
    click.echo("\nUninstallation complete!")

def generate_requirements(root_dir: str, unused_packages: List[Tuple[str, str, str]], quiet: bool = False) -> bool:
    """Generate requirements.txt with only used packages."""
    try:
        if os.path.exists(os.path.join(root_dir, "requirements.txt")):
            if quiet:
                return False
            
            if not click.confirm("\nrequirements.txt already exists. Do you want to overwrite it?", default=False):
                if not quiet:
                    click.echo("\nSkipping requirements.txt generation.")
                return False
        
        installed = get_installed_packages()
        unused_names = {pkg[0] for pkg in unused_packages}
        
        with open(os.path.join(root_dir, "requirements.txt"), "w") as f:
            for pkg, version in installed.items():
                if pkg not in unused_names:
                    f.write(f"{pkg}=={version}\n")
        
        if not quiet:
            click.echo(Fore.GREEN + "\nGenerated requirements.txt with only used packages!" + Style.RESET_ALL)
        return True
    except Exception as e:
        if not quiet:
            click.echo(Fore.RED + f"\nError generating requirements.txt: {str(e)}" + Style.RESET_ALL)
        return False

@click.command()
@click.argument('path', default='.', type=click.Path(exists=True))
@click.option('--version','-v', is_flag=True, help='Show version information.')
@click.option('--exclude','-e', multiple=True, help='Directories to exclude from scanning.')
@click.option('--ignore','-i', multiple=True, help='Packages to ignore when finding unused packages.')
@click.option('--requirements','-r', is_flag=True, help='Generate requirements.txt with only used packages.')
@click.option('--json','-J', is_flag=True, help='Output results in JSON format.')
@click.option('--quiet','-q', is_flag=True, help='Suppress non-essential output.')
@click.option('-d', '--deep', is_flag=True, help='Scan for all Python environments and let user select one.')
@click.option('-l', '--logs', is_flag=True, help='Show detailed logs during environment scanning.')
def main(path, version=False, exclude=(), ignore=(), requirements=False,
         json=False, quiet=False, deep=False, logs=False):
    """Find and remove unused pip packages in your Python projects."""
    if version:
        click.echo(f"pip-cleanup version {__version__}")
        sys.exit(0)
    
    if not quiet:
        print_header()
    
    if deep:
        # Find all Python environments
        from .env_scanner import find_python_environments, select_environment
        
        try:
            environments = find_python_environments(show_logs=logs)
            
            if not environments:
                click.echo(Fore.RED + "\nNo Python environments found!" + Style.RESET_ALL)
                sys.exit(1)
                
            click.echo("\nFound Python environments:")
            for i, (env_path, env_name) in enumerate(environments, 1):
                click.echo(f"{i}. {env_name}")
                click.echo(f"   Path: {env_path}")
            
            python_path = select_environment(environments)
            # Update sys.executable to use the selected environment's Python
            sys.executable = os.path.join(python_path, "Scripts", "python.exe") if os.name == "nt" else os.path.join(python_path, "bin", "python")
        except Exception as e:
            click.echo(Fore.RED + f"\nError scanning environments: {str(e)}" + Style.RESET_ALL)
            sys.exit(1)
    
    # Validate directory
    if not os.path.isdir(path):
        click.echo(Fore.RED + f"Error: Directory '{path}' does not exist." + Style.RESET_ALL)
        sys.exit(1)
    
    # Get and display unused packages
    exclude_dirs = set(exclude) if exclude else None
    unused_packages = get_unused_packages(path, exclude_dirs, quiet)
    
    # Filter out ignored packages
    if ignore:
        unused_packages = [pkg for pkg in unused_packages if pkg[0] not in ignore]
    
    if json:
        result = {
            "unused_packages": [
                {"name": pkg[0], "version": pkg[1], "size": pkg[2]}
                for pkg in unused_packages
            ]
        }
        click.echo(json_module.dumps(result, indent=2))
        return
    
    display_packages(unused_packages)
    
    if unused_packages:
        if requirements:
            if not generate_requirements(path, unused_packages, quiet):
                if not quiet:
                    click.echo(Fore.RED + "\nrequirements.txt not generated" + Style.RESET_ALL)
        else:
            # Get user selection and uninstall
            to_uninstall = confirm_deletion(unused_packages)
            if to_uninstall:
                uninstall_packages(to_uninstall)

if __name__ == "__main__":
    main()