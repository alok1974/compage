"""
Light weight package installer a la setup.py(distutils)
Uses PYTHONPATH to mock site locations
"""
import os
import sys
import shutil


class exception(object):
    """Exceptions for intall errors"""

    class InstallError(Exception):
        """Error raised when install fails"""
        pass

    class SiteNotFoundError(IOError):
        """Error raised when install fails"""
        pass

    class InvalidPackageError(IOError):
        """Error raised when trying to install an invalid package"""
        pass

    class UninstallError(IOError):
        """Error raised when unable to uninstall package"""
        pass


def handle_error(exc_type, error_info=None):
    if exc_type == exception.InstallError:
        info = ''
        if error_info.errno == 17:
            info = "use 'force=True' to force install"
        msg = "unable to install, OSError{0}, {1}"
        raise exception.InstallError(msg.format(error_info, info))
    elif exc_type == exception.SiteNotFoundError:
        msg = "'{0}' not found in 'PYTHONPATH'".format(error_info)
        raise exception.SiteNotFoundError(msg)
    elif exc_type == exception.InvalidPackageError:
        msg = "{0} is not a valid package, no __init__.py found"
        raise exception.InvalidPackageError(msg.format(error_info))
    elif exc_type == exception.UninstallError:
        package_name, uninstall_path = error_info
        msg = "cannot uninstall '{0}', package path '{1}' does not exist"
        raise exception.UninstallError(
            msg.format(package_name, uninstall_path))
    else:
        msg = "unable to handle exception {0}".format(exc_type)
        raise ValueError(msg)


def validate_site(site):
    site = os.path.abspath(site)
    if site not in sys.path:
        handle_error(exception.SiteNotFoundError, site)
    return site


def validate_package(src_dir):
    src_dir = os.path.abspath(src_dir)
    if '__init__.py' not in os.listdir(src_dir):
        handle_error(exception.InvalidPackageError, src_dir)

    return src_dir


def validate_uninstall_path(package, package_path):
    package_path = os.path.abspath(package_path)
    if not os.path.exists(package_path):
        handle_error(exception.UninstallError, (package, package_path))

    return package_path


def setup(site, packages, package_dir, force=False):
    site = validate_site(site)
    src_dir = None
    dst_dir = None
    for package in packages:
        src_dir = validate_package(package_dir.get(package))
        dst_dir = os.path.join(site, package)

        if force and os.path.exists(dst_dir):
            shutil.rmtree(dst_dir)

        try:
            shutil.copytree(src_dir, dst_dir)
        except OSError as e:
            handle_error(exception.InstallError, e)

    return src_dir


def install(site, packages, package_dir, force=False):
    src_dir = setup(
        site=site,
        packages=packages,
        package_dir=package_dir,
        force=force,
    )

    msg = "installed '{0}' to site '{1}'\n".format(src_dir, site)
    sys.stdout.write(msg)


def uninstall(site, package):
    site = validate_site(site)
    package_dir = validate_uninstall_path(package, os.path.join(site, package))

    shutil.rmtree(package_dir)

    msg = "uninstalled {0} from site {1}\n".format(package, package_dir)
    sys.stdout.write(msg)
