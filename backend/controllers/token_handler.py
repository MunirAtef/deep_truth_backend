import os
import time

from functools import wraps
import jwt
from flask import request
from dotenv import load_dotenv
from werkzeug.exceptions import UnsupportedMediaType

from backend.logger.logger import Logger

load_dotenv()
ACCESS_TOKEN_SECRET_KEY = os.getenv('ACCESS_TOKEN_SECRET_KEY')
REFRESH_TOKEN_SECRET_KEY = os.getenv('REFRESH_TOKEN_SECRET_KEY')


class TokenHandler:
    @staticmethod
    def generate_access_token(user_id: str) -> str:
        payload = {"id": user_id, 'exp': int(time.time()) + 13600}
        return jwt.encode(payload, ACCESS_TOKEN_SECRET_KEY)

    @staticmethod
    def generate_refresh_token(user_id: str) -> str:
        payload = {"id": user_id}
        return jwt.encode(payload, REFRESH_TOKEN_SECRET_KEY)

    @staticmethod
    def verify_access_token(func):
        @wraps(func)
        def decorated_function():
            auth_header = request.headers.get('Authorization')

            if not auth_header:
                return {'message': 'missing_authorization_header'}, 401

            try:
                token = auth_header.split()[-1]
                data = jwt.decode(token, ACCESS_TOKEN_SECRET_KEY, algorithms=['HS256'])
                user_id = data['id']
                return func(user_id)
            except jwt.DecodeError:
                return {'message': 'invalid_access_token'}, 401
            except jwt.ExpiredSignatureError:
                return {'message': 'expired_access_token'}, 401
            except UnsupportedMediaType:
                return {"message": "invalid_body_sent"}, 400
            except Exception as e:
                Logger.error(request, e)
                return {"message": "internal_server_error"}, 500

        return decorated_function

    @staticmethod
    def verify_refresh_token():
        try:
            refresh_token = request.get_json().get('refresh_token')

            if not refresh_token:
                return {'message': 'missing_refresh_token'}, 401
            data = jwt.decode(refresh_token, REFRESH_TOKEN_SECRET_KEY, algorithms=['HS256'])
            user_id = data['id']
            return TokenHandler.generate_access_token(user_id), 200
        except jwt.DecodeError:
            return {'message': 'invalid_refresh_token'}, 401
        except jwt.ExpiredSignatureError:
            return {'message': 'expired_refresh_token'}, 401
        except UnsupportedMediaType:
            return {"message": "invalid_body_sent"}, 400
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500
