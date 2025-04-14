from jose import jwt
from datetime import datetime, timezone
from sqlmodel import Session
from backend import queries as db
from backend.models import Login, AccessToken, Claims
from backend.database.schema import DBAccount
from backend.exceptions import InvalidCredentials, AuthenticationRequiredError, ExpiredAccessTokenError, InvalidAccessTokenError
import os

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", default="default")
JWT_ALGORITHM = "HS256"
DURATION = 3600
JWT_ISSUER = "http://127.0.0.1"

def generate_token(session: Session, form: Login) -> str:
    account = db.get_account_by_username(session, form.username)
    account = validate_credentials(account, form.password)
    claims = generate_claims(account)
    return jwt.encode(claims.model_dump(), JWT_SECRET_KEY, algorithm=JWT_ALGORITHM,)

def generate_claims(account: DBAccount) -> Claims:
    iat = int(datetime.now(timezone.utc).timestamp())
    exp = iat + DURATION
    return Claims(sub=str(account.id), iss=JWT_ISSUER, iat=iat, exp=exp)

def validate_credentials(account: DBAccount | None, password: str,) -> DBAccount:
    if account is None or not db.verify_password(password, account.hashed_password):
        raise InvalidCredentials()
    return account

def extract_account(session: Session, token: str) -> DBAccount:
    try:
        payload = jwt.get_unverified_claims(token)
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        claims = Claims(**payload)
        
        return db.get_account(session, int(claims.sub))
    except jwt.ExpiredSignatureError:
        raise ExpiredAccessTokenError()
    except Exception:
        raise InvalidAccessTokenError()