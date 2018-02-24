import logging
from datetime import timedelta

from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import LoginManager, login_user, logout_user, current_user
from preston.esi import Preston

from auth.shared import Database
from auth.models import User


# -- Initialisation -- #

# Create and configure app
FlaskApplication = Flask(__name__)
FlaskApplication.permanent_session_lifetime = timedelta(days=14)
FlaskApplication.config.from_pyfile('config.cfg')

UserAgent = 'GETIN Auth (Apate) app ({})'.format(FlaskApplication.config['USER_AGENT_EMAIL'])

# EVE  API connection
PrestonConnection = Preston(
    user_agent=UserAgent,
    client_id=FlaskApplication.config['EVE_DEFAULT_USER_CLIENT'],
    client_secret=FlaskApplication.config['EVE_DEFAULT_USER_SECRET'],
    callback_url=FlaskApplication.config['BASE_URL'] + FlaskApplication.config['EVE_DEFAULT_USER_CALLBACK']
)

# Database connection
Database.app = FlaskApplication
Database.init_app(FlaskApplication)

# User management
LoginManager = LoginManager(FlaskApplication)
LoginManager.login_message = ''
LoginManager.login_view = 'login'

# Application logging
FlaskApplication.logger.setLevel(FlaskApplication.config['LOGGING_LEVEL'])
handler = logging.FileHandler('log.txt')
handler.setFormatter(logging.Formatter(style='{', fmt='{asctime} [{levelname}] {message}', datefmt='%Y-%m-%d %H:%M:%S'))
handler.setLevel(FlaskApplication.config['LOGGING_LEVEL'])
FlaskApplication.logger.addHandler(handler)
FlaskApplication.logger.info('Initialization complete')

# Jinja global variables
FlaskApplication.jinja_env.globals.update(login_url=PrestonConnection.get_authorize_url())
# -- End Initialisation -- #

# -- Methods -- #


@LoginManager.user_loader
def load_user(user_id):
    """Takes a string int and returns a auth.models.User object for Flask-Login.

    Args:
        user_id (str): user model id

    Returns:
        auth.models.User: user with that id
    """
    return User.query.filter_by(id=int(user_id)).first()


@FlaskApplication.route('/')
def landing():
    return render_template('landing.html')


@FlaskApplication.route('/eve/user/default/callback')
def eve_oauth_callback():
    """Completes the EVE SSO login. Here, hr.models.User models
    and hr.models.Member models are created for the user if they don't
    exist and the user is redirected the the page appropriate for their
    access level.

    Args:
        None

    Returns:
        str: redirect to the login endpoint if something failed, join endpoint if
        the user is a new user, or the index endpoint if they're already a member.
    """
    if 'error' in request.path:
        FlaskApplication.logger.error('Error in EVE SSO callback: ' + request.url)
        flash('There was an error in EVE\'s response', 'error')
        return url_for('login')
    try:
        auth = PrestonConnection.authenticate(request.args['code'])
    except Exception as e:
        FlaskApplication.logger.error('ESI signing error: ' + str(e))
        flash('There was an authentication error signing you in.', 'error')
        return redirect(url_for('login'))
    character_info = auth.whoami()
    character_name = character_info['CharacterName']
    user = User.query.filter_by(name=character_name).first()
    if user:
        login_user(user)
        FlaskApplication.logger.debug('{} logged in with EVE SSO'.format(current_user.name))
        flash('Logged in', 'success')
        return redirect(url_for('landing'))
    user = User(character_name)
    Database.session.add(user)
    Database.session.commit()
    login_user(user)
    FlaskApplication.logger.info('{} created an account'.format(current_user.name))
    return redirect(url_for('landing'))


@FlaskApplication.route('/logout')
def logout():
    """Logs the user out of the site.

    Args:
        None

    Returns:
        str: redirect to the login endpoint
    """
    FlaskApplication.logger.debug('{} logged out'.format(current_user.name if not current_user.is_anonymous else 'unknown user'))
    logout_user()
    return redirect(url_for('landing'))


@FlaskApplication.errorhandler(404)
def error_404(e):
    """Catches 404 errors in the app and shows the user an error page.

    Args:
        e (Exception): the exception from the server

    Returns:
        str: rendered template 'error_404.html'
    """
    FlaskApplication.logger.error('404 error at "{}" by {}: {}'.format(
        request.url, current_user.name if not current_user.is_anonymous else 'unknown user', str(e))
    )
    return render_template('error_404.html')


@FlaskApplication.errorhandler(500)
def error_500(e):
    """Catches 500 errors in the app and shows the user an error page.

    Args:
        e (Exception): the exception from the server

    Returns:
        str: rendered template 'error_404.html'
    """
    FlaskApplication.logger.error('500 error at "{}" by {}: {}'.format(
        request.url, current_user.name if not current_user.is_anonymous else 'unknown user', str(e))
    )
    return render_template('error_500.html')
# -- End methods -- #
