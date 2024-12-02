from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, request, jsonify
from functools import wraps
from ..models.user import User
from .. import db

def get_token_from_header() -> Optional[str]:
    """Extract token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or 'Bearer ' not in auth_header:
        return None
    return auth_header.split('Bearer ')[1]

def create_token(user_id: int, expiry_hours: int = 24) -> str:
    """Create JWT token for user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=expiry_hours),
        'iat': datetime.utcnow()
    }
    return jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

def verify_token(token: str) -> Optional[Dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return jsonify({'error': 'No token provided'}), 401
            
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
            
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 401
            
        return f(*args, **kwargs)
    return decorated

def require_role(role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_token_from_header()
            if not token:
                return jsonify({'error': 'No token provided'}), 401
                
            payload = verify_token(token)
            if not payload:
                return jsonify({'error': 'Invalid token'}), 401
                
            user = User.query.get(payload['user_id'])
            if not user:
                return jsonify({'error': 'User not found'}), 401
                
            if role not in user.roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
                
            return f(*args, **kwargs)
        return decorated
    return decorator

class AuthService:
    @staticmethod
    def register_user(
        email: str,
        password: str,
        username: str,
        roles: list = None
    ) -> Dict:
        """Register new user"""
        if User.query.filter_by(email=email).first():
            raise ValueError('Email already registered')
            
        if User.query.filter_by(username=username).first():
            raise ValueError('Username already taken')
            
        user = User(
            email=email,
            username=username,
            password_hash=generate_password_hash(password),
            roles=roles or ['user']
        )
        
        db.session.add(user)
        db.session.commit()
        
        token = create_token(user.id)
        
        return {
            'token': token,
            'user': user.to_dict()
        }
        
    @staticmethod
    def login_user(email: str, password: str) -> Dict:
        """Login user"""
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            raise ValueError('Invalid email or password')
            
        token = create_token(user.id)
        
        return {
            'token': token,
            'user': user.to_dict()
        }
        
    @staticmethod
    def refresh_token(user_id: int) -> str:
        """Refresh user token"""
        return create_token(user_id)
        
    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str):
        """Change user password"""
        user = User.query.get(user_id)
        if not user or not check_password_hash(user.password_hash, old_password):
            raise ValueError('Invalid password')
            
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
    @staticmethod
    def update_roles(user_id: int, roles: list, admin_user_id: int):
        """Update user roles (admin only)"""
        admin = User.query.get(admin_user_id)
        if not admin or 'admin' not in admin.roles:
            raise ValueError('Insufficient permissions')
            
        user = User.query.get(user_id)
        if not user:
            raise ValueError('User not found')
            
        user.roles = roles
        db.session.commit()
