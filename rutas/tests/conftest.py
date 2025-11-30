import os
from unittest.mock import patch

def pytest_configure():
    patch.dict(os.environ, {
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "DATABASE_URL": "sqlite:///./test.db"
    }).start()