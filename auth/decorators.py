import functools
from flask import current_app, flash, redirect
from flask_login import current_user


def needs_permission(permission_name, page_name):
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
