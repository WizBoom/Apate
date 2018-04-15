import logging
from datetime import timedelta

from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import LoginManager, login_user, logout_user, current_user

from auth.shared import Database, SharedInfo, EveAPI
from auth.admin.app import Application as admin_blueprint
from auth.corp_management.app import Application as corp_management_blueprint
from auth.hr import Application as hr_blueprint
from auth.models import *
from auth.util import Util

from preston.esi import Preston

# -- Initialisation -- #


# Create and configure app
FlaskApplication = Flask(__name__)
FlaskApplication.permanent_session_lifetime = timedelta(days=14)
FlaskApplication.config.from_pyfile('config.cfg')
SharedInfo['alliance_id'] = FlaskApplication.config['ALLIANCE_ID']
SharedInfo['user_agent'] = 'Apate Auth App ({})'.format(FlaskApplication.config['USER_AGENT_EMAIL'])

# Database connection
Database.app = FlaskApplication
Database.init_app(FlaskApplication)

# User management
LoginManager = LoginManager(FlaskApplication)
LoginManager.login_message = ''
LoginManager.login_view = 'login'

# Application logging
FlaskApplication.logger.setLevel(FlaskApplication.config['LOGGING_LEVEL'])
LogFormat = logging.Formatter(style='{', fmt='{asctime} [{levelname}] {message}', datefmt='%Y-%m-%d %H:%M:%S')

FileHandler = logging.FileHandler('log.txt')
FileHandler.setFormatter(LogFormat)
FileHandler.setLevel(FlaskApplication.config['LOGGING_LEVEL'])
FlaskApplication.logger.addHandler(FileHandler)

ConsoleHandler = logging.StreamHandler()
ConsoleHandler.setFormatter(LogFormat)
ConsoleHandler.setLevel(FlaskApplication.config['LOGGING_LEVEL'])
FlaskApplication.logger.addHandler(ConsoleHandler)

# EVE  API connection
EveAPI["default_user_preston"] = Preston(
    user_agent=EveAPI['user_agent'],
    client_id=FlaskApplication.config['EVE_DEFAULT_USER_CLIENT'],
    client_secret=FlaskApplication.config['EVE_DEFAULT_USER_SECRET'],
    callback_url=FlaskApplication.config['BASE_URL'] + FlaskApplication.config['EVE_DEFAULT_USER_CALLBACK']
)

EveAPI["corp_preston"] = Preston(
    user_agent=EveAPI['user_agent'],
    client_id=FlaskApplication.config['CORP_CLIENT_ID'],
    client_secret=FlaskApplication.config['CORP_CLIENT_SECRET'],
    callback_url=FlaskApplication.config['BASE_URL'] + "/corp_management/eve/corp/callback",
    scope="esi-corporations.read_corporation_membership.v1"
)

# Jinja global variables
FlaskApplication.jinja_env.globals.update(login_url=EveAPI["default_user_preston"].get_authorize_url())

# Blueprints
FlaskApplication.register_blueprint(admin_blueprint, url_prefix='/admin')
FlaskApplication.register_blueprint(corp_management_blueprint, url_prefix='/corp_management')
FlaskApplication.register_blueprint(hr_blueprint, url_prefix='/hr')


# Util
SharedInfo['util'] = Util(
    FlaskApplication
)

FlaskApplication.logger.info('Initialization complete')
# -- End Initialisation -- #

# -- Methods -- #


@LoginManager.user_loader
def load_user(character_id):
    """Takes a string int and returns a auth.models.Character object for Flask-Login.

    Args:
        character_id (str): character model id

    Returns:
        auth.models.Character: character with that id
    """
    return Character.query.filter_by(id=int(character_id)).first()


@FlaskApplication.route('/')
def landing():
    """Landing page of the website.

    Args:
        None

    Returns:
        str: redirect to the appropriate url.
    """
    return render_template('landing.html')


@FlaskApplication.route('/eve/user/default/callback')
def eve_oauth_callback():
    """Completes the EVE SSO login. Here, auth.models.Characters model
    is created for the user if they doesn't exist and the user is redirected
    to the the page appropriate for their access level.

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
        auth = EveAPI["default_user_preston"].authenticate(request.args['code'])
    except Exception as e:
        FlaskApplication.logger.error('ESI signing error: ' + str(e))
        flash('There was an authentication error signing you in.', 'error')
        return redirect(url_for('login'))

    # Get character information
    characterInfo = auth.whoami()
    characterId = characterInfo['CharacterID']
    character = Character.query.filter_by(id=characterId).first()

    # Get character corporation information
    corporationInfo = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/characters/{}/?datasource=tranquility".format(str(characterId))).json()
    corporationId = corporationInfo['corporation_id']

    # If character already exists, log them in
    if character:
        # Update the corporation if it changed
        if corporationId != character.corp_id:
            SharedInfo['util'].update_character_corporation(character, corporationId)

        login_user(character)
        FlaskApplication.logger.debug('{} logged in with EVE SSO'.format(current_user.name))
        flash('Logged in', 'success')
        return redirect(url_for('landing'))

    # If there is no character, make a new one in the database
    character = SharedInfo['util'].create_character(characterId)
    SharedInfo['util'].update_character_corporation(character, corporationId)
    Database.session.add(character)
    Database.session.commit()
    login_user(character)
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


@FlaskApplication.route('/login')
def login():
    """Directs user to the login page.

    Args:
        None

    Returns:
        str: redirect to login page.
    """
    return redirect(EveAPI["default_user_preston"].get_authorize_url())


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
