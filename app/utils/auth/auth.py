from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import current_app, jsonify, request


def get_jwt(payload):
    """
    Encode the payload to create a JWT.
    Adds expiration time and issuer/audience information.
    """
    # Adding the expiration, issuer, and audience claims
    issuer = current_app.config['JWT_ISSUER']
    audience = current_app.config['JWT_AUDIENCE']
    expiration = current_app.config['JWT_EXPIRATION']
    payload.update({
        'exp': datetime.now() + timedelta(seconds=expiration),
        'iat': datetime.now(),
        'iss': issuer,
        'aud': audience
    })
    # Encode the JWT using the application's secret key
    return jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm="HS256")


def decode_jwt(token):
    """
    Decode the JWT and return the payload if valid.
    Handles expired and invalid token errors.
    """
    issuer = current_app.config['JWT_ISSUER']
    audience = current_app.config['JWT_AUDIENCE']

    try:
        # Decode the JWT using the application's secret key and expected algorithms
        return jwt.decode(token, current_app.config['JWT_SECRET'],
                          algorithms=["HS256"],
                          issuer=issuer,
                          audience=audience)
    except jwt.ExpiredSignatureError:
        # Handle token expiration
        raise ValueError('Token expired')
    except jwt.InvalidIssuerError:
        # Handle invalid issuer errors
        raise ValueError('Invalid issuer')
    except jwt.InvalidAudienceError:
        # Handle invalid audience errors
        raise ValueError('Invalid audience')
    except jwt.InvalidTokenError as e:
        # Handle any invalid token errors
        current_app.logger.error(f"Invalid token: {e}")
        raise ValueError('Invalid token')


def get_user_id(token):
    """
    Extract the user ID from the JWT.
    """
    try:
        payload = decode_jwt(token)
        # Return the 'sub' claim as the user ID if it exists
        return payload.get('sub')
    except Exception as e:
        # Log or handle decoding errors
        current_app.logger.error(f"Error decoding token: {e}")
        return None


def token_required(f):
    """
    Decorator that requires a valid JWT for the endpoint.
    Passes the user_id from the token to the endpoint.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        # Retrieve the token from the Authorization header
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token to get the user ID
            payload = decode_jwt(token)
            user_id = payload.get('sub')
            if not user_id:
                return jsonify({'message': 'Token is invalid!'}), 401

            # Pass the user ID to the endpoint
            kwargs['sub'] = user_id
        except ValueError as e:
            current_app.logger.error(f"Token error: {e}")
            return jsonify({'message': str(e)}), 401

        return f(*args, **kwargs)

    return decorated


def firewall(f):
    """
    Decorator to restrict access based on IP addresses.
    Allows access if the IP is in NO_AUTH_IPS configuration.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the client's IP address is in the list of allowed IPs
        if request.remote_addr in current_app.config.get('NO_AUTH_IPS', []):
            return f(*args, **kwargs)
        else:
            return jsonify({'message': 'Access denied!'}), 403

    return decorated_function
