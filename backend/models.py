# For response models

from datetime import datetime
from pydantic import BaseModel

# -------------------------------------- Assignment 2 --------------------------------------

class Metadata(BaseModel):
    count: int

class Account(BaseModel):
    id: int
    username: str

class Chat(BaseModel):
    id: int
    name: str
    owner_id: int

class Message(BaseModel):
    id: int
    text: str
    account_id: int | None
    chat_id: int 
    created_at: datetime

class AccountList(BaseModel):
    metadata: Metadata
    accounts: list[Account]

class ChatList(BaseModel):
    metadata: Metadata
    chats: list[Chat]

class MessageList(BaseModel):
    metadata: Metadata
    messages: list[Message]

# -------------------------------------- Assignment 3 --------------------------------------

class CreateChat(BaseModel):
    name: str
    owner_id: int

class UpdateChat(BaseModel):
    name: str | None = None
    owner_id: int | None = None

class CreateMessage(BaseModel):
    text: str
    account_id: int

class UpdateMessage(BaseModel):
    text: str

class ChatMembership(BaseModel):
    account_id: int

# -------------------------------------- Assignment 4 --------------------------------------

class Registration(BaseModel):
    id: int
    username: str
    email: str

class AccessToken(BaseModel):
    access_token: str
    token_type: str

class Login(BaseModel):
    username: str
    password: str

class Claims(BaseModel):
    sub: str
    iss: str
    iat: int
    exp: int

class UpdateAccount(BaseModel):
    username: str | None = None
    email: str | None = None