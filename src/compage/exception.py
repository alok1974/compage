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


# Exceptions for installutils
class InstallError(Exception):
    """Error raised when install fails"""
    pass


class SiteNotFoundError(IOError):
    """Error raised site does not exist"""
    pass


class SiteNotRegisteredError(ValueError):
    """Error raised when site is not registered for package lookups"""
    pass


class InvalidPackageError(IOError):
    """Error raised when trying to install an invalid package"""
    pass


class UninstallError(IOError):
    """Error raised when unable to uninstall package"""
    pass


# Exceptions for nodeutils
class NodeCreationError(ValueError):
    """Error raised when unable to create node"""
    pass


class TreeCreationError(ValueError):
    """Error raised when unable to create tree"""
    pass


class TreeRenderError(ValueError):
    """Error raised when unable to render tree"""
    pass
