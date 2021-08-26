from passlib.context import CryptContext

# TODO: to backend

pwd_context = CryptContext(
    schemes=["bcrypt", "django_pbkdf2_sha256"], deprecated="auto"
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
