"""PonyExpress backend API application.

Args:
    app (FastAPI): The FastAPI application
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, Depends
from fastapi.responses import Response, JSONResponse
from fastapi.requests import Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from typing import Annotated

from backend.dependencies import create_db_tables, DBSession, CurrentAccount
from backend.models import Account, AccountList, Chat, ChatList, Message, MessageList, CreateChat, UpdateChat, CreateMessage, UpdateMessage, ChatMembership, Registration, AccessToken, Login, UpdateAccount
from backend.exceptions import *
from backend import auth

from backend.database.schema import DBAccount

import backend.queries as db



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_tables()
    yield


app = FastAPI(
    title = "<Chat API>",
    summary = "<This is a chat application>",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.exception_handler(ModelDNE)
def handle_modeldne(request: Request, exc: ModelDNE):
    return exc.response()

@app.exception_handler(DuplicateModel)
def handle_modeldne(request: Request, exc: DuplicateModel):
    return exc.response()

@app.exception_handler(ChatMembershipError)
def handle_modeldne(request: Request, exc: ChatMembershipError):
    return exc.response()

@app.exception_handler(ChatOwnerRemovalError)
def handle_modeldne(request: Request, exc: ChatOwnerRemovalError):
    return exc.response()

@app.exception_handler(InvalidCredentials)
def handle_modeldne(request: Request, exc: InvalidCredentials):
    return exc.response()

@app.exception_handler(AuthenticationRequiredError)
def handle_authentication_required(request: Request, exc: AuthenticationRequiredError):
    return exc.response()

@app.exception_handler(ExpiredAccessTokenError)
def handle_expired_token(request: Request, exc: ExpiredAccessTokenError):
    return exc.response()

@app.exception_handler(InvalidAccessTokenError)
def handle_invalid_token(request: Request, exc: InvalidAccessTokenError):
    return exc.response()

@app.exception_handler(AccessDeniedError)
def handle_invalid_token(request: Request, exc: AccessDeniedError):
    return exc.response()


@app.get("/status", response_model=None, status_code=204)
def status():
    pass

# -------------------------------------- Assignment 2 --------------------------------------

"""
    Route to get all the accounts in the database and the number of accounts
"""
@app.get("/accounts", response_model = AccountList)
def get_accounts(session: DBSession) -> AccountList:
    accounts = db.get_accounts(session)
    return AccountList(
        metadata = {"count": len(accounts)},
        accounts = [Account(id=acc.id, username=acc.username) for acc in accounts]
    )


"""
    Route to get current account
"""
@app.get("/accounts/me", response_model=Registration, status_code=200)
def get_current_account(account: CurrentAccount) -> Registration:
    # return account
    return Registration(id=account.id, username=account.username, email=account.email)


"""
    Route to get the account with the specified account_id 
"""
@app.get("/accounts/{account_id}", response_model=Account)
def get_account(account_id: int, session: DBSession) -> Account:
    return db.get_account(session, account_id)


"""
    Route to get all the chats in the database and the number of chats
"""
@app.get("/chats", response_model = ChatList)
def get_chats(session: DBSession) -> ChatList:
    chats = db.get_chats(session)
    return ChatList(
        metadata={"count": len(chats)},
        chats=[Chat(id = chat.id, name = chat.name, owner_id = chat.owner_id) for chat in chats]
    )


"""
    Route to get the chat with the specified chat_id 
"""
@app.get("/chats/{chat_id}", response_model = Chat)
def get_chat(chat_id: int, session: DBSession) -> Chat:
    return db.get_chat(session, chat_id)


"""
    Route to get all messages associated with the specified chat_id and the number of messages
"""
@app.get("/chats/{chat_id}/messages", response_model = MessageList)
def get_messages(chat_id: int, session: DBSession) -> MessageList:
    messages = db.get_messages(session, chat_id)
    return MessageList(
        metadata={"count": len(messages)},
        messages = [Message(id = message.id, text = message.text, account_id = message.account_id, chat_id = message.chat_id, created_at = message.created_at) for message in messages]
    )


"""
    Route to get all accounts associated with the specified chat_id and the number of accounts
"""
@app.get("/chats/{chat_id}/accounts", response_model = AccountList)
def get_chat_id_accounts(chat_id: int, session: DBSession):
    accounts = db.get_chat_id_accounts(session, chat_id)
    return AccountList(
        metadata = {"count": len(accounts)},
        accounts = [Account(id = acc.id, username = acc.username) for acc in accounts]
    )

# -------------------------------------- Assignment 3 --------------------------------------

"""
    Route to post chats
