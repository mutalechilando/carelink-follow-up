from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


TOKENS = {
    "clinician-mwansa": {
        "role": "CLINICIAN",
        "facility_id": "FAC-0101",
    },
    "clinician-kalemba": {
        "role": "CLINICIAN",
        "facility_id": "FAC-0207",
    },
    "district-chembe": {
        "role": "DISTRICT_OFFICER",
        "facility_id": None,
    },
}


class CareLinkUser:
    def __init__(self, role, facility_id=None):
        self.role = role
        self.facility_id = facility_id

    @property
    def is_authenticated(self):
        return True


class StaticTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = request.headers.get("Authorization", "")

        if not header.startswith("Token "):
            return None

        token = header.removeprefix("Token ").strip()
        identity = TOKENS.get(token)

        if identity is None:
            raise AuthenticationFailed("Invalid authentication token.")

        return (
            CareLinkUser(
                role=identity["role"],
                facility_id=identity["facility_id"],
            ),
            token,
        )