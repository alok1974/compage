from functools import wraps


class classproperty(object):
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


def validatetype(pos, typ, exc=TypeError, msg=None, formatArgs=None):
    """
    A type validation decorator

    Args:
        pos (int): The position of the argument(to validate) in args
        typ (python objects): Type that the argument should be an instance of
        exc (exception, optional): Exception to raise for failed validation
        msg (str, optional): Message for exception
        formatArgs (list of ints, optional): A list of ints defining the
                                             position of arguments to be used
                                             from wrapped functions *args


    Returns:
        decorated function's return value
    """
    def validateArgType(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            toValidate = args[pos]
            # Accessing arg through a mutable([]) to allow assigment
            # for a non local argument outside local scope. Basically
            # a workaround for what is now `nonlocal` statement in Python 3
            outertyp = [typ]
            fargs = ([args[i] for i in formatArgs] if formatArgs else
                     [toValidate, pos, outertyp[0]])
            if not isinstance(toValidate, typ):
                if outertyp[0] is basestring:
                    outertyp[0] = '<str or unicode>'

                message = msg or ("argument '{0}', at position {1} "
                                  "should be of type {2}")
                raise exc(message.format(*fargs))
            return func(*args, **kwargs)
        return wrapper
    return validateArgType
