import pytest
from app import app as flask_app  # Import your Flask app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
   # Check if certain text is in the response

def test_create_page_get(client):
    response = client.get('/create/')
    assert response.status_code == 200

# Add more tests as needed for different routes and scenarios
