from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request, Markup
from flask_login import current_user, login_required
from auth.shared import EveAPI, SharedInfo
from preston import Preston
from auth.decorators import needs_permission

# Create and configure app
Application = Blueprint('esi_parser', __name__, template_folder='templates/esi', static_folder='static')


@Application.route('/', methods=['GET', 'POST'])
@login_required
@needs_permission('parse_esi', 'ESI Index')
def index():
    """Landing page of the ESI parser.

    Args:
        None

    Returns:
        str: redirect to the appropriate url.
    """

    if request.method == 'POST':
        return redirect(url_for('esi_parser.audit_assets', character_id=request.form['characterIDText'], client_id=request.form['clientIDText'],
                                client_secret=request.form['clientSecretText'], refresh_token=request.form['refreshTokenText'], scopes=request.form['scopeTextArea']))

    return render_template('esi_parser/index.html')


@Application.route('/audit/assets/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_assets(character_id, client_id, client_secret, refresh_token, scopes):
    """Audit a character's assets.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('esi_parser/audit_assets.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes)


@Application.route('/audit/bookmarks/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_bookmarks(character_id, client_id, client_secret, refresh_token, scopes):
    """Audit a character's bookmarks.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('esi_parser/audit_bookmarks.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes)


@Application.route('/audit/character/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_character(character_id, client_id, client_secret, refresh_token, scopes):
    """Audit a character's character.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('esi_parser/audit_character.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes)


@Application.route('/audit/clones/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_clones(character_id, client_id, client_secret, refresh_token, scopes):
    """Audit a character's clones.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('esi_parser/audit_clones.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes)


@Application.route('/audit/contacts/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_contacts(character_id, client_id, client_secret, refresh_token, scopes):
    """Audit a character's contacts.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('esi_parser/audit_contacts.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes)


@Application.route('/audit/contracts/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_contracts(character_id, client_id, client_secret, refresh_token, scopes):
    """Audit a character's contracts.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('esi_parser/audit_contracts.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes)


@Application.route('/audit/corporation/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_corporation(character_id, client_id, client_secret, refresh_token, scopes):
    """Audit a character's corporation.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('esi_parser/audit_corporation.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes)


@Application.route('/audit/fw/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_fw(character_id, client_id, client_secret, refresh_token, scopes):
    """Audit a character's FW stats.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('esi_parser/audit_fw.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes)


@Application.route('/audit/fittings/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_fittings(character_id, client_id, client_secret, refresh_token, scopes):
    """Audit a character's fittings.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('esi_parser/audit_fittings.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes)


@Application.route('/audit/industry/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_industry(character_id, client_id, client_secret, refresh_token, scopes):
    """Audit a character's industry.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('esi_parser/audit_industry.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes)


@Application.route('/audit/location/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_location(character_id, client_id, client_secret, refresh_token, scopes):
    """Audit a character's location.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('esi_parser/audit_location.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes)


@Application.route('/audit/lp/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_lp(character_id, client_id, client_secret, refresh_token, scopes):
    """Audit a character's LP.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('esi_parser/audit_lp.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes)


@Application.route('/audit/mail/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_mail(character_id, client_id, client_secret, refresh_token, scopes):
    """Audit a character's mail.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('esi_parser/audit_mail.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes)


@Application.route('/audit/market/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_market(character_id, client_id, client_secret, refresh_token, scopes):
    """Audit a character's market.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('esi_parser/audit_market.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes)


@Application.route('/audit/opportunities/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_opportunities(character_id, client_id, client_secret, refresh_token, scopes):
    """Audit a character's opportunities.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('esi_parser/audit_opportunities.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes)


@Application.route('/audit/pi/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_pi(character_id, client_id, client_secret, refresh_token, scopes):
    """Audit a character's PI.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('esi_parser/audit_pi.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes)


