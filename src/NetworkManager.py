import requests


class UnauthenticatedError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class InvalidResponseError(Exception):
    pass


class NetworkManager:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.token = ""

    def register_device(self, hardware_id: str) -> str:
        payload = {"device": hardware_id}
        headers = {"Content-type": "application/json", "Accept": "application/json"}
        request = requests.get(
            self.endpoint + "/api/register", params=payload, headers=headers
        )

        status = request.status_code

        if status == 200:
            if request.json()["token"]:
                self.token = request.json()["token"]
                return self.token

        return None

    def _auth_header(self) -> dict:
        return {
            "Authorization": "Bearer " + self.token,
            "Content-type": "application/json",
            "Accept": "application/json",
        }

    def fetch_messages(self) -> dict:
        if self.token:
            request = requests.get(
                self.endpoint + "/api/messages", headers=self._auth_header()
            )

            if request.status_code == 200:
                response = request.json()

                if "message" in response and "settings" in response:
                    return response

                raise InvalidResponseError("InvalidResponseError: " + response)

            elif request.status_code == 401:
                raise UnauthenticatedError()

        raise InvalidTokenError()

    def read_message(self, message_id: int) -> bool:
        if self.token and message_id:
            requests.patch(
                self.endpoint + f"/api/messages/{message_id}",
                headers=self._auth_header(),
            )
            return True

        raise InvalidTokenError()
