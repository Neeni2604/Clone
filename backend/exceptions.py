from fastapi.responses import JSONResponse

"""
    Exception for when a model doesn't exist in the database
"""
class ModelDNE(Exception):
    def __init__(self, model_name: str, model_id: int):
        self.message=f"Unable to find {model_name} with id={model_id}"

    def response(self) -> JSONResponse:
        return JSONResponse(
            status_code=404, 
            content={
                "error":"entity_not_found", 
                "message":self.message,
            },
        )


"""
    Exception for when a duplicate model exists
"""
class DuplicateModel(Exception):
    def __init__(self, model_name: str, field: str, value: str):
        self.message = f"Duplicate value: {model_name} with {field}={value} already exists"
        self.field = field
        self.value = value
    
    def response(self) -> JSONResponse:
        return JSONResponse(
            status_code=422, 
            content={
                "error": "duplicate_entity_value", 
                "message": self.message,
            },
        )


"""
    Exception for when a chat membership doesn't exist
"""
class ChatMembershipError(Exception):
    def __init__(self, account_id: int, chat_id: int):
        self.message=f"Account with id={account_id} must be a member of chat with id={chat_id}"
    
    def response(self) -> JSONResponse:
        return JSONResponse(
            status_code=422, 
            content={
                "error":"chat_membership_required", 
                "message":self.message,
            },
        )


"""
    Exception for when a chat owner cannot be removed
"""
class ChatOwnerRemovalError(Exception):
    def __init__(self):
        self.message = "Unable to remove the owner of a chat"

    def response(self) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": "chat_owner_removal",
                "message": self.message,
            },
        )
    

"""
    Exception for invalid credentials (authentication failed)
"""
class InvalidCredentials(Exception):
    def __init__(self):
        self.message = "Authentication failed: invalid username or password"

    def response(self) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={
                "error": "invalid_credentials",
                "message": self.message,
            },
        )
    

"""
    Exception for when authentication is required
"""
class AuthenticationRequiredError(Exception):
    def __init__(self):
        self.message = "Not authenticated"
    
    def response(self) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={
                "error": "authentication_required",
                "message": self.message
            }
        )


"""
    Exception for when access token is expired
"""
class ExpiredAccessTokenError(Exception):
    def __init__(self):
        self.message = "Authentication failed: expired access token"
    
    def response(self) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={
                "error": "expired_access_token",
                "message": self.message
            }
        )



"""
    Exception for when access token is invalid
"""
class InvalidAccessTokenError(Exception):
    def __init__(self):
        self.message = "Authentication failed: invalid access token"
    
    def response(self) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={
                "error": "invalid_access_token",
                "message": self.message
            }
        )


"""
    Exception for when you are trying to create a model on behalf of another account
"""
class AccessDeniedError(Exception):
    def __init__(self, model_name: str):
        self.message = f"Cannot create {model_name} on behalf of different account"

    def response(self) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content = {
                "error": "access_denied",
                "message": self.message
            }
        )