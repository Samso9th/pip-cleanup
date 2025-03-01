from setuptools import setup, find_packages

setup(
    name="pip-cleanup",
    version="0.1.84",
    author="Samso9th",
    description="A Python tool to clean up unused pip packages",
    long_description="A CLI tool that helps you identify and remove unused pip packages from your Python environment",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "click>=8.0.0",
        "colorama>=0.4.4",
        "tabulate>=0.8.9",
    ],
    entry_points={
        "console_scripts": [
            "pip-cleanup=pip_cleanup.cli:main",
        ],
    },
    python_requires=">=3.7",
    license="MIT",
)