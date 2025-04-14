import pytest
from backend.database.schema import *
from datetime import datetime, timezone, timedelta
from jose import jwt
import os
from backend.auth import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ISSUER
import bcrypt

# ------------------------------------ Helper Functions ------------------------------------

"""
    Helper function to generate auth token for tests
"""
def create_test_token(account_id: int):
    iat = int(datetime.now(timezone.utc).timestamp())
    payload = {
        "sub": str(account_id),
        "iss": "http://127.0.0.1",
        "iat": iat,
        "exp": iat + 3600
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

"""
    Add auth headers to requests
"""
def auth_headers(account_id: int):
    token = create_test_token(account_id)
    return {"Authorization": f"Bearer {token}"}

# -------------------------------------------------------------------------------------------

"""
    Setting up the test database
"""
@pytest.fixture
def setup_db(session):
    account1 = DBAccount(id = 1, username = "a", email = "a", hashed_password = "a")
    account2 = DBAccount(id = 2, username = "b", email = "b", hashed_password = "b")
    account3 = DBAccount(id = 3, username = "c", email = "c", hashed_password = "c")
    chat1 = DBChat(id = 1, name = "chat1", owner_id = 1)
    chat2 = DBChat(id = 2, name = "chat2", owner_id = 2)
    chat3 = DBChat(id = 3, name = "chat3", owner_id = 1)
    msg1 = DBMessage(id = 1, text = "Hello", account_id = 1, chat_id = 1, created_at = datetime(2020, 5, 17))
    msg2 = DBMessage(id = 2, text = "Hey", account_id = 2, chat_id = 1, created_at = datetime(2020, 5, 17))
    msg3 = DBMessage(id = 3, text = "Heya", account_id = 1, chat_id = 2, created_at = datetime(2020, 5, 17))
    chatmem1 = DBChatMembership(account_id = 1, chat_id = 1)
    chatmem2 = DBChatMembership(account_id = 2, chat_id = 1)
    chatmem3 = DBChatMembership(account_id = 1, chat_id = 3)
    session.add(account1)
    session.add(account2)
    session.add(account3)
    session.add(chat1)
    session.add(chat2)
    session.add(chat3)
    session.add(msg1)
    session.add(msg2)
    session.add(msg3)
    session.add(chatmem1)
    session.add(chatmem2)
    session.add(chatmem3)
    session.commit()


def test_status(client):
    response = client.get("/status")
    assert response.status_code == 204


"""
    Test to get all accounts in the test database and the number of accounts
"""
def test_get_accounts(setup_db, client):
    response = client.get("/accounts")
    assert response.status_code == 200
    assert response.json() == {
        "metadata": {"count": 3},
        "accounts": [
            {"id":1, "username":"a"},
            {"id":2, "username":"b"},
            {"id":3, "username":"c"}
        ]
    }


"""
    Test to get account with account_id = 1 from the test database
"""
def test_get_account1(setup_db, client):
    response = client.get("/accounts/1")
    assert response.status_code == 200
    assert response.json() == {"id":1, "username":"a"}


"""
    Test to get an account with an account_id that doesn't exist in the test database
"""
def test_get_account_dne(setup_db, client):
    response = client.get("/accounts/100")
    assert response.status_code == 404
    assert response.json() == {
        "error":"entity_not_found", 
        "message":"Unable to find account with id=100",
    }


"""
    Test to get all the chats in the test database and the number of chats
"""
def test_get_chats(setup_db, client):
    response = client.get("/chats")
    assert response.status_code == 200
    assert response.json() == {
        "metadata": {"count": 3},
        "chats": [
            {"id":1, "name":"chat1", "owner_id":1},
            {"id":2, "name":"chat2", "owner_id":2},
            {"id":3, "name":"chat3", "owner_id":1},
        ]
    }


"""
    Test to get chat with chat_id = 1 from the test database
"""
def test_get_chat1(setup_db, client):
    response = client.get("/chats/3")
    assert response.status_code == 200
    assert response.json() == {"id":3, "name":"chat3", "owner_id":1}


"""
    Test to get a chat with a chat_id that doesn't exist in the test database
"""
def test_get_chat_dne(setup_db, client):
    response = client.get("/chats/100")
    assert response.status_code == 404
    assert response.json() == {
        "error":"entity_not_found", 
        "message":"Unable to find chat with id=100",
    }


"""
    Test to get all messages associated with chat_id = 1 from the test database
"""
def test_get_messages_1(setup_db , client):
    response = client.get("/chats/1/messages")
    assert response.status_code == 200
    assert response.json() == {
        "metadata": {"count": 2},
        "messages": [
            {"id":1, "text":"Hello", "account_id":1, "chat_id":1, "created_at":"2020-05-17T00:00:00"},
            {"id":2, "text":"Hey", "account_id":2, "chat_id":1, "created_at":"2020-05-17T00:00:00"},
        ]
    }

"""
    Test to get all messages associated with chat_id = 3 from the test database
"""
def test_get_messages_3(setup_db , client):
    response = client.get("/chats/3/messages")
    assert response.status_code == 200
    assert response.json() == {
        "metadata": {"count": 0},
        "messages": [
        ]
    }


"""
    Test to return an error when trying to get all messages associated with a chat_id that
    doesn't exist in the test database
"""
def test_get_messages_dne(setup_db , client):
    response = client.get("/chats/100/messages")
    assert response.status_code == 404
    assert response.json() == {
        "error":"entity_not_found", 
        "message":"Unable to find chat with id=100",
    }


"""
    Test to get all accounts associated with chat_id = 1 in the chat_memberships table
"""
def test_get_chat_id_accounts_1(setup_db , client):
    response = client.get("/chats/1/accounts")
    assert response.status_code == 200
    assert response.json() == {
        "metadata": {"count": 2},
        "accounts": [
            {"id":1, "username":"a"},
            {"id":2, "username":"b"},
        ]
    }


"""
    Test to get all accounts associated with chat_id = 2 in the chat_memberships table
"""
def test_get_chat_id_accounts_2(setup_db , client):
    response = client.get("/chats/2/accounts")
    assert response.status_code == 200
    assert response.json() == {
        "metadata": {"count": 0},
        "accounts": []
    }


"""
    Test to get all acounts with a chat_id that doesn't exist in the chat_memberships table
"""
def test_get_chat_id_accounts_dne(setup_db , client):
    response = client.get("/chats/100/accounts")
    assert response.status_code == 404
    assert response.json() == {
        "error":"entity_not_found", 
        "message":"Unable to find chat with id=100",
    }

# --------------------------------- Assignment 3 Tests --------------------------------------

"""
    Test to create a chat (no exceptions thrown)
"""
def test_create_chat(setup_db, client):
    request_data = {"name": "This is a new chat", "owner_id": 1}
    headers = auth_headers(1)  # Authenticated as account 1
    response = client.post("/chats", json=request_data, headers=headers)
    assert response.status_code == 201
    assert response.json() == {"id": 4, "name": "This is a new chat", "owner_id": 1}



"""
    Test to create a chat with an owner_id that doesn't correspond to an account in the 
    database but with an unauthenticated account (InvalidAccessToken exception thrown)
"""
def test_create_chat_invalid_access_token(setup_db, client):
    headers = {"Authorization": f"Bearer invalid"}
    request_data = {"name": "This is a new chat", "owner_id": 1}
    response = client.post("/chats", json=request_data, headers=headers)
    
    assert response.status_code == 403
    assert response.json() == {
        "error": "invalid_access_token",
        "message": "Authentication failed: invalid access token"
    }


"""
    Test to create a chat with a name that already exists (DuplicateChat exception thrown)
"""
def test_create_chat_duplicate_chat(setup_db, client):
    headers = auth_headers(1)
    request_data = {"name": "chat1", "owner_id": 1}
    response = client.post("/chats", json=request_data, headers=headers)
    
    assert response.status_code == 422
    assert response.json() == {
        "error": "duplicate_entity_value",
        "message": "Duplicate value: chat with name=chat1 already exists"
    }


"""
    Test to update a chat (no exceptions thrown)
"""
def test_update_chat(setup_db, client):
    request_data = {"name": "This is the updated chat name", "owner_id": 2}
    response = client.put("/chats/1", json=request_data)
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "This is the updated chat name", "owner_id": 2}


