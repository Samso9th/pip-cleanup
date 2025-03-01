"""
pip-cleanup - A tool to find and remove unused pip packages
"""

from .version import __version__
from .cli import main

__author__ = "Samso9th"

if __name__ == "__main__":
    main()