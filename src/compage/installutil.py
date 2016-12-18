"""
Light weight package installer a la setup.py(distutils).

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
"""
import os
import sys
import shutil


from compage import exception


def handle_error(exc_type, error_info=None):
    if exc_type == exception.InstallError:
        e, package_name = error_info
        if e.errno == 17:
            msg = ("'{0}' is already installed, use `force_update=True`"
                   " to overwrite the existing package").format(package_name)
        else:
            msg = e
        raise exception.InstallError(msg)
    elif exc_type == exception.SiteNotFoundError:
        msg = "Site '{0}' does not exist".format(
            error_info)
        raise exception.SiteNotFoundError(msg)
    elif exc_type == exception.SiteNotRegisteredError:
        msg = ("Site '{0}' is not registered "
               "(i.e, not found in sys.path)").format(error_info)
        raise exception.SiteNotRegisteredError(msg)
    elif exc_type == exception.InvalidPackageError:
        msg = "{0} is not a valid package, no __init__.py found"
        raise exception.InvalidPackageError(msg.format(error_info))
    elif exc_type == exception.UninstallError:
        msg = "Package '{0}' is not installed, nothing to uninstall".format(
            error_info)
        raise exception.UninstallError(msg)
    else:
        msg = "Unable to handle exception {0}".format(exc_type)
        raise ValueError(msg)


def validate_site(site):
    site = os.path.abspath(site)
    if not os.path.exists(site):
        handle_error(exception.SiteNotFoundError, site)
    if site not in sys.path:
        handle_error(exception.SiteNotRegisteredError, site)
    return site


def validate_package(src_dir):
    src_dir = os.path.abspath(src_dir)
    if '__init__.py' not in os.listdir(src_dir):
        handle_error(exception.InvalidPackageError, src_dir)
    return src_dir


def validate_uninstall_path(package, package_path):
    package_path = os.path.abspath(package_path)
    if not os.path.exists(package_path):
        handle_error(exception.UninstallError, package)
    return package_path


def package_install(site, package_name, src_dir, force_update=False):
    site = validate_site(site)
    src_dir = validate_package(src_dir)
    dst_dir = os.path.join(site, package_name)

    updated = False
    if force_update and os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
        updated = True

    try:
        shutil.copytree(src_dir, dst_dir)
    except OSError as e:
        handle_error(exception.InstallError, (e, package_name))

    msg_base = "'{0}' to site '{1}'\n".format(src_dir, site)
    if updated:
        msg = 'Updated {0}'.format(msg_base)
    else:
        msg = 'Installed {0}'.format(msg_base)

    sys.stdout.write(msg)


def package_uninstall(site, package_name):
    site = validate_site(site)
    package_dir = validate_uninstall_path(
        package_name, os.path.join(site, package_name))

    shutil.rmtree(package_dir)

    msg = "Uninstalled '{0}' from site '{1}'\n".format(
        package_name, package_dir)
    sys.stdout.write(msg)


def setup(site, package_name, src_dir=None, install=True, force_update=False):
    if install:
        package_install(
            site=site,
            package_name=package_name,
            src_dir=src_dir,
            force_update=force_update,
        )
    else:
        package_uninstall(
            site=site,
            package_name=package_name,
        )
