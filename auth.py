import json
from functools import wraps
from urllib.request import urlopen

from flask import request
from jose import jwt, exceptions

AUTH0_DOMAIN = 'pet-checkin.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'pet-checkin'


# AuthError Exception
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header
def get_token_auth_header():
    if 'Authorization' not in request.headers:
        raise AuthError('Authorization header required', 401)

    auth_header = request.headers['Authorization']
    header_parts = auth_header.split(' ')

    if len(header_parts) != 2:
        raise AuthError('Malformed header', 401)
    elif header_parts[0].lower() != 'bearer':
        raise AuthError('Auth token needs to be bearer token', 401)

    return header_parts[1]


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError('Permissions not included in JWT.', 403)

    for user_permission in payload['permissions']:
        if user_permission in permission:
            return True
    raise AuthError('Permission not found.', 403)



def verify_decode_jwt(token):
    # GET THE PUBLIC KEY FROM AUTH0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # GET THE DATA IN THE HEADER
    try:
        unverified_header = jwt.get_unverified_header(token)
    except exceptions.JWTError:
        raise AuthError('Could not decode JWT token', 400)

    # CHOOSE OUR KEY
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError('Authorization malformed.', 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    # Finally, verify!!!
    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError('Token expired.', 401)

        except jwt.JWTClaimsError:
            raise AuthError('Incorrect claims. Please, check the audience and issuer.', 401)

        except Exception:
            raise AuthError('Unable to parse authentication token', 400)

    raise AuthError("Missing permissions", 403)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
