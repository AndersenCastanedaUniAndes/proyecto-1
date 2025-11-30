import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from unittest.mock import patch


@pytest.fixture(scope="module")
def db_session():

    # aplicar patch dentro del fixture
    with patch.dict(os.environ, {
        "DATABASE_URL": "sqlite:///./test.db",
        "SECRET_KEY": "test",
        "ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30"
    }):
        from app.models.databases import Base
        from app.services import crud
        from app.models import models

        engine = create_engine("sqlite:///:memory:", echo=False)
        TestingSessionLocal = sessionmaker(bind=engine)
        Base.metadata.create_all(bind=engine)
        db = TestingSessionLocal()

        db.crud = crud
        db.models = models

        yield db

        db.close()
