from flask import Blueprint, render_template, redirect, url_for, flash
from auth.shared import EveAPI, SharedInfo

# Create and configure app
Application = Blueprint('esi_parser', __name__, template_folder='templates/esi', static_folder='static')


@Application.route('/')
def index():
    return render_template('esi_parser/index.html')


@Application.route('/audit/<int:character_id>/<access_code>/<scopes>')
def audit(character_id, access_code, scopes):
    # Get character
    characterPayload = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/characters/{}/?datasource=tranquility".format(str(character_id)))
    if characterPayload.status_code != 200:
        flash('There was an error ({}) when trying to retrieve character with ID {}'.format(str(characterPayload.status_code), str(character_id)), 'danger')
        return redirect(url_for('esi_parser.index'))

    characterJSON = characterPayload.json()
    characterPortrait = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/characters/{}/portrait/?datasource=tranquility".format(str(character_id))).json()

    # Get corporation
    corporationPayload = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/?datasource=tranquility".format(str(characterJSON['corporation_id'])))
    if corporationPayload.status_code != 200:
        flash('There was an error ({}) when trying to retrieve character with ID {}'.format(str(corporationPayload.status_code), str(characterJSON['corporation_id'])), 'danger')
        return redirect(url_for('esi_parser.index'))

    corporationJSON = corporationPayload.json()
    corporationLogo = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/icons/?datasource=tranquility".format(str(characterJSON['corporation_id']))).json()

    # Get alliance
    allianceJSON = None
    allianceLogo = None
    if 'alliance_id' in characterJSON:
        alliancePayload = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/?datasource=tranquility".format(str(characterJSON['alliance_id'])))
        if alliancePayload.status_code != 200:
            flash('There was an error ({}) when trying to retrieve character with ID {}'.format(str(alliancePayload.status_code), str(characterJSON['alliance_id'])), 'danger')
            return redirect(url_for('esi_parser.index'))

        allianceJSON = alliancePayload.json()
        allianceLogo = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/icons/?datasource=tranquility".format(str(characterJSON['alliance_id']))).json()

    return render_template('esi_parser/audit.html',
                           character=characterJSON, character_portrait=characterPortrait,
                           corporation=corporationJSON, corporation_logo=corporationLogo,
                           alliance=allianceJSON, alliance_logo=allianceLogo)
