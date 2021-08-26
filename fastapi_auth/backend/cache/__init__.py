from .base import BaseCacheBackend

try:
    from .redis import RedisBackend
except ImportError:
    pass
