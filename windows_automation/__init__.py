"""
Windows Automation Package

This package provides tools for automating Windows applications using Appium and Windows Application Driver.
"""

__version__ = "0.1.0"

# Import key components to make them available at package level
from .windows_driver_factory import create_windows_driver
from .windows_driver import WindowsDriver
from .windows_client import WindowsClient

__all__ = [
    'create_windows_driver',
    'WindowsDriver',
    'WindowsClient'
]