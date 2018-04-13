import requests
from auth.models import *
from auth.shared import Database, SharedInfo
from flask import flash


class Util:
    def __init__(self, application):
        self.Application = application

    def make_esi_request(self, request_link):
        """Makes an ESI request and logs / returns the necessary info.

        Args:
            request_link (str): Request link to send to ESI.

        Returns:
            json: Returns the requested ESI object.
        """
        self.Application.logger.debug("make_esi_request > Making ESI request: " + request_link)
        return requests.get(request_link, headers={'User-Agent': SharedInfo['user_agent']})

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
        if corporation:
            corporation.characters.append(character)
            character.admin_corp_id = corporation.id
            Database.session.commit()

    def create_character(self, character_id):
        """Creates a character based on a character id and adds it to the database.

        Args:
            character_id (int): Character ID of the character to create.

        Returns:
            Character: Created character object.
        """

        # Check if corporation already exists
        character = Character.query.filter_by(id=character_id).first()
        if character:
            self.Application.logger.debug("create_character > Character with id {} already exists.".format(str(character_id)))
            return character

        character_json = self.make_esi_request("https://esi.tech.ccp.is/latest/characters/{}/?datasource=tranquility".format(str(character_id))).json()

        # Log and return if the character does not exist
        if not character_json:
            self.Application.logger.warning("create_character > Character with ID {} not found. Returning...".format(str(character_id)))
            return None

        # Make character
        character = Character(character_id, character_json['name'])
        Database.session.add(character)

        # Create corporation
        self.update_character_corporation(character, character_json['corporation_id'])

        Database.session.commit()
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

        corporation_json = self.make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/?datasource=tranquility".format(str(corp_id))).json()

        # Log and return if the corporation does not exist
        if not corporation_json:
            self.Application.logger.warning("create_corporation > Corporation with ID {} not found. Returning...".format(str(corp_id)))
            return None

        # Make corporation
        corporation = Corporation(corp_id, corporation_json['name'], corporation_json['ticker'],
                                  "http://image.eveonline.com/Corporation/{}_128.png".format(str(corp_id)))

        # Check if corporation has alliance
        if 'alliance_id' in corporation_json:
            alliance_id = corporation_json['alliance_id']

            # Check if alliance already exists
            alliance = Alliance.query.filter_by(id=alliance_id).first()

            if not alliance:
                # Create alliance
                alliance = self.create_alliance(alliance_id)

                if alliance:
                    Database.session.add(alliance)
                else:
                    return

            alliance.corporations.append(corporation)

        Database.session.add(corporation)
        Database.session.commit()
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

        alliance_json = self.make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/".format(str(alliance_id))).json()

        # Log and return if the alliance does not exist
        if not alliance_json:
            self.Application.logger.warning("create_alliance > Alliance with ID {} not found. Returning...".format(str(alliance_id)))
            return None

        # Make alliance
        alliance = Alliance(alliance_id, alliance_json['name'], alliance_json['ticker'],
                            "http://image.eveonline.com/Alliance/{}_128.png".format(str(alliance_id)))

        Database.session.add(alliance)
        Database.session.commit()
        return alliance

    def create_all_corporations_in_alliance(self, alliance_id):
        """Creates all the corporations in an alliance based on an alliance id and adds it to the database.

        Args:
            alliance_id (int): Alliance ID of the alliance to fill.

        Returns:
            None
        """

        alliance_json = self.make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/corporations/".format(str(alliance_id))).json()

        # Log and return if the alliance does not exist
        if not alliance_json:
            self.Application.logger.warning("create_all_corporations_in_alliance > Alliance with ID {} not found. Returning...".format(str(alliance_id)))
            return None

        for corporation_id in alliance_json:
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
