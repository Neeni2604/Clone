# For database query functions

from backend.exceptions import *
from sqlmodel import Session, select
from backend.database.schema import DBAccount, DBChat, DBMessage, DBChatMembership
from backend.models import Account, AccountList, Chat, Message, MessageList
# from backend.dependencies import engine
import bcrypt

# -------------------------------------- Assignment 2 --------------------------------------

"""
    Getting all accounts in the database
"""
def get_accounts(session: Session) -> list[Account]:
    stmt = select(DBAccount).order_by(DBAccount.id)
    results = session.exec(stmt)
    return list(results)
    

"""
    Getting all accounts associated with account_id
"""
def get_account(session: Session, account_id: int) -> Account:
    account = account_exists(session, account_id)
    return account


"""
    (Assignment 4) Getting account by username
"""
def get_account_by_username(session: Session, username: str) -> DBAccount | None:
    stmt= select(DBAccount).where(DBAccount.username == username)
    account = session.exec(stmt).first()
    return account


"""
    Getting all chats in the database
"""
def get_chats(session: Session) -> list[Chat]:
    stmt = select(DBChat).order_by(DBChat.id)
    results = session.exec(stmt)
    return list(results)


"""
    Getting all chats associated with chat_id
"""
def get_chat(session: Session, chat_id: int) -> Chat:
    chat = chat_exists(session, chat_id)
    return chat


"""
    Getting all messages associated with chat_id
"""
def get_messages(session: Session, chat_id: int) -> list[Message]:
    chat = chat_exists(session, chat_id)
    stmt = select(DBMessage).where(DBMessage.chat_id == chat_id).order_by(DBMessage.id)
    results = session.exec(stmt)
    return list(results)


"""
    Getting all accounts associated with chat_id in the chat_memberships table
"""
def get_chat_id_accounts(session: Session, chat_id: int) -> list[Account]:
    chat = chat_exists(session, chat_id)
    stmt = (
        select(DBAccount)
        .join(DBChatMembership, DBAccount.id == DBChatMembership.account_id)
        .where(DBChatMembership.chat_id == chat_id)
        .order_by(DBAccount.id)
    )
    results = session.exec(stmt)
    return list(results)

# -------------------------------------- Assignment 3 --------------------------------------

"""
    Creating a new chat
"""
def create_chat(session: Session, chat_name: str, chat_owner_id: int, current_account_id: int):
    # Does owner exist?
    owner = account_exists(session, chat_owner_id)
    
    # Is the name taken?
    check_duplicate_chat_name(session, chat_name)
    
    # Add chat to the database
    new_chat = DBChat(name=chat_name, owner_id=chat_owner_id)
    session.add(new_chat)
    session.commit()
    session.refresh(new_chat)

    # Add chat membership to database
    chat_membership = DBChatMembership(account_id=chat_owner_id, chat_id=new_chat.id)
    session.add(chat_membership)
    session.commit()

    return new_chat


"""
    Updating an existing chat
"""
def update_chat(session: Session, chat_id: int, chat_name: str | None = None, chat_owner_id: int | None = None):
    # Does chat_id correspond to a chat in the database?
    chat = chat_exists(session, chat_id)
    
    # Is the name taken?
    if chat_name is not None:
        check_duplicate_chat_name(session, chat_name)
        chat.name = chat_name
    
    # Does owner exist in the chat membership?
    if chat_owner_id is not None:
        owner_exists_in_membership(session, chat_id, chat_owner_id)
        chat.owner_id = chat_owner_id

    session.add(chat)
    session.commit()
    session.refresh(chat)
    return chat


"""
    Deleting an existing chat
"""
def delete_chat(session: Session, chat_id: int):
    # Does chat_id correspond to a chat in the database?
    chat = chat_exists(session, chat_id)
    
    session.delete(chat)
    session.commit()


"""
    Creating a new message
"""
def create_message(session: Session, chat_id: int, message_text: str, message_account_id: int) -> DBMessage:
    # Does chat_id correspond to a chat in the database?
    chat = chat_exists(session, chat_id)
    
    account_in_chat_membership(session, chat_id, message_account_id)
    
    message = DBMessage(text=message_text, account_id=message_account_id, chat_id=chat_id)
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


