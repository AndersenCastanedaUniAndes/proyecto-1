import pytest
from unittest.mock import patch, mock_open, MagicMock
from app.services.key_service import KeyService

@pytest.fixture
def key_service_instance():
    with patch("app.services.key_service.PRIVATE_KEY_PATH", "private.pem"), \
         patch("app.services.key_service.PUBLIC_KEY_PATH", "public.pem"), \
         patch("app.services.key_service.JWKS_PATH", "jwks.json"), \
         patch("app.services.key_service.KEY_ID", "testkid"):
        ks = KeyService()
        ks.private_key = MagicMock()
        ks.public_key = MagicMock()
        ks.jwks = {"keys": []}
        ks.current_kid = "testkid"
        return ks
 


def test_get_private_key_not_loaded():
    ks = KeyService()
    ks.private_key = None
    with pytest.raises(ValueError):
        ks.get_private_key()


def test_get_public_key_not_loaded():
    ks = KeyService()
    ks.public_key = None
    with pytest.raises(ValueError):
        ks.get_public_key()


def test_get_jwks_not_loaded():
    ks = KeyService()
    ks.jwks = None
    with pytest.raises(ValueError):
        ks.get_jwks()


def test_load_keys_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            KeyService().load_keys()