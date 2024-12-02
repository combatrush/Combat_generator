import pytest
from app.models.user import User

def test_register(client):
    """Test user registration"""
    response = client.post('/api/auth/register', json={
        'email': 'new@example.com',
        'password': 'password123',
        'username': 'newuser'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'token' in data
    assert 'user' in data
    assert data['user']['email'] == 'new@example.com'

def test_login(client, test_user):
    """Test user login"""
    response = client.post('/api/auth/login', json={
        'email': test_user.email,
        'password': 'test_password'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    assert 'user' in data
    assert data['user']['email'] == test_user.email

def test_refresh_token(client, auth_headers):
    """Test token refresh"""
    response = client.post('/api/auth/refresh', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data

def test_change_password(client, auth_headers):
    """Test password change"""
    response = client.put('/api/auth/password', headers=auth_headers, json={
        'old_password': 'test_password',
        'new_password': 'new_password123'
    })
    assert response.status_code == 200

def test_get_profile(client, auth_headers, test_user):
    """Test getting user profile"""
    response = client.get('/api/auth/profile', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['email'] == test_user.email

def test_update_profile(client, auth_headers):
    """Test updating user profile"""
    response = client.put('/api/auth/profile', headers=auth_headers, json={
        'display_name': 'Test User',
        'bio': 'Test bio'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['display_name'] == 'Test User'
    assert data['bio'] == 'Test bio'

def test_generate_api_key(client, auth_headers):
    """Test API key generation"""
    response = client.post('/api/auth/api-key', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'api_key' in data

def test_get_api_usage(client, auth_headers):
    """Test getting API usage"""
    response = client.get('/api/auth/api-usage', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'quota' in data
    assert 'usage' in data
