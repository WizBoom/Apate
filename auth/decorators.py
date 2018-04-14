import functools
from flask import current_app, flash, redirect
from flask_login import current_user


def needs_permission(permission_name, page_name):
    """Checks if user has correct permissions.

    Args:
        permission_name (str): Name of the permission
        page_name (str): Name of the page (for logging purposes)
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.has_permission(permission_name):
                flash("You do not have the required permission ({}) to access the {} page.".format(permission_name, page_name), "danger")
                current_app.logger.info("{} tried to illegally access the {} page but didn't have the required {} permission.".format(current_user.name, page_name, permission_name))
                return redirect(current_app.config['BASE_URL'])

            result = f(*args, **kwargs)

            return result
        return wrapped
    return decorator


def alliance_required():
    """Checks if user is in the main alliance.

    Args:
        None
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_in_alliance:
                flash("This page requires you to be in the alliance.", "danger")
                return redirect(current_app.config['BASE_URL'])

            result = f(*args, **kwargs)

            return result
        return wrapped
    return decorator
