from ninja.security import HttpBearer
from rest_framework.authtoken.models import Token


class TokenAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            token_obj = Token.objects.get(key=token)
            request.user = token_obj.user
            return token_obj.user
        except Token.DoesNotExist:
            return None


auth = TokenAuth()
