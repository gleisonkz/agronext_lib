from datetime import datetime, timedelta, timezone
from typing import Any, Dict
import msal
import jwt
from .auth_settings import auth_settings
from ...exceptions.auth import InvalidCredentialsError, AuthenticationError, InternalServerError
from .profiles import SystemFeature, resource_permissions, Role


