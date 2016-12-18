
"""
A Code Server Manager - classes, functions and other code objects can be
added as a service and retrieved when needed. Mostly helps in patterns like
dependency injection.
"""
import collections


from compage import decorator, exception


__all__ = ['ServiceManager']


# Creating a validation decorator for token validation
msg = "token '{0}' should be of type <str or unicode>"
validatetoken = decorator.validatetype(
    1,
    str,
    exc=exception.InvalidTokenError,
    msg=msg,
    format_args=[1]
)


# Super Simple code object container using an OrderedDict
class _CodeObjectServices(object):
    def __init__(self):
        super(_CodeObjectServices, self).__init__()
        self._services = collections.OrderedDict()

    @validatetoken
    def add_service(self, token, service, force=False, execute=False,
                    pre_args=None, pre_kwargs=None):

        if token in self.tokens and not force:
            msg = ("service with token '{0}' already exists, "
                   "use force=True to overwrite".format(token))
            raise exception.ServiceAlreadyExistsError(msg)

        if callable(service) and execute:
            # Execute (call ) the service object before storing it.
            # This will store the return value in case of a function / method
            # and an object instance in case of a class.
            args = pre_args or []
            kwargs = pre_kwargs or {}
            service_obj = service(*args, **kwargs)
        else:
            service_obj = service

        self._services[token] = service_obj

    @validatetoken
    def remove_service(self, token):
        try:
            self._services.pop(token)
        except KeyError:
            msg = "Service with token '{0}' does not exists, unable to remove"
            raise exception.ServiceNotFoundError(msg)

    @validatetoken
    def service_exists(self, token):
        return token in self._services

    def clear_all(self):
        self._services.clear()

    @property
    def id(self):
        return id(self._services)

    @property
    def tokens(self):
        return self._services.keys()

    @property
    def count(self):
        return len(self.tokens)

    def __getitem__(self, token):
        if not self.count:
            raise exception.NoServiceError("No services exists")
        try:
            service = self._services[token]
        except KeyError:
            msg = ("No service with token '{0}'".format(token))
            raise exception.ServiceNotFoundError(msg)
        else:
            return service


# The descriptor allows for getting and attaching
# _static_ objects stored in services dict.
class _ServiceDescriptor(object):
    def __init__(self, token, services):
        super(_ServiceDescriptor, self).__init__()
        self._token = token
        self._services = services

    def __get__(self, instance, owner):
        return self.service

    def __getattr__(self, name):
        if name != 'service':
            msg = "Unexpected attribute request other then 'service'"
            raise exception.UnexpectedAttributeError(msg)

        self.service = self._get_service()
        return self.service

    def _get_service(self):
        return self._services[self._token]


class ServiceManager(object):
    _services = _CodeObjectServices()

    @classmethod
    def add(cls, token, service, force=False, execute=True, pre_args=None,
            pre_kwargs=None):
        """
        Adds a service


        Args:
            token (str): Token for adding service
            service (obj): Any code object i.e, class, function etc.
            force (bool, optional): When true overwrites the existing service
            execute (bool, optional): When true, executes the code with given
                                      pre_args and pre_kwargs before adding
            pre_args ([], optional): Arguments for pre execution of code before
                                    adding
            pre_kwargs ({}, optional): Keyword arguments for pre execution of
                                      code before adding



        Returns:
            None

        """
        cls._services.add_service(
            token,
            service,
            force=force,
            execute=execute,
            pre_args=pre_args,
            pre_kwargs=pre_kwargs,
        )

    @classmethod
    def remove(cls, token):
        """
        Removes a service


        Args:
            token (str): Token for which service needs to be removed


        Returns:
            None

        """
        cls._services.remove_service(token)

    @classmethod
    def get(cls, token):
        """
        Return an existing service


        Args:
            tokens (str): Token to get service


        Returns:
            service (code object)
        """
        class _Service(object):
            obj = _ServiceDescriptor(token, cls._services)

        return _Service.obj

    @classmethod
    def remove_all(cls):
        """Removes all existing services"""
        cls._services.clear_all()

    @classmethod
    def exists(cls, token):
        """
        Returns whether a service exists


        Args:
            token (str): Token to check for existence of service


        Returns:
            bool
        """
        return cls._services.service_exists(token)

    @decorator.classproperty
    def tokens(cls):
        """
        Returns a list of all existing service tokens


        Returns:
            []

        """
        return cls._services.tokens

    @decorator.classproperty
    def count(cls):
        """
        Return the count of existing services


        Returns:
            int
        """
        return cls._services.count

    @decorator.classproperty
    def id(cls):
        """
        Returns the id of services container (dict)


        Returns:
            str (hex)
        """
        return cls._services.id