@Application.route('/audit/skills/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_skills(character_id, client_id, client_secret, refresh_token, scopes):
    """Audit a character's skills.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('esi_parser/audit_skills.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes)


@Application.route('/audit/wallet/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_wallet(character_id, client_id, client_secret, refresh_token, scopes):
    """Audit a character's wallet.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
        refresh_token (str): Refresh token of the character.
        scopes (str): Scopes that the refresh token provides access to.

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('esi_parser/audit_wallet.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes)


@Application.route('/audit/onepage/<int:character_id>/<client_id>/<client_secret>/<refresh_token>/<scopes>')
@login_required
@needs_permission('parse_esi', 'ESI Audit')
def audit_onepage(character_id, client_id, client_secret, refresh_token, scopes):
    """Views a member with ID.

    Args:
        character_id (int): ID of the character.
        client_id (str): Client ID of the SSO that was used to retrieve the refresh token.
        client_secret (str): Client secret of the SSO that was used to retrieve the refresh token.
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
        client_id=client_id,
        client_secret=client_secret,
        scope=scopes,
        refresh_token=refresh_token
    )

    # Get access token.
    access_token = preston._get_access_from_refresh()[0]
    if access_token is None:
        flash('Refresh token ({}) could not get an access token.'.format(refresh_token), 'danger')
        current_app.logger.error('{} tried to parse ESI for character {} but the refresh token ({}) was not valid'.format(current_user.name, characterJSON['name'], refresh_token))

    # Get wallet.
    walletISK = SharedInfo['util'].make_esi_request_with_scope(preston, ['esi-wallet.read_character_wallet.v1'],
                                                               "https://esi.tech.ccp.is/latest/characters/{}/wallet/?datasource=tranquility&token={}".format(str(character_id), access_token))
    if walletISK is not None and type(walletISK) is not float:
        return redirect(url_for('esi_parser.index'))

    # Get skillpoints
    characterSkills = SharedInfo['util'].make_esi_request_with_scope(preston, ['esi-skills.read_skills.v1'],
                                                                     "https://esi.tech.ccp.is/latest/characters/{}/skills/?datasource=tranquility&token={}".format(
        str(character_id), access_token))
    if characterSkills is not None and 'error' in characterSkills:
        return redirect(url_for('esi_parser.index'))

    # Get contact endpoints.
    # We use labels endpoint because the normal operation id requires write access as well for some reason.
    characterContacts = SharedInfo['util'].make_esi_request_with_scope(preston, ['esi-characters.read_contacts.v1'],
                                                                       "https://esi.tech.ccp.is/latest/characters/{}/contacts/?datasource=tranquility&token={}".format(
        str(character_id), access_token))
    if characterContacts is not None and 'error' in characterContacts:
        return redirect(url_for('esi_parser.index'))

    characterContactLabels = SharedInfo['util'].make_esi_request_with_scope(preston, ['esi-characters.read_contacts.v1'],
                                                                            "https://esi.tech.ccp.is/latest/characters/{}/contacts/labels/?datasource=tranquility&token={}".format(
        str(character_id), access_token))
    if characterContactLabels is not None and 'error' in characterContactLabels:
        return redirect(url_for('esi_parser.index'))

    # Link characters, corporations, images and labels to contacts.
    for contact in characterContacts:
        # Name.
        if contact['contact_type'] == 'character':
            # Get character.
            character = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/characters/{}/?datasource=tranquility".format(str(contact['contact_id']))).json()
            contact['character'] = character

            # Get character corp.
            contact['character']['corporation_name'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/?datasource=tranquility".format(
                str(character['corporation_id']))).json()['name']

            # Get character corp logo.
            contact['character']['corporation_logo'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/icons/?datasource=tranquility".format(
                str(character['corporation_id']))).json()['px128x128']

            # Get character alliance if applicable.
            if 'alliance_id' in character:
                contact['character']['alliance_name'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/?datasource=tranquility".format(
                    str(character['alliance_id']))).json()['name']

                # Get character alliance logo.
                contact['character']['alliance_logo'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/icons/?datasource=tranquility".format(
                    str(character['alliance_id']))).json()['px128x128']

            # Get corporation history.
            corpHistory = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/characters/{}/corporationhistory/?datasource=tranquility".format(str(contact['contact_id']))).json()
            for index, corp in enumerate(corpHistory):
                # Name.
                corp['name'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/?datasource=tranquility".format(
                    str(corp['corporation_id']))).json()['name']

                # Logo.
                corp['logo'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/icons/?datasource=tranquility".format(
                    str(corp['corporation_id']))).json()['px128x128']

                # Leave date.
                if index > 0:
                    corp['end_date'] = corpHistory[index - 1]['start_date']
            contact['character']['corporation_history'] = corpHistory

            # Get contact name / image.
            contact['contact_name'] = character['name']
            contact['contact_image'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/characters/{}/portrait/?datasource=tranquility".format(
                str(contact['contact_id']))).json()['px128x128']
        elif contact['contact_type'] == 'corporation':
            # Get corporation.
            corporation = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/?datasource=tranquility".format(str(contact['contact_id']))).json()
            contact['corporation'] = corporation

            # Get corporation alliance.
            if 'alliance_id' in corporation:
                contact['corporation']['alliance_name'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/?datasource=tranquility".format(
                    str(corporation['alliance_id']))).json()['name']

                # Get corporation alliance logo.
                contact['corporation']['alliance_logo'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/icons/?datasource=tranquility".format(
                    str(corporation['alliance_id']))).json()['px128x128']

            # Get alliance history.
            allianceHistory = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/alliancehistory/?datasource=tranquility".format(str(contact['contact_id']))).json()
            for index, alliance in enumerate(allianceHistory):
                allianceJSON = None

                if 'alliance_id' in alliance:
                    allianceJSON = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/?datasource=tranquility".format(
                        str(alliance['alliance_id']))).json()

                    allianceJSON['alliance_id'] = alliance['alliance_id']

                # Name.
                if allianceJSON:
                    alliance['name'] = allianceJSON['name']
                else:
                    alliance['name'] = "No alliance"

                # Logo.
                if allianceJSON:
                    alliance['logo'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/icons/?datasource=tranquility".format(
                        str(alliance['alliance_id']))).json()['px128x128']

                # Leave date.
                if index > 0:
                    alliance['end_date'] = allianceHistory[index - 1]['start_date']

            contact['corporation']['alliance_history'] = allianceHistory

            # Get contact name / image.
            contact['contact_name'] = corporation['name']
            contact['contact_image'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/icons/?datasource=tranquility".format(
                str(contact['contact_id']))).json()['px128x128']
        elif contact['contact_type'] == 'alliance':
            # Get alliance.
            alliance = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/?datasource=tranquility".format(str(contact['contact_id']))).json()
            contact['alliance'] = alliance

            # Exec corp.
            if 'executor_corporation_id' in alliance:
                # Name.
                contact['alliance']['executor_corporation_name'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/?datasource=tranquility".format(
                    str(alliance['executor_corporation_id']))).json()['name']

                # Logo.
                contact['alliance']['executor_corporation_logo'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/icons/?datasource=tranquility".format(
                    str(alliance['executor_corporation_id']))).json()['px128x128']

            # Alliance members.
            allianceMembers = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/corporations/?datasource=tranquility".format(
                str(contact['contact_id']))).json()

            allianceMemberList = []
            for member in allianceMembers:
                # Corporation info.
                memberJSON = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/?datasource=tranquility".format(
                    str(member))).json()

                # ID.
                memberJSON['corporation_id'] = member

                # Logo.
                memberJSON['corporation_logo'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/icons/?datasource=tranquility".format(
                    str(member))).json()['px128x128']

                # Get corp.
                allianceMemberList.append(memberJSON)

            contact['alliance']['members'] = allianceMemberList

            contact['contact_name'] = alliance['name']
            contact['contact_image'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/icons/?datasource=tranquility".format(
                str(contact['contact_id']))).json()['px128x128']
        elif contact['contact_type'] == 'faction':
            contact['contact_name'] = "FACTION NAMES NOT IMPLEMENTED"
            contact['contact_image'] = "#"

        # Labels.
        if 'label_id' in contact:
            for label in characterContactLabels:
                if label['label_id'] == contact['label_id']:
                    contact['label_name'] = label['label_name']

    # Sort contacts by name.
    characterContacts = sorted(characterContacts, key=lambda k: k['contact_name'])

    # Sort contacts by standings.
    characterContacts = sorted(characterContacts, key=lambda k: k['standing'], reverse=True)

    # Get mail endpoint.
    characterMails = SharedInfo['util'].make_esi_request_with_scope(preston, ['esi-mail.read_mail.v1'],
                                                                    "https://esi.tech.ccp.is/latest/characters/{}/mail/?datasource=tranquility&token={}".format(
        str(character_id), access_token))

    # Get mailing lists.
    characterMailingLists = SharedInfo['util'].make_esi_request_with_scope(preston, ['esi-mail.read_mail.v1'],
                                                                           "https://esi.tech.ccp.is/latest/characters/{}/mail/lists/?datasource=tranquility&token={}".format(
        str(character_id), access_token))

    if characterMails is not None and 'error' in characterMails:
        return redirect(url_for('esi_parser.index'))

    for mail in characterMails:
        mail['mail'] = SharedInfo['util'].make_esi_request_with_scope(preston, ['esi-mail.read_mail.v1'],
                                                                      "https://esi.tech.ccp.is/latest/characters/{}/mail/{}/?datasource=tranquility&token={}".format(
            str(character_id), str(mail['mail_id']), access_token))

        # Convert body to be easily showed in html, but first save raw body.
        mail['mail']['raw_body'] = mail['mail']['body']
        mailBody = mail['mail']['body'].replace('<br>', '\n')
        mailBody = SharedInfo['util'].remove_html_tags(mailBody)
        mail['mail']['body'] = Markup(mailBody.replace('\n', '<br>'))

        # Get sender name.
        mail['mail']['from_name'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/characters/{}/?datasource=tranquility".format(
            str(mail['mail']['from']))).json()['name']

        # Get recipients.
        for recipient in mail['mail']['recipients']:
            recipient['recipient_name'] = recipient['recipient_id']

            # Determine type.
            if recipient['recipient_type'] == 'character':
                # Get character name.
                recipient['recipient_name'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/characters/{}/?datasource=tranquility".format(
                    str(recipient['recipient_id']))).json()['name']
            elif recipient['recipient_type'] == 'corporation':
                # Get corporation name.
                recipient['recipient_name'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/?datasource=tranquility".format(
                    str(recipient['recipient_id']))).json()['name']
            elif recipient['recipient_type'] == 'alliance':
                # Get alliance name.
                recipient['recipient_name'] = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/?datasource=tranquility".format(
                    str(recipient['recipient_id']))).json()['name']
            elif recipient['recipient_type'] == 'mailing_list':
                # Get mailing list name.
                for mailingList in characterMailingLists:
                    if mailingList['mailing_list_id'] == recipient['recipient_id']:
                        recipient['recipient_name'] = "{} [ML]".format(mailingList['name'])

    return render_template('esi_parser/audit_onepage.html',
                           character_id=character_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token, scopes=scopes,
                           character=characterJSON, character_portrait=characterPortrait,
                           corporation=corporationJSON, corporation_logo=corporationLogo,
                           alliance=allianceJSON, alliance_logo=allianceLogo,
                           wallet_isk=walletISK, character_skills=characterSkills, character_contacts=characterContacts,
                           character_mails=characterMails)
