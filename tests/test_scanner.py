import os
import tempfile
from pathlib import Path
import pytest
from pip_cleanup.scanner import find_imports_in_file, find_imports_in_directory, format_size

def test_find_imports_in_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
import os
import sys as system
from pathlib import Path
from datetime import datetime as dt
from .utils import helper
        """)
        f.flush()
        
        imports = find_imports_in_file(f.name)
        os.unlink(f.name)
        
        assert imports == {'os', 'sys', 'pathlib', 'datetime', 'utils'}

def test_find_imports_in_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file structure
        test_files = {
            'main.py': """
import requests
from PIL import Image
            """,
            'utils/helper.py': """
import json
from datetime import datetime
            """,
            'tests/test_main.py': """
import pytest
import os.path
            """
        }
        
        for filepath, content in test_files.items():
            full_path = Path(tmpdir) / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        imports = find_imports_in_directory(tmpdir)
        assert imports == {'requests', 'pillow', 'json', 'datetime', 'pytest', 'os'}

def test_format_size():
    assert format_size(500) == "500.0B"
    assert format_size(1024) == "1.0KB"
    assert format_size(1024 * 1024) == "1.0MB"
    assert format_size(1024 * 1024 * 1024) == "1.0GB" 