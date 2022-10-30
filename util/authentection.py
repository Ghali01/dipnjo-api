from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import User

class TokenAuth(BaseAuthentication):

    def authenticate(self, request):
        if 'Authorization' in request.headers:
            
            token=request.headers['Authorization'].strip().replace("Token ",'')
            try:
                user=User.objects.get(token=token)
                return (user,token)
            except :
                pass
        raise AuthenticationFailed()
        return None
        