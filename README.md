# compage
Generic reusable python utilities and tools.

### compage.services
--------------------
Classes, Functions and other Objects can be stored and retrieved when needed. Painless implementation of patterns like Dependency Injection.
```python
from compage.service import ServiceManager as mgr


# Code to be injected
class ToBeInjected(object):
    foo = 'foo'


# Injection is expected here
class InjectionReceiver(object):
    def __init__(self, injected_code):
        self._injected_code = injected_code

    @property
    def injected_code(self):
        return self._injected_code


# Injection code added to the manager
mgr.add('injected', ToBeInjected())

# Injection
toBeInjected = mgr.get('injected')
target = InjectionReceiver(toBeInjected)

assert target.injected_code.foo == 'foo'

```

### compage.installutils
-------------------------
Light weight package installer a la setup.py(distutils).

Example: Install package `foo` from the `/src/foo/` to `/custom/site-packages/`

```python
from compage.installutil import setup

# install - `True` to install, `False` to uninstall
install = True

# force_update - `True` to overwrite(update) existing package
force_update = False

# site - location where the package should be installed. Note that this
# location should be in sys.path
site = '/custom/site-packages/'

# package_name - Name of the package to install
package_name = 'foo'

# src_dir - Path to source code directory
src_dir = '/src/foo/'

args = [site, package_name]
kwargs = {
    'src_dir': src_dir,
    'install': install,
    'force_update': force_update,
}

setup(*args, **kwargs)

```
