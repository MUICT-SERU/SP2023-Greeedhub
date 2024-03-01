"""Custom exceptions for Saddlebags."""


class SaddlebagsError(Exception):
    """There was an ambiguous exception that occurred."""


class DuplicateConfigurationFile(SaddlebagsError):
    """
    Two configuration files exist with the same name. 

    This exception will be raised even if file types are different.
    Ex. Attempting to load ldap.json and ldap.yaml should result
    in this exception being raised.
    """


class MalformedConfigurationFile(SaddlebagsError):
    """Syntax errors exist in a configuration file."""