"""
    Test to update a chat when the chat_id doesn't correspond to a chat in the database
    (ModelDNE exeption thrown)
"""
def test_update_chat_model_dne(setup_db, client):
    request_data = {"name": "This is the updated chat name", "owner_id": 1}
    response = client.put("/chats/999", json=request_data)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=999"
    }


"""
    Test to update the chat when the name is already taken by a different chat
    (DuplicateChat exception thrown)
"""
def test_update_chat_duplicate_chat(setup_db, client):
    request_data = {"name": "chat2"} 
    response = client.put("/chats/1", json=request_data)
    assert response.status_code == 422
    assert response.json() == {
        "error": "duplicate_entity_value",
        "message": "Duplicate value: chat with name=chat2 already exists"
    }


"""
    Test to update the chat if the owner_id doesn't correspond to a chat in the database
    (ChatMembershipError exception thrown)
"""
def test_update_chat_owner_dne(setup_db, client):
    request_data = {"owner_id": 999}
    response = client.put("/chats/1", json=request_data)
    assert response.status_code == 422
    assert response.json() == {
        "error": "chat_membership_required",
        "message": "Account with id=999 must be a member of chat with id=1"
    }


"""
    Test to update the chat if the owner_id corresponds to an account that isn't a part of 
    the chat membership (ChatMembershipError exception thrown)
"""
def test_update_chat_owner_not_member_of_chat(setup_db, client):
    request_data = {"owner_id": 3}  # Account 3 exists but isn't a member of chat 1
    response = client.put("/chats/1", json=request_data)
    assert response.status_code == 422
    assert response.json() == {
        "error": "chat_membership_required",
        "message": "Account with id=3 must be a member of chat with id=1"
    }


