from flask import Blueprint, request, jsonify
from ..auth.auth import AuthService, require_auth
from ..models.user import User
from .. import db

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        result = AuthService.register_user(
            email=data['email'],
            password=data['password'],
            username=data['username']
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Registration failed'}), 500

@bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        result = AuthService.login_user(
            email=data['email'],
            password=data['password']
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500

@bp.route('/refresh', methods=['POST'])
@require_auth
def refresh_token():
    """Refresh authentication token"""
    try:
        user_id = request.user_id  # Set by require_auth decorator
        token = AuthService.refresh_token(user_id)
        return jsonify({'token': token}), 200
    except Exception as e:
        return jsonify({'error': 'Token refresh failed'}), 500

@bp.route('/password', methods=['PUT'])
@require_auth
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        user_id = request.user_id  # Set by require_auth decorator
        AuthService.change_password(
            user_id,
            data['old_password'],
            data['new_password']
        )
        return jsonify({'message': 'Password updated'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Password change failed'}), 500

@bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get user profile"""
    try:
        user = User.query.get(request.user_id)
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get profile'}), 500

@bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        user = User.query.get(request.user_id)
        
        # Update allowed fields
        if 'display_name' in data:
            user.display_name = data['display_name']
        if 'bio' in data:
            user.bio = data['bio']
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']
        if 'settings' in data:
            user.update_settings(data['settings'])
        if 'preferences' in data:
            user.update_preferences(data['preferences'])
            
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Profile update failed'}), 500

@bp.route('/api-key', methods=['POST'])
@require_auth
def generate_api_key():
    """Generate new API key"""
    try:
        user = User.query.get(request.user_id)
        api_key = user.generate_api_key()
        db.session.commit()
        return jsonify({'api_key': api_key}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to generate API key'}), 500

@bp.route('/api-usage', methods=['GET'])
@require_auth
def get_api_usage():
    """Get API usage statistics"""
    try:
        user = User.query.get(request.user_id)
        return jsonify({
            'quota': user.api_quota,
            'usage': user.api_usage
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get API usage'}), 500
