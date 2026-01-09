from fastapi import HTTPException, status


class OrderNotFoundException(HTTPException):
    """Exception raised when an order is not found."""
    
    def __init__(self, order_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )


class UserNotFoundException(HTTPException):
    """Exception raised when a user is not found."""
    
    def __init__(self, user_id: int = None, email: str = None):
        detail = "User not found"
        if user_id:
            detail = f"User with id {user_id} not found"
        elif email:
            detail = f"User with email {email} not found"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class UnauthorizedException(HTTPException):
    """Exception raised for unauthorized access."""
    
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(HTTPException):
    """Exception raised when user doesn't have permission."""
    
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class InvalidCredentialsException(HTTPException):
    """Exception raised for invalid login credentials."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )


class UserAlreadyExistsException(HTTPException):
    """Exception raised when trying to register with existing email."""
    
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {email} already exists"
        )


class InvalidTokenException(HTTPException):
    """Exception raised for invalid or expired tokens."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


class ValidationException(HTTPException):
    """Exception raised for validation errors."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )
