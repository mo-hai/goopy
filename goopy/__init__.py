"""
goopy - Google API Tools for Python

A simple wrapper for Google Drive, Sheets, and Slides APIs.
"""

from .DriveServiceAPI import DriveService
from .SheetsServiceAPI import SheetsService
from .SlidesServiceAPI import SlidesService

__version__ = "0.1.0"
__all__ = ['DriveService', 'SheetsService', 'SlidesService']