"""
@app.post("/chats", response_model = Chat, status_code = 201)
def create_chat(chat: CreateChat, current_account: CurrentAccount, session: DBSession) -> Chat:
    if chat.owner_id != current_account.id:
        raise AccessDeniedError("chat")
    return db.create_chat(session, chat.name, chat.owner_id, current_account.id)


"""
    Route to put a chat
"""
@app.put("/chats/{chat_id}", response_model = Chat, status_code = 200)
def update_chat(chat_id: int, chat: UpdateChat, session: DBSession) -> Chat:
    return db.update_chat(session, chat_id, chat.name, chat.owner_id)


"""
    Route to delete a chat
"""
@app.delete("/chats/{chat_id}", status_code = 204)
def delete_chat(chat_id: int, session: DBSession):
    db.delete_chat(session, chat_id)


"""
    Route to create a message
"""
@app.post("/chats/{chat_id}/messages", response_model=Message, status_code = 201)
def create_message(chat_id: int, message: CreateMessage, current_account: CurrentAccount, session: DBSession) -> Message:
    if message.account_id != current_account.id:
        raise AccessDeniedError("message")
    return db.create_message(session, chat_id, message.text, message.account_id)


"""
    Route to update a message
"""
@app.put("/chats/{chat_id}/messages/{message_id}", response_model=Message)
def update_message(chat_id: int, message_id: int, message: UpdateMessage, session: DBSession) -> Message:
    return db.update_message(session, chat_id, message_id, message.text)


"""
    Route to delete a message
"""
@app.delete("/chats/{chat_id}/messages/{message_id}", status_code = 204)
def delete_message(chat_id: int, message_id: int, session: DBSession):
    db.delete_message(session, chat_id, message_id)


"""
    Route to make an account a member of the specified chat
"""
@app.post("/chats/{chat_id}/accounts")
def add_account_as_chat_member(chat_id: int, membership: ChatMembership, response: Response, session: DBSession):
    chat_membership_object, new_membership_created = db.add_account_as_chat_member(session, chat_id, membership.account_id)

    # Setting the appropriate status code
    if new_membership_created:
        response.status_code = 201
    else:
        response.status_code = 200

    return {
        "chat_id": chat_id,
        "account_id": chat_membership_object.account_id,
    }


"""
    Route to delete a chat membership and all corresponding messages
"""
@app.delete("/chats/{chat_id}/accounts/{account_id}", status_code=204)
def delete_chat_membership(chat_id: int, account_id: int, session: DBSession):
    db.delete_chat_membership(session, chat_id, account_id)

# -------------------------------------- Assignment 4 --------------------------------------

"""
    Route to add an authenticated account to the database
"""
@app.post("/auth/registration", response_model=Registration, status_code=201)
def register(username: Annotated[str, Form()], email: Annotated[str, Form()], password: Annotated[str, Form()], session: DBSession):
    account = db.register_account(session, username, email, password)
    return Registration(id=account.id, username=account.username, email=account.email)


"""
    Route to get the token
"""
@app.post("/auth/token", response_model=AccessToken, status_code=200)
def get_token(form: Annotated[Login, Form()], session: DBSession):
    access_token = auth.generate_token(session, form)
    return AccessToken(access_token=access_token, token_type="bearer")


"""
    Route to login
"""
@app.post("/auth/web/login", status_code=204)
def login(response: Response, username: Annotated[str, Form()], password: Annotated[str, Form()], session: DBSession):
    form = Login(username=username, password=password)
    try:
        access_token = auth.generate_token(session, form)
        response.set_cookie(key="pony_express_token", value=access_token, httponly=True)
    except InvalidCredentials:
        raise


"""
    Route to logout
"""
@app.post("/auth/web/logout", status_code=204)
def logout(response: Response, current_account: CurrentAccount):
    response.delete_cookie(key="pony_express_token")


"""
    Route to update an existing account
"""
@app.put("/accounts/me", response_model=Registration, status_code=200)
def update_account(current_account: CurrentAccount, data: UpdateAccount, session: DBSession):
    updated_account = db.update_account(session, current_account.id, data.username, data.email)
    return Registration(id=updated_account.id, username=updated_account.username, email=updated_account.email)


"""
    Route to update a password
"""
@app.put("/accounts/me/password", status_code=204)
def update_password(
    old_password: Annotated[str, Form()],
    new_password: Annotated[str, Form()],
    current_account: CurrentAccount, 
    session: DBSession
):
    db.update_password(session, current_account.id, old_password, new_password)


"""
    Route to delete the current account
"""
@app.delete("/accounts/me", status_code=204)
def delete_account(session: DBSession, current_account: CurrentAccount):
    db.delete_account(session, current_account.id)