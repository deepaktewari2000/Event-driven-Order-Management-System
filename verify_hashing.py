from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

try:
    hash = pwd_context.hash("testpassword")
    print("SUCCESS: Hashed password: ", hash)
except Exception as e:
    print("FAILURE: ", e)