"""
    Test to delete a chat from the database (no exceptions thrown)
"""
def test_delete_chat(setup_db, client):
    response = client.delete("/chats/1")
    assert response.status_code == 204
    
    # Verifying that the chat no longer exists in the database
    response = client.get("/chats/1")
    assert response.status_code == 404


"""
    Test to delete a chat when the chat_id doesn't correspond to a chat in the database
    (ModelDNE exception thrown)
"""
def test_delete_chat_dne(setup_db, client):
    response = client.delete("/chats/999")
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=999"
    }


"""
    Test to create a message (no exceptions thrown)
"""
def test_create_message(setup_db, client):
    headers = auth_headers(1)
    request_data = {"text": "This is a new message", "account_id": 1}
    response = client.post("/chats/1/messages", json=request_data, headers=headers)
    
    assert response.status_code == 201

    # Verifying each part of the new message individually because we cannot verify the 
    # "created_at" field in a test database
    data = response.json()
    assert data["account_id"] == 1
    assert data["chat_id"] == 1
    assert data["id"] == 4  # Assuming 3 messages already exist in setup_db
    assert data["text"] == "This is a new message"


"""
    Test to create a message when the chat_id doesn't correspond to a chat in the database
    (ModelDNE exception thrown)
"""
def test_create_message_chat_dne(setup_db, client):
    headers = auth_headers(1)
    request_data = {"text": "This is a new message", "account_id": 1}
    response = client.post("/chats/999/messages", json=request_data, headers=headers)
    
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=999"
    }


"""
    Test to create a message when the account_id doesn't correspond to an account in the 
    database (AccessDeniedError exception thrown)
"""
def test_create_message_account_dne(setup_db, client):
    headers = auth_headers(1)
    request_data = {"text": "This is a new message", "account_id": 999}
    response = client.post("/chats/1/messages", json=request_data, headers=headers)
    
    # account_id != authenticated account's id
    # AccessDeniedError exception raised
    assert response.status_code == 403
    assert response.json() == {
        "error": "access_denied",
        "message": "Cannot create message on behalf of different account"
    }


"""
    Test to create a message when the account_id corresponds to an account that doesn't 
    belong to the chat membership (ChatMembershipError exception thrown)
"""
def test_create_message_account_not_member(setup_db, client):
    headers = auth_headers(3)
    request_data = {"text": "This is a new message", "account_id": 3}
    response = client.post("/chats/1/messages", json=request_data, headers=headers)
    
    # After passing access_denied check, ChatMembershipError will be thrown
    assert response.status_code == 422
    assert response.json() == {
        "error": "chat_membership_required",
        "message": "Account with id=3 must be a member of chat with id=1"
    }