"""
    Updating an existing message
"""
def update_message(session: Session, chat_id: int, message_id: int, message_text: str):
    # Does chat_id correspond to a chat in the database?
    chat = chat_exists(session, chat_id)
    
    # Does message_id correspond to a message in the database or to a different chat_id?
    message = verify_message(session, chat_id, message_id)
    
    message.text = message_text
    session.commit()
    session.refresh(message)
    return message


"""
    Deleting an existing message
"""
def delete_message(session: Session, chat_id: int, message_id: int):
    # Does chat_id correspond to a chat in the database?
    chat = chat_exists(session, chat_id)
    
    # Does message_id correspond to a message in the database or to a different chat_id?
    message = verify_message(session, chat_id, message_id)
    
    session.delete(message)
    session.commit()


"""
    Adding an account as a chat member
"""
def add_account_as_chat_member(session: Session, chat_id: int, account_id):
    # Does chat_id correspond to a chat in the database?
    chat = chat_exists(session, chat_id)
    
    # Does account_id correspond to an account in the database?
    account = account_exists(session, account_id)
      
    # Is the account already a member of the chat?
    try:
        current_account = account_in_chat_membership(session, chat_id, account_id)
        if current_account is not None:
            return current_account, False
    except(ChatMembershipError):
        # Create new membership if it doesn't already exist
        membership = DBChatMembership(account_id = account_id, chat_id = chat_id)
        session.add(membership)
        session.commit()
        session.refresh(membership)
        return membership, True


"""
    Deleting a chat membership between a chat and an account
"""
def delete_chat_membership(session: Session, chat_id: int, account_id: int):
    # Does chat_id correspond to a chat in the database?
    chat = chat_exists(session, chat_id)
    
    # Does account_id correspond to an account in the database?
    membership = account_in_chat_membership(session, chat_id, account_id)
    
    # Is the account the owner of the chat?
    is_account_chat_owner(session, chat, account_id)
    
    # Deleting messages corresponding to the account
    delete_all_messages(session, chat_id, account_id)
    
    # Deleting the chat membership
    session.delete(membership)
    session.commit()

# -------------------------------------- Assignment 4 --------------------------------------

"""
    Adding a new authenticated account
"""
def register_account(session: Session, username: str, email: str, password: str):
    # Check if the account with username already exists
    stmt = select(DBAccount).where(DBAccount.username == username)
    existing_account = session.exec(stmt).first()
    if existing_account:
        raise DuplicateModel(model_name="account", field="username", value=username)
    
    # Check if there is an account that exists with the email
    stmt = select(DBAccount).where(DBAccount.email == email)
    existing_account = session.exec(stmt).first()
    if existing_account:
        raise DuplicateModel(model_name="account", field="email", value=email)
    
    # Hashing the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(encoding="utf-8"), salt).decode(encoding="utf-8")
    
    # Creating and adding the new account
    new_account = DBAccount(username=username, email=email, hashed_password=hashed_password)
    session.add(new_account)
    session.commit()
    session.refresh(new_account)
    
    return new_account


"""
    Getting an account by its username and password
"""
def get_verified_user(session: Session, username: str, password: str):
    stmt = select(DBAccount).where(DBAccount.username == username)
    account = session.exec(stmt).one_or_none()
    if account is not None and verify_password(password, account.hashed_password):
        return account
    raise InvalidCredentials()


"""
    Updating the username or email of an account
"""
def update_account(session: Session, id: int, username: str = None, email: str = None):
    account = account_exists(session, id)

    # Checking if the username is not none and the new username is not the same as the current username
    if username is not None and username != account.username:
        # Checking if the username is already associated with an account
        stmt = select(DBAccount).where(DBAccount.username == username)
        existing = session.exec(stmt).first()
        if existing and existing.id != id:
            raise DuplicateModel(model_name="account", field="username", value=username)
        account.username = username
    
    # Checking if email is not None and the new email is not the same as the current email
    if email is not None and email != account.email:
        # Check if the email is already associated with an account
        stmt = select(DBAccount).where(DBAccount.email == email)
        existing = session.exec(stmt).first()
        if existing and existing.id != id:
            raise DuplicateModel(model_name="account", field="email", value=email)
        account.email = email
    
    session.add(account)
    session.commit()
    session.refresh(account)

    return account


