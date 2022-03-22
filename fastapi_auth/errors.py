class FastAPIAuthException(Exception):
    pass


# captcha
class InvalidCaptchaError(FastAPIAuthException):
    pass


# email
class EmailAlreadyExistsError(FastAPIAuthException):
    pass


class EmailAlreadyVerifiedError(FastAPIAuthException):
    pass


class EmailMismatchError(FastAPIAuthException):
    pass


class SameEmailError(FastAPIAuthException):
    pass


# username
class UsernameAlreadyExistsError(FastAPIAuthException):
    pass


class SameUsernameError(FastAPIAuthException):
    pass


# password
class PasswordAlreadyExistsError(FastAPIAuthException):
    pass


class PasswordNotSetError(FastAPIAuthException):
    pass


class InvalidPasswordError(FastAPIAuthException):
    pass


# db
class UserNotFoundError(FastAPIAuthException):
    pass


# rate limit
class TimeoutError(FastAPIAuthException):
    pass


# oauth
class OAuthLoginOnlyError(FastAPIAuthException):
    pass


# oauth account
class OAuthAccountAlreadyExistsError(FastAPIAuthException):
    pass


class OAuthAccountNotSetError(FastAPIAuthException):
    pass


# jwt
class TokenDecodingError(FastAPIAuthException):
    pass


class WrongTokenTypeError(FastAPIAuthException):
    pass


class TokenAlreadyUsedError(FastAPIAuthException):
    pass


# authorization
class AuthorizationError(FastAPIAuthException):
    pass


# ban
class UserNotActiveError(AuthorizationError):
    pass
