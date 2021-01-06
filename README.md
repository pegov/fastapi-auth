# FastAPI-Auth

It is a personal project.

### Usage

Create global object and import it, otherwise it is a complete mess.
```python
# auth.py
...
from fastapi_auth import FastAPIAuth

auth = FastAPIAuth(...)

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

### Dependency injections:
```python
from fastapi_auth import get_user, get_authenticated_user, admin_required

# return User
from fastapi_auth import User
```

