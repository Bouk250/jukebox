#!/usr/bin/env python3
import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="jukebox",
    version="0.0.1",
    description="A downloader from multiple services",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Bouk250",
    #author_email="RemixDev64@gmail.com",
    license="GPL3",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
    	"Programming Language :: Python :: 3.7",
    	"Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=["requests"],
)