"""
    Test to create a message from a different account (AccessDeniedError exception thrown)
"""
def test_create_message_different_account(setup_db, client):
    headers = auth_headers(1)
    # Try to create a message on behalf of account 2 when authenticated as account 1
    request_data = {"text": "This is a new message", "account_id": 2}
    response = client.post("/chats/1/messages", json=request_data, headers=headers)
    
    assert response.status_code == 403
    assert response.json() == {
        "error": "access_denied",
        "message": "Cannot create message on behalf of different account"
    }


"""
    Test to update a message's text (no exceptions thrown)
"""
def test_update_message(setup_db, client):
    request_data = {"text": "I updated the message's text"}
    response = client.put("/chats/1/messages/1", json=request_data)
    assert response.status_code == 200
    assert response.json()["text"] == "I updated the message's text"


"""
    Test to update a message's text when the chat_id doesn't correspond to a chat in the
    database (ModelDNE exception thrown)
"""
def test_update_message_chat_dne(setup_db, client):
    request_data = {"text": "I updated the message's text"}
    response = client.put("/chats/999/messages/1", json=request_data)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=999"
    }


"""
    Test to update a message's text when the message_id doesn't correspond to a message in
    the database (ChatMembershipError exception thrown)
"""
def test_update_message_dne(setup_db, client):
    request_data = {"text": "I updated the message's text"}
    response = client.put("/chats/1/messages/999", json=request_data)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find message with id=999"
    }


"""
    Test to update a message's text when the message_id corresponds to a message that belongs
    to a different chat (ChatMembershipError exception thrown)
"""
def test_update_message_different_chat(setup_db, client):
    request_data = {"text": "I updated the message's text"}
    response = client.put("/chats/1/messages/3", json=request_data)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find message with id=3"
    }


"""
    Test to delete a message from the database (no exceptions thrown)
"""
def test_delete_message(setup_db, client):
    response = client.delete("/chats/1/messages/1")
    assert response.status_code == 204

    # Verifying that the message no longer exists in the database
    messages_response = client.get("/chats/1/messages")
    assert len(messages_response.json()["messages"]) == 1


"""
    Test to delete a message from the database when the chat_id doesn't correspond to a chat
    in the database (ModelDNE exception thrown)
"""
def test_delete_message_chat_dne(setup_db, client):
    response = client.delete("/chats/999/messages/1")
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=999"
    }


"""
    Test to delete a message from the database when the message_id doesn't correspond to a 
    message in the database (ChatMembershipError exception thrown)
"""
def test_delete_message_dne(setup_db, client):
    response = client.delete("/chats/1/messages/999")
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find message with id=999"
    }


"""
    Test to delete a message from the database when the message_id corresponds to a message 
    that belongs to a different chat (ChatMembershipError exception thrown)
"""
def test_delete_message_different_chat(setup_db, client):
    response = client.delete("/chats/1/messages/3")
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find message with id=3"
    }


"""
    Test to add a chat membership that already exists (no exceptions, status code = 200)
"""
def test_add_chat_membership_that_already_exists(setup_db, client):
    request_data = {"account_id": 1}
    response = client.post("/chats/1/accounts", json=request_data)
    assert response.status_code == 200
    assert response.json() == {
        "chat_id": 1,
        "account_id": 1
    }


"""
    Test to add a chat membership that doesn't already exist (no exceptions, status code = 201)
"""
def test_add_chat_membership_that_does_not_already_exist(setup_db, client):
    request_data = {"account_id": 3}
    response = client.post("/chats/1/accounts", json=request_data)
    assert response.status_code == 201
    assert response.json() == {
        "chat_id": 1,
        "account_id": 3
    }


"""
    Test to add a chat membership when the chat_id doesn't correpsond to a chat in the 
    database (ModelDNE exception thrown)
"""
def test_add_chat_membership_chat_dne(setup_db, client):
    request_data = {"account_id": 1}
    response = client.post("/chats/999/accounts", json=request_data)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=999"
    }


"""
    Test to add a chat membership when the account_id doesn't correspond to a chat in the 
    database (ModelDNE exception thrown)
"""
def test_add_chat_membership_account_dne(setup_db, client):
    request_data = {"account_id": 999}
    response = client.post("/chats/1/accounts", json=request_data)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find account with id=999"
    }


"""
    Test to delete a chat membership and all the corresponding messages (no exceptions thrown)
"""
def test_delete_chat_membership(setup_db, client):
    response = client.delete("/chats/1/accounts/2")
    assert response.status_code == 204

    # Verifying that the account is no longer a member of the chat
    members_response = client.get("/chats/1/accounts")
    members = members_response.json()["accounts"]
    assert len(members) == 1
    assert members[0]["id"] == 1


