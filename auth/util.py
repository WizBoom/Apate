import requests
from auth.models import *
from auth.shared import Database


class Util:
    def __init__(self, application, user_agent):
        self.Application = application
        self.UserAgent = user_agent

    def make_esi_request(self, request_link):
        """Makes an ESI request and logs / returns the necessary info.

        Args:
            request_link (str): Request link to send to ESI.

        Returns:
            json: Returns the requested ESI object.
        """
        self.Application.logger.debug("make_esi_request > Making ESI request: " + request_link)
        return requests.get(request_link, headers={'User-Agent': self.UserAgent}).json()

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
            Database.session.commit()

    def create_character(self, character_id):
        """Creates a character based on a character id and adds it to the database.

        Args:
            character_id (int): Character ID of the character to create.

        Returns:
            Character: Created character object.
        """
        character_json = self.make_esi_request("https://esi.tech.ccp.is/latest/characters/{}/?datasource=tranquility".format(str(character_id)))

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
        corporation_json = self.make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/?datasource=tranquility".format(str(corp_id)))

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
        alliance_json = self.make_esi_request("https://esi.tech.ccp.is/latest/alliances/{}/".format(str(alliance_id)))

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
