import os
import tempfile
import pytest
from flask import url_for
from app import app, db, add_admin, Email

# Configure the test client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

# Test add_admin function
def test_add_admin(client):
    username = "testadmin"
    password = "testpassword"
    add_admin(username, password)

    admin = Admin.query.filter_by(username=username).first()
    assert admin is not None
    assert admin.username == username
    assert admin.check_password(password)

# Test email form
def test_email_form(client):
    response = client.post('/', data={'email': 'test@example.com'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Thank You!" in response.data

    email = Email.query.filter_by(email='test@example.com').first()
    assert email is not None
    assert email.email == 'test@example.com'
