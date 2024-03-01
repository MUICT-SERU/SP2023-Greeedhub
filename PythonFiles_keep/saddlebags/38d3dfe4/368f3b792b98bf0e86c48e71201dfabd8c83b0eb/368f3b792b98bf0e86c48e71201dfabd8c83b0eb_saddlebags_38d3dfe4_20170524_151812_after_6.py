"""Custom exceptions for Saddlebags"""


class SaddlebagsError(Exception):
    """There was an ambiguous exception that occurred."""


class DuplicateConfigurationFile(SaddlebagsError):
    """
    Two configuration files exist with the
    same name (minus the file type suffix).
    """


class MalformedConfigurationFile(SaddlebagsError):
    """Syntax errors exist in a configuration file."""

