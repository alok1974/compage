"""Compage Exceptions"""


# Exceptions for Service Manager
class InvalidTokenError(TypeError):
    """Error raised when the token in malformed"""
    pass


class NoServiceError(ValueError):
    """Error raised when no services are added"""
    pass


class ServiceNotFoundError(KeyError):
    """Error raised when service is not found for a given token"""
    pass


class UnexpectedAttributeError(ValueError):
    """
    Error raised when an unexpected attribute
    is looked up in the Service Descriptor
    """
    pass


class ServiceAlreadyExistsError(Exception):
    """Error raised when trying to add already existing service"""
    pass
