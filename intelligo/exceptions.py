"""
intelligo.exceptions
===================
This module defines custom exceptions for the Intelligo library.
"""

class ConfigNotLoadedError(Exception):
    """
    Exception raised when the configuration file is not loaded.
    """

class ScraperError(Exception):
    """
    Exception raised when there is an error in the web scraping process.
    """