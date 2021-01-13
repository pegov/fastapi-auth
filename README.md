# FastAPI-Auth

It is a personal project.

### Usage

Create global object and import it, otherwise it is a complete mess.
```python
# auth.py
...
from fastapi_auth import AuthApp

auth = AuthApp(...)

# main.py
...
from .auth import auth
...
app.include_router(auth.auth_router, prefix="/api/users")
app.include_router(auth.social_router, prefix="/auth")
app.include_router(auth.password_router, prefix="/api/users")
app.include_router(auth.admin_router, prefix="/api/users")
app.include_router(auth.search_router, prefix="/api/users")
...
```

### Startup
```python
# in a startup event
from .auth import auth
...
auth.set_cache(cache) # aioredis client
auth.set_database(database) # motor client
...
```

### Dependency injections
```python
from fastapi import APIRouter, Depends
from fastapi_auth import User
from .auth import auth

router = APIRouter()

@router.get("/anonim")
def anonim_test(user: User = Depends(auth.get_user)):
  ...

@router.get("/user")
def user_test(user: User = Depends(auth.get_authenticated_user)):
  ...

@router.get("/admin", dependencies=[Depends(auth.admin_required)])
def admin_test():
  ...

```

### Dependency injections only
```python
from fastapi_auth import Auth
auth = Auth(...)

# startup
...
auth.set_cache(cache) # aioredis
...
```
