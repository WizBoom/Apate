from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import current_user
from auth.shared import EveAPI, SharedInfo
from preston import Preston

# Create and configure app
Application = Blueprint('esi_parser', __name__, template_folder='templates/esi', static_folder='static')


@Application.route('/')
def index():
    """Landing page of the ESI parser.

    Args:
        None

    Returns:
        str: redirect to the appropriate url.
    """
    return render_template('esi_parser/index.html')


@Application.route('/audit/<int:character_id>/<refresh_token>/<scopes>')
def audit(character_id, refresh_token, scopes):
    """Views a member with ID.

    Args:
        character_id (int): ID of the character.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """
    # Get character.
    characterPayload = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/characters/{}/?datasource=tranquility".format(str(character_id)))
    if characterPayload.status_code != 200:
        flash('There was an error ({}) when trying to retrieve character with ID {}'.format(str(characterPayload.status_code), str(character_id)), 'danger')
        return redirect(url_for('esi_parser.index'))

    characterJSON = characterPayload.json()
    characterPortrait = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/characters/{}/portrait/?datasource=tranquility".format(str(character_id))).json()

    # Get corporation.
    corporationPayload = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/?datasource=tranquility".format(str(characterJSON['corporation_id'])))
    if corporationPayload.status_code != 200:
        flash('There was an error ({}) when trying to retrieve character with ID {}'.format(str(corporationPayload.status_code), str(characterJSON['corporation_id'])), 'danger')
        return redirect(url_for('esi_parser.index'))

    corporationJSON = corporationPayload.json()
    corporationLogo = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/icons/?datasource=tranquility".format(str(characterJSON['corporation_id']))).json()

    # Get alliance.
    allianceJSON = None
    allianceLogo = None
    if 'alliance_id' in characterJSON:
        alliancePayload = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/?datasource=tranquility".format(str(characterJSON['alliance_id'])))
        if alliancePayload.status_code != 200:
            flash('There was an error ({}) when trying to retrieve character with ID {}'.format(str(alliancePayload.status_code), str(characterJSON['alliance_id'])), 'danger')
            return redirect(url_for('esi_parser.index'))

        allianceJSON = alliancePayload.json()
        allianceLogo = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/icons/?datasource=tranquility".format(str(characterJSON['alliance_id']))).json()

    # Make preston instance.
    preston = Preston(
        user_agent=EveAPI['user_agent'],
        client_id=EveAPI['full_auth_preston'].client_id,
        client_secret=EveAPI['full_auth_preston'].client_secret,
        scope=EveAPI['full_auth_preston'].scope,
        refresh_token=refresh_token
    )

    # Get access token.
    access_token = preston._get_access_from_refresh()[0]
    if access_token is None:
        flash('Refresh token ({}) could not get an access token.'.format(refresh_token), 'danger')
        current_app.logger.error('{} tried to parse ESI for character {} but the refresh token ({}) was not valid'.format(current_user.name, characterJSON['name'], refresh_token))

    # Get wallet.
    walletISK = SharedInfo['util'].make_esi_request_with_operation_id(preston, 'get_characters_character_id_wallet', True,
                                                                      "https://esi.tech.ccp.is/latest/characters/{}/wallet/?datasource=tranquility&token={}".format(str(character_id), access_token))
    if walletISK is None:
        return redirect(url_for('esi_parser.index'))

    # Get skillpoints
    characterSkills = SharedInfo['util'].make_esi_request_with_operation_id(preston, 'get_characters_character_id_wallet', True,
                                                                            "https://esi.tech.ccp.is/latest/characters/{}/skills/?datasource=tranquility&token={}".format(
                                                                                str(character_id), access_token))
    if characterSkills is None:
        return redirect(url_for('esi_parser.index'))

    return render_template('esi_parser/audit.html',
                           character=characterJSON, character_portrait=characterPortrait,
                           corporation=corporationJSON, corporation_logo=corporationLogo,
                           alliance=allianceJSON, alliance_logo=allianceLogo,
                           wallet_isk=walletISK, character_skills=characterSkills)
