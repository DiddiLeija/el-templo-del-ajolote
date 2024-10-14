"""
Script to generate the Windows-only executable with cx_Freeze.
"""

import sys

try:
    from cx_Freeze import Executable, setup
except ImportError:
    sys.exit("COuld not find package 'cx_Freeze'. Please install it and try again.")


setup(
    name="El Templo del Ajolote",
    description="Axolotls and dungeon crawlers.",
    author="Diego Ramirez",
    author_email="dr01191115@gmail.com",
    executables=[
        Executable(
            "main.py",
            base="Win32GUI",
        )
    ],
)