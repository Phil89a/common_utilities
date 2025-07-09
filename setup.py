from setuptools import setup, find_packages

setup(
    name="common-utils",
    version="0.1.0",
    description="Shared logging and utilities for my energy projects",
    author="Phil",
    packages=find_packages(),
    install_requires=[
        "loguru>=0.7.3",
    ],
    python_requires=">=3.8",
)