# compage
A python tool bag consiting of generic reusable utilities and tools.

### compage.services
--------------------
A Code Object Service Manager - classes, functions and other code objects can be added as a service and retrieved when needed. Mostly helps in patterns like dependency injection.


##### Compage Services Example
```python
from compage.services import ServiceManager as mgr


# Code to be injected
class ToBeInjected(object):
    foo = 'foo'


# Injection is expected here
class InjectionReceiver(object):
    def __init__(self, injectedCode):
        self._injectedCode = injectedCode

    @property
    def injectedCode(self):
        return self._injectedCode

# Injection code added to the manager
mgr.add('injected', ToBeInjected())

# Injection
toBeInjected = mgr.get('injected')
target = InjectionReceiver(toBeInjected)

print target.injectedCode.foo

# >>> foo

```
