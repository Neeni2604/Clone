"""Dependencies for the backend API.

Args:
    engine (sqlachemy.engine.Engine): The database engine
"""

from sqlmodel import SQLModel, create_engine, Session
from typing import Annotated
from fastapi import Depends
from fastapi.security import APIKeyCookie, HTTPBearer, HTTPAuthorizationCredentials
from backend.exceptions import AuthenticationRequiredError

from backend.database.schema import *
from backend import auth

_db_filename = "backend/database/development.db"
_db_url = f"sqlite:///{_db_filename}"
engine = create_engine(_db_url, echo=True)

bearer_scheme = HTTPBearer(auto_error=False)
cookie_scheme = APIKeyCookie(name="pony_express_token", auto_error=False)

def create_db_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

def get_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    cookie_token: str | None = Depends(cookie_scheme),
):
    if credentials:
        return credentials.credentials
    if cookie_token:
        return cookie_token
    raise AuthenticationRequiredError()
    
def get_current_account(
    session: Session = Depends(get_session),
    token: str = Depends(get_token)
):
    return auth.extract_account(session, token)

DBSession = Annotated[Session, Depends(get_session)]

CurrentAccount = Annotated[DBAccount, Depends(get_current_account)]