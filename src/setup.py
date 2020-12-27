import sys
from pathlib import Path
from typing import Dict

from setuptools import setup

NAME = "systemhud"

this = Path(__file__)
info: Dict[str, str] = {}

setup(
    name=NAME,
    version="0.1",
    author="jdost",
    description=(
        "Library of various system monitoring and presenting utilities used "
        "to present system information."
    ),
    python_requires=">=3.6.0",
    packages=[NAME, f"{NAME}.ui", f"{NAME}.lib"],
    package_dir={
        NAME: f"{NAME}/",
        f"{NAME}.ui": f"{NAME}/ui/",
        f"{NAME}.lib": f"{NAME}/lib/",
    },
    extras_require={
        "dev": [
            "black>=19.3b0",
            "isort>=4.3.21",
            "mypy>=0.770",
        ]
    },
    scripts=[
        "../bin/pulseaudio",
        "../bin/acpi",
        "../bin/bluetooth",
        "../bin/cpu",
        "../bin/screen-brightness",
        "../bin/memory",
    ],
)