"""
    Updating the password of an account
"""
def update_password(session: Session, id: int, old_pwd: str, new_pwd: str):
    account = account_exists(session, id)

    if not verify_password(old_pwd, account.hashed_password):
        raise InvalidCredentials()
    else:
        account.hashed_password = hash_password(new_pwd)
    session.add(account)
    session.commit()


"""
    Deleting the current account
"""
def delete_account(session: Session, id: int):
    account = account_exists(session, id)

    stmt = select(DBChat).where(DBChat.owner_id == id)
    chats = session.exec(stmt).first()

    if chats:
        raise ChatOwnerRemovalError()
    else:
        session.delete(account)
        session.commit()


# ------------------------------------ Helper Functions ------------------------------------


"""
    If chat with chat_id doesn't exist, raise ModelDNE exception
"""
def chat_exists(session: Session, chat_id: int):
    chat = session.get(DBChat, chat_id)
    if chat is None:
        raise ModelDNE(model_name="chat", model_id=chat_id)
    return chat


"""
    If account with account_id doesn't exist, raise ModelDNE exception
"""
def account_exists(session: Session, account_id: int):

    account = session.get(DBAccount, account_id)
    if account is None:
        raise ModelDNE(model_name="account", model_id=account_id)
    return account


"""
    Checking if an account is a member of the chat
"""
def account_in_chat_membership(session, chat_id, account_id):
    account = session.get(DBAccount, account_id)
    stmt = (
        select(DBChatMembership)
        .where(DBChatMembership.account_id == account_id)
        .where(DBChatMembership.chat_id == chat_id)
    )
    membership = session.exec(stmt).first()

    if membership is None or account is None:
        raise ChatMembershipError(account_id = account_id, chat_id = chat_id)
    else:
        return membership


"""
    Checking if a name already exists
"""
def check_duplicate_chat_name(session: Session, name: str):
    stmt = (select(DBChat).where(DBChat.name == name))
    chat = session.exec(stmt).first()
    if chat is not None:
        raise DuplicateModel(model_name="chat", field="name", value=name)
    

"""
    Checking if the owner exists in the chat membership
"""
def owner_exists_in_membership(session: Session, chat_id, chat_owner_id):
    # Check if account exists (ChatMembershipError)
    account_in_chat_membership(session, chat_id, chat_owner_id)
    
    # If account exists, check if it is a member of the chat
    stmt = (
        select(DBChatMembership)
        .where(DBChatMembership.account_id == chat_owner_id)
        .where(DBChatMembership.chat_id == chat_id)
    )
    membership = session.exec(stmt).first()
    if membership is None:
        raise ChatMembershipError(account_id=chat_owner_id, chat_id=chat_id)


"""
    Checking if a message exists in the database
"""
def verify_message(session: Session, chat_id: int, message_id: int):
    message = session.get(DBMessage, message_id)
    if message is None or message.chat_id != chat_id:
        raise ModelDNE(model_name="message", model_id=message_id)
    return message


"""
    Checking if an account is the owner of the chat
"""
def is_account_chat_owner(session: Session, chat: DBChat, account_id: int):
    if account_id == chat.owner_id:
        raise ChatOwnerRemovalError()


"""
    Deleting all messages associated with a chat membership
"""
def delete_all_messages(session: Session, chat_id: int, account_id: int):
    stmt = (
        select(DBMessage)
        .where(DBMessage.chat_id == chat_id)
        .where(DBMessage.account_id == account_id)
    )
    messages = session.exec(stmt).all()
    for message in messages:
        message.account_id = None


"""
    Using bcrypt to hash a password
"""
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


"""
    Using bcrypt to verify the password
"""
def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))