import logging
from datetime import timedelta

from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

from auth.shared import Database, SharedInfo, EveAPI
from auth.admin.app import Application as admin_blueprint
from auth.corp_management.app import Application as corp_management_blueprint
from auth.hr import Application as hr_blueprint
from auth.esi_parser import Application as esi_parser_blueprint
from auth.models import *
from auth.util import Util

import praw
from preston import Preston

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
    callback_url=FlaskApplication.config['BASE_URL'] + '/eve/user/default/callback'
)

EveAPI["corp_preston"] = Preston(
    user_agent=EveAPI['user_agent'],
    client_id=FlaskApplication.config['CORP_CLIENT_ID'],
    client_secret=FlaskApplication.config['CORP_CLIENT_SECRET'],
    callback_url=FlaskApplication.config['BASE_URL'] + "/corp_management/eve/corp/callback",
    scope="esi-corporations.read_corporation_membership.v1"
)

EveAPI["full_auth_preston"] = Preston(
    user_agent=EveAPI['user_agent'],
    client_id=FlaskApplication.config['EVE_FULL_AUTH_CLIENT_ID'],
    client_secret=FlaskApplication.config['EVE_FULL_AUTH_SECRET'],
    callback_url=FlaskApplication.config['BASE_URL'] + "/eve/user/auth/callback",
    scope="esi-calendar.read_calendar_events.v1 esi-location.read_location.v1 esi-location.read_ship_type.v1 esi-mail.read_mail.v1 esi-skills.read_skills.v1 esi-skills.read_skillqueue.v1 esi-wallet.read_character_wallet.v1 esi-clones.read_clones.v1 esi-characters.read_contacts.v1 esi-universe.read_structures.v1 esi-bookmarks.read_character_bookmarks.v1 esi-killmails.read_killmails.v1 esi-assets.read_assets.v1 esi-planets.manage_planets.v1 esi-fleets.read_fleet.v1 esi-fittings.read_fittings.v1 esi-markets.structure_markets.v1 esi-characters.read_loyalty.v1 esi-characters.read_opportunities.v1 esi-characters.read_chat_channels.v1 esi-characters.read_medals.v1 esi-characters.read_standings.v1 esi-characters.read_agents_research.v1 esi-industry.read_character_jobs.v1 esi-markets.read_character_orders.v1 esi-characters.read_blueprints.v1 esi-characters.read_corporation_roles.v1 esi-location.read_online.v1 esi-contracts.read_character_contracts.v1 esi-clones.read_implants.v1 esi-characters.read_fatigue.v1 esi-characters.read_notifications.v1 esi-industry.read_character_mining.v1 esi-characters.read_titles.v1 esi-characters.read_fw_stats.v1 esi-characterstats.read.v1"
)

# Reddit connection
SharedInfo['reddit'] = praw.Reddit(
    client_id=FlaskApplication.config['REDDIT_OAUTH_CLIENT_ID'],
    client_secret=FlaskApplication.config['REDDIT_OAUTH_SECRET'],
    redirect_uri=FlaskApplication.config['BASE_URL'] + "/reddit/callback",
    user_agent=FlaskApplication.config['REDDIT_USER_AGENT']
)

# Jinja global variables
FlaskApplication.jinja_env.globals.update(login_url=EveAPI["default_user_preston"].get_authorize_url())

# Blueprints
FlaskApplication.register_blueprint(admin_blueprint, url_prefix='/admin')
FlaskApplication.register_blueprint(corp_management_blueprint, url_prefix='/corp_management')
FlaskApplication.register_blueprint(hr_blueprint, url_prefix='/hr')
FlaskApplication.register_blueprint(esi_parser_blueprint, url_prefix='/esi_parser')


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

    # Find main alliance
    alliance = Alliance.query.filter_by(id=SharedInfo['alliance_id']).first()

    return render_template('landing.html', alliance=alliance)


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
        flash('There was an error in EVE\'s response', 'danger')
        return redirect(url_for('login'))
    try:
        auth = EveAPI["default_user_preston"].authenticate(request.args['code'])
    except Exception as e:
        FlaskApplication.logger.error('ESI signing error: ' + str(e))
        flash('There was an authentication error signing you in.', 'danger')
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


@FlaskApplication.route('/eve/user/auth/callback')
@login_required
def eve_oath_full_callback():
    """Completes the EVE SSO login for a fully authed user. Here, a user's
    access and refresh token gets set.

    Args:
        None

    Returns:
        str: If nothing went wrong, redirect to the place they came from.
    """
    if 'error' in request.path:
        FlaskApplication.logger.error('Error in EVE SSO callback: ' + request.url)
        flash('There was an error in EVE\'s response', 'danger')
        return redirect(url_for('landing'))
    try:
        auth = EveAPI["full_auth_preston"].authenticate(request.args['code'])
    except Exception as e:
        FlaskApplication.logger.error('ESI signing error: ' + str(e))
        flash('There was an authentication error signing you in.', 'danger')
        return redirect(url_for('landing'))

    # Get character information
    characterInfo = auth.whoami()
    characterId = characterInfo['CharacterID']
    if current_user.id != characterId:
        flash("You have to authenticate the character you're applying with!", 'danger')
        FlaskApplication.logger.info("{} tried to fully authenticate with {}.".format(current_user.name, characterInfo['CharacterName']))
        return redirect(request.args.get('state'))

    current_user.access_token = auth.access_token
    current_user.refresh_token = auth.refresh_token
    Database.session.commit()

    FlaskApplication.logger.info("{} succesfully updated ESI for {} with access token {} and refresh token {}".format(
        current_user.name, current_user.name, str(auth.access_token), str(auth.refresh_token)))
    flash('Succesfully provided ESI.', 'success')

    return redirect(request.args.get('state'))


@FlaskApplication.route('/reddit/callback')
@login_required
def reddit_oath_callback():
    """Completes the reddit SSO login for a user.
    Here a user's reddit account gets set.

    Args:
        None

    Returns:
        str: If nothing went wrong, redirect to the place they came from.
    """
    SharedInfo['reddit'].auth.authorize(request.args['code'])
    current_user.reddit = str(SharedInfo['reddit'].user.me())
    Database.session.commit()
    FlaskApplication.logger.info("{} succesfully updated Reddit (/u/{})".format(current_user.name, current_user.reddit))
    flash("Successfully linked reddit account {}".format(current_user.reddit), 'success')

    return redirect(request.args.get('state'))


@FlaskApplication.route('/logout')
def logout():
    """Logs the user out of the site.

    Args:
        None

    Returns:
        str: redirect to the login endpoint
    """
    if current_user.is_anonymous:
        return redirect(url_for('landing'))

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
