"""
Describes all metadata of this project and create the necessary configuration
to install this package with `pip`.
"""
import setuptools

import picasso

setuptools.setup(
    name="picasso",
    version="0.1.0",
    author="R&E",
    platform="Tested under Windows 10",
    packages=setuptools.find_packages(include=["azarias", "azarias.*"]),
    description=picasso.__doc__
)