"""
    Test to delete a chat membership and all the corresponding messages when the chat_id 
    doesn't correspond to a chat in the database (ModelDNE exception thrown)
"""
def test_delete_chat_membership_chat_dne(setup_db, client):
    response = client.delete("/chats/999/accounts/1")
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=999"
    }


"""
    Test to delete a chat membership and all the corresponding messages when the account_id 
    doesn't correspond to an account in the database (ChatMembershipError exception thrown)
"""
def test_delete_chat_membership_account_dne(setup_db, client):
    response = client.delete("/chats/1/accounts/999")
    assert response.status_code == 422
    assert response.json() == {
        "error": "chat_membership_required",
        "message": "Account with id=999 must be a member of chat with id=1"
    }


"""
    Test to delete a chat membership and all the corresponding messages when the account_id 
    corresponds to an account that is not a member of the chat (ChatMembershipError exception
    thrown)
"""
def test_delete_chat_membership_account_not_in_membership(setup_db, client):
    response = client.delete("/chats/1/accounts/3")
    assert response.status_code == 422
    assert response.json() == {
        "error": "chat_membership_required",
        "message": "Account with id=3 must be a member of chat with id=1"
    }


"""
    Test to delete a chat membership and all the corresponding messages when the account_id
    is the owner of the chat (ChatOwnerRemovalError exception thrown)
"""
def test_delete_chat_membership_account_is_owner(setup_db, client):
    response = client.delete("/chats/1/accounts/1")
    assert response.status_code == 422
    assert response.json() == {
        "error": "chat_owner_removal",
        "message": "Unable to remove the owner of a chat"
    }


"""
    Test to add an authenticated account to the database (no exceptions raised)
"""
def test_add_authenticated_account(setup_db, client):
    request_data = {"username": "newuser", "email": "newuser@example.com", "password": "password123"}
    response = client.post("/auth/registration", data=request_data)
    
    assert response.status_code == 201
    assert response.json() == {
        "id": 4,  # Assuming 3 accounts already exist
        "username": "newuser",
        "email": "newuser@example.com"
    }
    
    # Verify the account was created
    get_response = client.get("/accounts/4")
    assert get_response.status_code == 200
    assert get_response.json()["username"] == "newuser"


"""
    Test to add an authenticated account to the database with a username that already exists
    (DuplicateModel exception raised)
"""
def test_add_authenticated_account_duplicate_username(setup_db, client):
    request_data = {"username": "a", "email": "a@gmail.com", "password": "a"}
    response = client.post("/auth/registration", data=request_data)
    
    assert response.status_code == 422
    assert response.json() == {
        "error": "duplicate_entity_value",
        "message": "Duplicate value: account with username=a already exists"
    }


"""
    Test to add an authenticated account to the database with an email that already exists
    (DuplicateModel exception raised)
"""
def test_register_duplicate_email(setup_db, client):
    request_data = {"username": "uniqueuser", "email": "a", "password": "password123"}
    response = client.post("/auth/registration", data=request_data)
    
    assert response.status_code == 422
    assert response.json() == {
        "error": "duplicate_entity_value",
        "message": "Duplicate value: account with email=a already exists"
    }


