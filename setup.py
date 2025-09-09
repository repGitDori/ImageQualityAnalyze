"""
Setup script for ImageQualityAnalyzer
"""

from setuptools import setup, find_packages
import os

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="image-quality-analyzer",
    version="1.0.0",
    author="Dorian Lapi",
    author_email="databasemaestro@gmail.com",
    description="Advanced image quality checker - Dual Licensed (Free for non-commercial, Commercial license required for business use)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/ImageQualityAnalyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
        ],
        "gui": [
            "tkinter",
            "PyQt5>=5.15.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "image-quality-analyzer=cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "image_quality_analyzer": [
            "configs/*.json",
        ],
    },
    keywords="image quality document scan photo analysis metrics sharpness contrast contributions opensource",
    project_urls={
        "Bug Reports": "https://github.com/DorianLapi/ImageQualityAnalyzer/issues",
        "Source": "https://github.com/DorianLapi/ImageQualityAnalyzer",
        "Documentation": "https://github.com/DorianLapi/ImageQualityAnalyzer#readme",
        "Contributions": "https://github.com/DorianLapi/ImageQualityAnalyzer/blob/main/CONTRIBUTING.md",
        "Commercial License": "mailto:databasemaestro@gmail.com?subject=Commercial%20License%20Request",
        "Contact": "mailto:databasemaestro@gmail.com",
    },
)
