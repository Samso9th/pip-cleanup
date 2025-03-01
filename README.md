# pip-cleanup 

A Python tool to clean up unused pip packages from your Python environment.

## Features

- Scans your Python project for imported packages
- Compares against installed packages
- Identifies unused dependencies
- Interactive removal of unused packages
- Generates requirements.txt with only used packages
- Supports JSON output for automation
- Configurable directory exclusions and package ignores

## Installation

```bash
pip install pip-cleanup
```

Linux/MacOS users can also install using pipx for better isolation:

```bash
pipx install pip-cleanup
```

## Usage

1. Navigate to your Python project directory or activated environment

2. Run pip-cleanup:

```bash
pip-cleanup
```

### Available Options

```bash
# Show help message and available options
pip-cleanup --help

# Check version (any of these work)
pip-cleanup -v
pip-cleanup --version

# Scan a specific directory
pip-cleanup --path /path/to/project
pip-cleanup -p /path/to/project

# Exclude directories from scanning
pip-cleanup --exclude tests --exclude docs
pip-cleanup -e tests -e docs

# Ignore specific packages
pip-cleanup --ignore pytest --ignore black
pip-cleanup -i pytest -i black

# Generate requirements.txt with only used packages
pip-cleanup --requirements
pip-cleanup -r

# Output in JSON format (useful for scripting)
pip-cleanup --json

# Scan system for all Python environments and choose one
pip-cleanup --deep
pip-cleanup -d

# Show detailed logs during deep environment scanning (requires --deep)
pip-cleanup -d --logs
pip-cleanup --deep -l

# Suppress non-essential output
pip-cleanup --quiet
pip-cleanup -q
```

### How It Works

1. **Project Scanning**: The tool scans your Python files for import statements
2. **Package Analysis**: Compares found imports against installed packages
3. **Smart Detection**: 
   - Handles both direct imports (import numpy) and from imports (from PIL import Image)
   - Recognizes common package aliases (e.g., PIL -> pillow)
   - Excludes standard library packages
4. **Interactive Cleanup**: Lets you choose which packages to remove
5. **Requirements Generation**: Can create requirements.txt with only used packages
6. **JSON Output**: Can return output in parsable JSON format for development/automation purposes

## Example Output

```
╔═══════════════════════════════════════╗
║          📦 PIP-CLEANUP 📦           ║
║    Find and remove unused packages    ║
╚═══════════════════════════════════════╝

💻 Pip package remover tool by @samso9th

🔍 Scanning for installed packages...
🔍 Scanning for imports in your code...
🔍 Checking project requirements...

+-----+--------------------+-------------+---------+
|   # | Package            | Version     | Size    |
+=====+====================+=============+=========+
|   1 | numpy              | 2.2.3       | 34.4MB  |
+-----+--------------------+-------------+---------+
|   2 | pandas             | 2.2.3       | 43.1MB  |
+-----+--------------------+-------------+---------+
|   3 | requests           | 2.32.3      | 408.7KB |
+-----+--------------------+-------------+---------+

Enter package numbers to uninstall (comma-separated, e.g. 1,3,5), 'all', or 'q' to quit:
```

You can:
- Enter numbers like `1,2` to select specific packages
- Type `all` to select all packages
- Type `q` to quit without uninstalling

## Notes

- Essential packages (pip, setuptools, wheel) are automatically excluded
- The tool respects your project's requirements.txt and setup.py dependencies
- Virtual environment friendly - works with both global and virtual environments
- Use --exclude to skip test directories or other non-relevant code
- Use --ignore to keep packages that might be used indirectly
- Use --json for integration with other tools or scripts.
- Use --requirements to update your requirements.txt automatically.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests, as it will make the project better.

## License

MIT License