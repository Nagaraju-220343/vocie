import pytest
from fastapi.testclient import TestClient

from app.config.settings import settings
from app.db.indexes import ensure_indexes
from app.db.mongodb import MongoDBManager
from app.main import app

@pytest.fixture(scope="session", autouse=True)
def test_db():
    settings.mongodb_database = settings.mongodb_test_database
    MongoDBManager.connect()
    ensure_indexes()
    
    db = MongoDBManager.get_db()
    for collection_name in db.list_collection_names():
        db[collection_name].delete_many({})
        
    yield db
    MongoDBManager.disconnect()

@pytest.fixture(autouse=True)
def clean_db(test_db):
    for collection_name in test_db.list_collection_names():
        test_db[collection_name].delete_many({})
    yield test_db

@pytest.fixture
def client():
    # Do not use 'with TestClient' to avoid lifespan triggering which disconnects the DB
    yield TestClient(app)
