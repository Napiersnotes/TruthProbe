from setuptools import setup, find_packages
import os

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="truthprobe",
    version="4.0.0",
    author="Dafydd Napier",
    author_email="napiersnotes@github.com",
    description="A lightweight, model-agnostic deception detector for LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Napiersnotes/TruthProbe",
    project_urls={
        "Bug Tracker": "https://github.com/Napiersnotes/TruthProbe/issues",
        "Documentation": "https://github.com/Napiersnotes/TruthProbe#readme",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(include=['src', 'src.*']),
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "dashboard": [
            "dash>=2.9.0",
            "dash-bootstrap-components>=1.4.0",
            "plotly>=5.14.0",
        ],
        "full": [
            "torch>=2.0.0",
            "transformers>=4.30.0",
            "sentence-transformers>=2.2.0",
            "spacy>=3.5.0",
            "scikit-learn>=1.3.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "truthprobe=src.truthprobe_v3:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.txt", "*.md"],
    },
)