"""
    Test to generate the access token (no exceptions raised)
"""
def test_get_token(setup_db, client, session): 
    # Get the account and update its password with a proper bcrypt hash
    account = session.get(DBAccount, 1)
    password = "testpassword"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    
    # Update the account with the proper hashed password
    account.hashed_password = hashed_password
    session.add(account)
    session.commit()
    
    # Now test getting a token with the correct password
    request_data = {"username": "a", "password": password}
    response = client.post("/auth/token", data=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Verify token works by using it to access protected route
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    me_response = client.get("/accounts/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["id"] == 1


"""
    Test to generate the access token with a username that doesn't correspond to an account
    in the database (InvalidCredentials exception thrown)
"""
def test_get_token_invalid_username(setup_db, client):
    request_data = {"username": "nonexistent_user", "password": "password"}
    response = client.post("/auth/token", data=request_data)
    
    assert response.status_code == 401
    assert response.json() == {
        "error": "invalid_credentials",
        "message": "Authentication failed: invalid username or password"
    }


"""
    Test to generate an access token for the account that's currently stored in the cookie
    (no exceptions raised)
"""
def test_login_with_cookie(setup_db, client, session):
    account = session.get(DBAccount, 1)
    password = "testpassword"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    
    account.hashed_password = hashed_password
    session.add(account)
    session.commit()
    
    # Login to get the cookie
    request_data = {"username": "a", "password": password}
    response = client.post("/auth/web/login", data=request_data)
    
    assert response.status_code == 204
    assert "pony_express_token" in response.cookies
    
    # Test accessing a protected route with the cookie
    me_response = client.get("/accounts/me")
    assert me_response.status_code == 200
    assert me_response.json()["id"] == 1


"""
    Test to generate an access token for the account that's currently stored in the cookie 
    when the username doesn't correspond to an account in the dataabse (Invalid Credentials
    exception is raised)
"""
def test_login_with_invalid_credentials(setup_db, client):
    request_data = {"username": "nonexistent_user", "password": "password"}
    response = client.post("/auth/web/login", data=request_data)
    
    assert response.status_code == 401
    assert response.json() == {
        "error": "invalid_credentials",
        "message": "Authentication failed: invalid username or password"
    }
    assert "pony_express_token" not in response.cookies


"""
    Test to logout an account that is logged in (no exceptions raised)
"""
def test_logout(setup_db, client, session):
    account = session.get(DBAccount, 1)
    password = "testpassword"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    
    account.hashed_password = hashed_password
    session.add(account)
    session.commit()
    
    # Login to get the cookie
    login_response = client.post("/auth/web/login", data={"username": "a", "password": password})
    assert login_response.status_code == 204
    assert "pony_express_token" in login_response.cookies
    
    # Test the logout
    headers = auth_headers(1)  # We need to include auth headers for the logout endpoint
    response = client.post("/auth/web/logout", headers=headers)
    
    assert response.status_code == 204
    
    # When a cookie is cleared, its value might not be directly accessible in the response
    # Instead, verify that after logout, protected endpoints are no longer accessible
    me_response = client.get("/accounts/me")
    assert me_response.status_code == 403
    assert me_response.json() == {
        "error": "authentication_required",
        "message": "Not authenticated"
    }


"""
    Test to update the authenticated account if the username and email in the request body
    aren't None (no exceptions thrown)
"""
def test_update_account_both_fields(setup_db, client):
    headers = auth_headers(1)
    request_data = {"username": "updated_username", "email": "updated_email@example.com"}
    response = client.put("/accounts/me", json=request_data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "updated_username"
    assert data["email"] == "updated_email@example.com"


"""
    Test to update the authenticated account if the username is None and email is not None
    in the request body (no exceptions thrown)
"""
def test_update_account_email_only(setup_db, client):
    headers = auth_headers(1)
    request_data = {"email": "new_email@example.com"}
    response = client.put("/accounts/me", json=request_data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "a"  # Should not be changed
    assert data["email"] == "new_email@example.com"


"""
    Test to update the authenticated account if the username is not None and email is None
    in the request body (no exceptions thrown)
"""
def test_update_account_username_only(setup_db, client):
    headers = auth_headers(1)
    request_data = {"username": "new_username"}
    response = client.put("/accounts/me", json=request_data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "new_username"
    assert data["email"] == "a"  # Should not be changed


"""
    Test to update the authenticated account if the username and email in the request body
    aren't None and the username already exists in the database (DuplicateModel exception 
    thrown)
"""
def test_update_account_duplicate_username(setup_db, client):
    headers = auth_headers(1)
    request_data = {"username": "b"}  # "b" is already taken by account with id=2
    response = client.put("/accounts/me", json=request_data, headers=headers)
    
    assert response.status_code == 422
    assert response.json() == {
        "error": "duplicate_entity_value",
        "message": "Duplicate value: account with username=b already exists"
    }


"""
    Test to update the authenticated account if the username and email in the request body
    aren't None and the email already exists in the database (DuplicateModel exception 
    thrown)
"""
def test_update_account_duplicate_email(setup_db, client):
    headers = auth_headers(1)
    request_data = {"email": "b"}  # "b" is already taken by account with id=2
    response = client.put("/accounts/me", json=request_data, headers=headers)
    
    assert response.status_code == 422
    assert response.json() == {
        "error": "duplicate_entity_value",
        "message": "Duplicate value: account with email=b already exists"
    }


"""
    Test to update the the password of the authenticated account (no exceptions thrown)
"""
def test_update_password(setup_db, client, session):
    account = session.get(DBAccount, 1)
    old_password = "old_password"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(old_password.encode("utf-8"), salt).decode("utf-8")
    
    account.hashed_password = hashed_password
    session.add(account)
    session.commit()
    
    # Test updating password
    headers = auth_headers(1)
    request_data = {"old_password": old_password, "new_password": "new_password"}
    response = client.put("/accounts/me/password", data=request_data, headers=headers)
    
    assert response.status_code == 204
    
    # Verify password change worked by trying to get a token with the new password
    token_response = client.post("/auth/token", data={"username": "a", "password": "new_password"})
    assert token_response.status_code == 200


"""
    Test to update the the password of the authenticated account with an invalid username or
    password (InvalidCredentials exception raised)
"""
def test_update_password_invalid(setup_db, client, session):
    account = session.get(DBAccount, 1)
    correct_password = "correct_password"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(correct_password.encode("utf-8"), salt).decode("utf-8")
    
    account.hashed_password = hashed_password
    session.add(account)
    session.commit()
    
    # Test updating password with wrong old_password
    headers = auth_headers(1)
    request_data = {"old_password": "wrong_password", "new_password": "new_password"}
    response = client.put("/accounts/me/password", data=request_data, headers=headers)
    
    assert response.status_code == 401
    assert response.json() == {
        "error": "invalid_credentials",
        "message": "Authentication failed: invalid username or password"
    }


"""
    Delete the authenticated account (no exceptions thrown)
"""
def test_delete_account(setup_db, client):
    # Account id=3 doesn't own any chat
    headers = auth_headers(3)
    response = client.delete("/accounts/me", headers=headers)
    
    assert response.status_code == 204
    
    # Verify the account was deleted
    get_response = client.get("/accounts/3")
    assert get_response.status_code == 404


"""
    Delete the authenticated account where the authenticated account is the owner of a chat
    (ChatOwnerRemovalError exception is thrown)
"""
def test_delete_account_with_owned_chats(setup_db, client):
    # Account id=1 owns chats
    headers = auth_headers(1)
    response = client.delete("/accounts/me", headers=headers)
    
    assert response.status_code == 422
    assert response.json() == {
        "error": "chat_owner_removal",
        "message": "Unable to remove the owner of a chat"
    }


"""
    Test the authentication required error when no token is provided
"""
def test_authentication_required(setup_db, client):
    # Access a protected route without authentication
    response = client.get("/accounts/me")
    
    assert response.status_code == 403
    assert response.json() == {
        "error": "authentication_required",
        "message": "Not authenticated"
    }


"""
    Test the invalid access token error
"""
def test_invalid_access_token(setup_db, client):
    # Creating an invalid token
    headers = {"Authorization": "Bearer invalid.token.format"}
    response = client.get("/accounts/me", headers=headers)
    
    assert response.status_code == 403
    assert response.json() == {
        "error": "invalid_access_token",
        "message": "Authentication failed: invalid access token"
    }


"""
    Test the access denied error when trying to create a chat for another account
"""
def test_create_chat_access_denied(setup_db, client):
    # Authenticate as account 1 but try to create a chat for account 2
    headers = auth_headers(1)
    request_data = {"name": "New Chat", "owner_id": 2}
    response = client.post("/chats", json=request_data, headers=headers)
    
    assert response.status_code == 403
    assert response.json() == {
        "error": "access_denied",
        "message": "Cannot create chat on behalf of different account"
    }


"""
    Test the expired access token error
"""
def test_expired_token(setup_db, client):

    # Create a token that's already expired (issued 2 hours ago with 1 hour expiry)
    iat = int((datetime.now(timezone.utc) - timedelta(hours=2)).timestamp())
    exp = iat + 3600  # 1 hour after the issued time, so expired 1 hour ago
    
    payload = {
        "sub": "1",  # Account ID 1
        "iss": JWT_ISSUER,
        "iat": iat,
        "exp": exp
    }
    
    expired_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    # Try to access a protected route with the expired token
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/accounts/me", headers=headers)
    
    # Verify we get the expired token error
    assert response.status_code == 403
    assert response.json() == {
        "error": "expired_access_token",
        "message": "Authentication failed: expired access token"
    }