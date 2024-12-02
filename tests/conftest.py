import pytest
from app import create_app, db
from app.models.user import User
from app.models.animation import Animation
from app.auth.auth import create_token

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create test user"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            roles=['user']
        )
        user.password_hash = 'test_hash'
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def admin_user(app):
    """Create admin user"""
    with app.app_context():
        user = User(
            username='admin',
            email='admin@example.com',
            roles=['admin', 'user']
        )
        user.password_hash = 'admin_hash'
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers"""
    token = create_token(test_user.id)
    return {'Authorization': f'Bearer {token}'}
