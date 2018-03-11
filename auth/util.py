import requests


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
        self.Application.logger.debug(request_link)
        return requests.get(request_link, headers={'User-Agent': self.UserAgent}).json()
