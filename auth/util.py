import requests
from auth.models import *
from auth.shared import Database, SharedInfo
from flask import flash
import re


class Util:
    def __init__(self, application):
        self.Application = application

    def make_esi_request(self, request_link):
        """Makes an ESI request and logs / returns the necessary info.

        Args:
            request_link (str): Request link to send to ESI.

        Returns:
            response: Returns the ESI response object.
        """
        self.Application.logger.debug("make_esi_request > Making ESI request: " + request_link)

        esiRequest = requests.get(request_link, headers={'User-Agent': SharedInfo['user_agent']})

        if esiRequest.status_code != 200:
                self.Application.logger.error('make_esi_request > ESI request threw error {}'.format(str(esiRequest.status_code)))

        return esiRequest

    def make_esi_request_with_operation_id(self, preston, operation_id, request_link):
        """Makes an esi request to an endpoint that requires a certain scope.

        Args:
            preston (Preston): Preston instance that holds the scopes of the refresh token.
            operation_id (str): Operation ID of the endpoint.
            request_link (str): Request link to send to ESI.

        Returns:
            json: Returns either None if the request was invalid, or the json of the request.
        """

        if self.has_scope(preston, operation_id):
            payload = self.make_esi_request(request_link)
            return payload.json()
        return None

    def make_esi_request_with_scope(self, preston, scopes, request_link):
        """Makes an esi request to an endpoint that requires a certain scope.

        Args:
            preston (Preston): Preston instance that holds the scopes of the refresh token.
            scopes (list<str>): List of required scopes.
            request_link (str): Request link to send to ESI.

        Returns:
            json: Returns either None if the request was invalid, or the json of the request.
        """

        for scope in scopes:
            if scope not in preston.scope:
                return None

        payload = self.make_esi_request(request_link)
        return payload.json()

    def update_character_corporation(self, character, corp_id):
        """Updates the corporation of the character. If the new
        corporation does not exist, it will create one.

        Args:
            character (Character): Character to update.
            corp_id (int): New corporation ID.

        Returns:
            None
        """

        # Try to find corporation in the database with the given id.Character
        corporation = Corporation.query.filter_by(id=corp_id).first()

        # If there is no corporation with that corp id make a corp
        if not corporation:
            corporation = self.create_corporation(corp_id)

        # if nothing went wrong, add the character to the new corp
        if corporation and corporation.id != character.corp_id:
            corporation.characters.append(character)
            character.admin_corp_id = corporation.id
            Database.session.commit()

    def create_character(self, character_id, main_id=None):
        """Creates a character based on a character id and adds it to the database.

        Args:
            character_id (int): Character ID of the character to create.
            main_id (int): Optional main character ID.

        Returns:
            Character: Created character object.
        """

        # Check if corporation already exists
        character = Character.query.filter_by(id=character_id).first()
        if character:
            self.Application.logger.debug("create_character > Character with id {} already exists.".format(str(character_id)))
            return character

        characterJson = self.make_esi_request("https://esi.tech.ccp.is/latest/characters/{}/?datasource=tranquility".format(str(character_id))).json()

        # Log and return if the character does not exist
        if not characterJson:
            self.Application.logger.warning("create_character > Character with ID {} not found. Returning...".format(str(character_id)))
            return None

        # Make character
        character = Character(character_id, characterJson['name'], main_id if main_id is not None else character_id, "https://imageserver.eveonline.com/Character/{}_128.jpg".format(str(character_id)))
        Database.session.add(character)

        # Create corporation
        self.update_character_corporation(character, characterJson['corporation_id'])

        Database.session.commit()
        self.Application.logger.info("Created account for {}.".format(character.name))
        return character

    def create_corporation(self, corp_id):
        """Creates a corporation based on a corp id and adds it to the database.

        Args:
            corp_id (int): Corporation ID of the corporation to create.

        Returns:
            Corporation: Created corporation object.
        """

        # Check if corporation already exists
        corporation = Corporation.query.filter_by(id=corp_id).first()
        if corporation:
            self.Application.logger.debug("create_corporation > Corporation with id {} already exists.".format(str(corp_id)))
            return corporation

        corporationJson = self.make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/?datasource=tranquility".format(str(corp_id))).json()

        # Log and return if the corporation does not exist
        if not corporationJson:
            self.Application.logger.warning("create_corporation > Corporation with ID {} not found. Returning...".format(str(corp_id)))
            return None

        # Make corporation
        corporation = Corporation(corp_id, corporationJson['name'], corporationJson['ticker'],
                                  "http://image.eveonline.com/Corporation/{}_128.png".format(str(corp_id)))

        # Check if corporation has alliance
        if 'alliance_id' in corporationJson:
            allianceId = corporationJson['alliance_id']

            # Check if alliance already exists
            alliance = Alliance.query.filter_by(id=allianceId).first()

            if not alliance:
                # Create alliance
                alliance = self.create_alliance(allianceId)

                if alliance:
                    Database.session.add(alliance)
                else:
                    return

            alliance.corporations.append(corporation)

        Database.session.add(corporation)
        Database.session.commit()
        self.Application.logger.info("Created corporation {}.".format(corporation.name))
        return corporation

    def create_alliance(self, alliance_id):
        """Creates a alliance based on an alliance id and adds it to the database.

        Args:
            alliance_id (int): Alliance ID of the alliance to create.

        Returns:
            Alliance: Created alliance object.
        """

        # Check if alliance already exists
        alliance = Alliance.query.filter_by(id=alliance_id).first()
        if alliance:
            self.Application.logger.debug("create_alliance > Alliance with id {} already exists.".format(str(alliance_id)))
            return alliance

        allianceJson = self.make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/".format(str(alliance_id))).json()

        # Log and return if the alliance does not exist
        if not allianceJson:
            self.Application.logger.warning("create_alliance > Alliance with ID {} not found. Returning...".format(str(alliance_id)))
            return None

        # Make alliance
        alliance = Alliance(alliance_id, allianceJson['name'], allianceJson['ticker'],
                            "http://image.eveonline.com/Alliance/{}_128.png".format(str(alliance_id)))

        Database.session.add(alliance)
        Database.session.commit()
        self.Application.logger.info("Created alliance {}.".format(alliance.name))
        return alliance

    def create_all_corporations_in_alliance(self, alliance_id):
        """Creates all the corporations in an alliance based on an alliance id and adds it to the database.

        Args:
            alliance_id (int): Alliance ID of the alliance to fill.

        Returns:
            None
        """

        allianceJson = self.make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/corporations/".format(str(alliance_id))).json()

        # Log and return if the alliance does not exist
        if not allianceJson:
            self.Application.logger.warning("create_all_corporations_in_alliance > Alliance with ID {} not found. Returning...".format(str(alliance_id)))
            return None

        for corporation_id in allianceJson:
            self.create_corporation(corporation_id)

    def remove_role(self, role_name, executing_user_name="System", html_flash=False):
        """Removes a role based on the role name.

        Args:
            role_name (string): Name of the role to delete.
            html_flash (boolean): If enabled, flash a message on screen to notify the user.
            executing_user_name (string): Name of the user deleting.

        Returns:
            None
        """

        # Find the role that needs to be removed
        role = Role.query.filter_by(name=role_name).first()

        # Double check if there is actually a role with that name
        # This should always be the case though
        if role:
            if not role.has_permission("admin"):
                Database.session.delete(role)
                Database.session.commit()
                if html_flash:
                    flash('Succesfully removed role {}.'.format(role.name), 'success')
                self.Application.logger.info('{} removed role {}.'.format(executing_user_name, role.name))
            elif html_flash:
                flash('You cannot remove an admin role!', 'danger')

    def has_scope(self, preston, operation_id):
        """Checks if preston instance has the correct scope for a certain operation id.

        Args:
            preston (Preston): Preston object to get the scopes from.
            operation_id (str): Operation ID to check scopes for.

        Returns:
            bool: If true, the preston instance has the scope.
        """

        path = preston._get_path_for_op_id(operation_id)
        if path is None:
            self.Application.logger.error('has_scope > No path found for operation ID {}.'.format(operation_id))
            return False

        pathSpec = preston._get_spec()['paths'][path]
        for key in pathSpec:
            if pathSpec[key].get('security'):
                if pathSpec[key]['security'][0]['evesso'][0] not in preston.scope:
                    return False
        return True

    def string_to_datetime(self, string, format):
        """Converts string to datetime.

        Args:
            string (str): string to convert.
            format (str): format of the string.

        Returns:
            datetime: datetime converted from string.
        """

        return datetime.strptime(string, format)

    def datetime_to_string(self, datetime, format):
        """Converts string to datetime.

        Args:
            datetime (datetime): datetime to convert.
            format (str): format of the string.

        Returns:
            string: datetime converted from string.
        """

        return datetime.strftime(format)

    def age_from_now(self, datetime):
        """Get age from now in years, months and days.

        Args:
            datetime (datetime): date to check.

        Returns:
            str: age in years, months & days.
        """

        days = (datetime.utcnow() - datetime).days
        years = int(days / 365)
        days -= years * 365
        months = int(days / 30)
        days -= months * 30
        return "{} years, {} months and {} days".format(years, months, days)

    def remove_html_tags(self, text):
        """Remove all html tags from a string.

        Args:
            text (str): Text to remove the tags from.

        Returns:
            str: String without tags.
        """
        tag = re.compile(r'<[^>]+>')
        return tag.sub('', text)
