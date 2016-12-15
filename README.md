# compage
Generic reusable python utilities and tools.

### compage.services
--------------------
Code Object Manager - classes, functions and other code objects can be added as a service and retrieved when needed. Mostly helps in patterns like dependency injection.
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

### compage.installutils
-------------------------
Light weight package installer a la setup.py(distutils).
```python
from compage.installutils import setup

# install - `True` to install, `False` to uninstall
install = True

# force_update - `True` to overwrite(update) existing package
force_update = False

# site - location where the package should be installed. Note that this
# location should be in sys.path via PYTHONPATH or use of .pth files
site = 'path to site location'

# package_name - Name of the installed package
package_name = 'compage'

# src_dir - Path to source code dir
src_dir = 'path to source code dir'

args = [site, package_name]
kwargs = {
    'src_dir': src_dir,
    'install': install,
    'force_update': force_update,
}

setup(*args, **kwargs)
```