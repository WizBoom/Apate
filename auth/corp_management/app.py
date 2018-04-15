from flask import Blueprint, current_app, render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user
from auth.util import Util
from auth.decorators import needs_permission, alliance_required
from auth.shared import EveAPI
from auth.models import *
from auth.corp_management.forms import *

# Create and configure app
Application = Blueprint('corp_management', __name__, template_folder='templates/corp_management', static_folder='static')

# Util
Util = Util(
    current_app
)


@Application.route('/', methods=['GET', 'POST'])
@login_required
@alliance_required()
@needs_permission('corp_manager', 'Corp management Landing')
def index():
    # Get corp
    corporation = current_user.get_corp()

    # Check if recruitment is open or closed
    recruitmentValue = "closed"
    if corporation.recruitment_open:
        recruitmentValue = "open"
    editCorpForm = EditCorpForm(recruitmentStatus=recruitmentValue, description=corporation.inhouse_description)

    if request.method == 'POST':
        # If EditCorp has been pushed
        if request.form['btn'] == "EditCorp" and editCorpForm.validate_on_submit():
            # Check if recruitment status is open or closed
            if editCorpForm.recruitmentStatus.data == "closed":
                corporation.recruitment_open = False
            elif editCorpForm.recruitmentStatus.data == "open":
                corporation.recruitment_open = True

            # Update description
            corporation.inhouse_description = editCorpForm.description.data
            recruitmentStatus = "closed"
            if corporation.recruitment_open:
                recruitmentStatus = "open"

            Database.session.commit()
            current_app.logger.info('{} updated {}\'s description to "{}" and recruitment status to {}.'.format(
                current_user.name, corporation.name, corporation.inhouse_description, recruitmentStatus))
            flash('Updated {} description to "{}" and recruitment status to {}.'.format(corporation.name, corporation.inhouse_description, recruitmentStatus), 'success')

    return render_template('corp_management/index.html', corporation=corporation, corp_auth_url=EveAPI["corp_preston"].get_authorize_url(), editCorpForm=editCorpForm)


@Application.route('/eve/corp/callback')
@login_required
@alliance_required()
@needs_permission('corp_manager', 'Corp Management Corp Callback')
def eve_oauth_corp_callback():
    """Completes the EVE SSO CORP login. Here, a corp's ESI
    access & refresh token get updated.

    Args:
        None

    Returns:
        str: redirect to the appropriate url.
    """
    if 'error' in request.path:
        current_app.logger.error('Error in EVE SSO callback: ' + request.url)
        flash('There was an error in EVE\'s SSO response.', 'danger')
        return redirect(url_for('corp_management.index'))

    try:
        # Current logged in character's corporation
        currentCorp = current_user.get_corp()

        # Get character's corporation
        auth = EveAPI["corp_preston"].authenticate(request.args['code'])
        character_id = auth.whoami()['CharacterID']
        character_info = Util.make_esi_request("https://esi.tech.ccp.is/latest/characters/{}/?datasource=tranquility".format(str(character_id))).json()
        if character_info['corporation_id'] != currentCorp.id:
            current_app.logger.info("{} tried to add a corporation ESI code with a character ({}) that isn't in same corp ({}).".format(current_user.name, character_info['name'], currentCorp.name))
            flash("{} is not a member of your current corp ({}) and thus cannot provide a valid ESI code! If you're an admin double check what your current corp is set to.".format(
                character_info['name'], currentCorp.name), 'danger')
            return redirect(url_for('corp_management.index'))

        currentCorp.access_token = auth.access_token
        currentCorp.refresh_token = auth.refresh_token
        Database.session.commit()
        current_app.logger.info("{} (using {}) succesfully updated ESI for {} with access token {} and refresh token {}".format(
            current_user.name, character_info['name'], currentCorp.name, str(auth.access_token), str(auth.refresh_token)))
        flash('Succesfully updated ESI for {}'.format(currentCorp.name), 'success')

        return redirect(url_for('corp_management.index'))
    except Exception as e:
        current_app.logger.error('ESI signing error: ' + str(e))
        flash('There was an authentication error signing you in.', 'danger')
        return redirect(url_for('corp_management.index'))

    flash(code, 'danger')
    return redirect(url_for('corp_management.index'))
