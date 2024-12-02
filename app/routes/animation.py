from flask import Blueprint, request, jsonify
from ..auth.auth import require_auth, require_role
from ..models.animation import Animation
from ..services.animator import AnimationTask
from ..services.character_generator import CharacterGenerator
from ..services.effects_generator import EffectsGenerator
from ..services.sound_generator import SoundGenerator
from ..services.environment_generator import EnvironmentGenerator
from .. import db, celery

bp = Blueprint('animation', __name__, url_prefix='/api/animation')

@bp.route('/create', methods=['POST'])
@require_auth
def create_animation():
    """Create new animation project"""
    try:
        data = request.get_json()
        animation = Animation(
            title=data.get('title', 'Untitled Animation'),
            description=data.get('description', ''),
            user_id=request.user_id,
            scene_data=data.get('scene_data', {}),
            settings=data.get('settings', {}),
            status='draft'
        )
        db.session.add(animation)
        db.session.commit()
        return jsonify(animation.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>', methods=['GET'])
@require_auth
def get_animation(id):
    """Get animation details"""
    animation = Animation.query.get_or_404(id)
    if animation.user_id != request.user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(animation.to_dict())

@bp.route('/<int:id>', methods=['PUT'])
@require_auth
def update_animation(id):
    """Update animation details"""
    animation = Animation.query.get_or_404(id)
    if animation.user_id != request.user_id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    animation.title = data.get('title', animation.title)
    animation.description = data.get('description', animation.description)
    animation.scene_data = data.get('scene_data', animation.scene_data)
    animation.settings = data.get('settings', animation.settings)
    
    db.session.commit()
    return jsonify(animation.to_dict())

@bp.route('/<int:id>/render', methods=['POST'])
@require_auth
def render_animation(id):
    """Start animation rendering"""
    animation = Animation.query.get_or_404(id)
    if animation.user_id != request.user_id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    task = AnimationTask().delay(
        animation.scene_data,
        f'outputs/{animation.id}.mp4'
    )
    
    animation.render_task_id = task.id
    animation.status = 'rendering'
    db.session.commit()
    
    return jsonify({
        'task_id': task.id,
        'status': 'rendering'
    })

@bp.route('/<int:id>/status', methods=['GET'])
@require_auth
def get_render_status(id):
    """Get animation render status"""
    animation = Animation.query.get_or_404(id)
    if animation.user_id != request.user_id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    if animation.render_task_id:
        task = celery.AsyncResult(animation.render_task_id)
        return jsonify({
            'status': task.status,
            'progress': task.info.get('progress', 0) if task.info else 0
        })
    return jsonify({'status': animation.status})

@bp.route('/character', methods=['POST'])
@require_auth
def generate_character():
    """Generate character using AI"""
    try:
        data = request.get_json()
        character = CharacterGenerator().generate(
            prompt=data['prompt'],
            style=data.get('style', 'modern'),
            attributes=data.get('attributes', {})
        )
        return jsonify(character)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/effects', methods=['POST'])
@require_auth
def generate_effects():
    """Generate visual effects"""
    try:
        data = request.get_json()
        effects = EffectsGenerator().generate(
            effect_type=data['type'],
            parameters=data.get('parameters', {})
        )
        return jsonify(effects)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/sound', methods=['POST'])
@require_auth
def generate_sound():
    """Generate sound effects or music"""
    try:
        data = request.get_json()
        sound = SoundGenerator().generate(
            sound_type=data['type'],
            parameters=data.get('parameters', {})
        )
        return jsonify(sound)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/environment', methods=['POST'])
@require_auth
def generate_environment():
    """Generate 3D environment"""
    try:
        data = request.get_json()
        environment = EnvironmentGenerator().generate(
            prompt=data['prompt'],
            style=data.get('style', 'modern'),
            parameters=data.get('parameters', {})
        )
        return jsonify(environment)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/list', methods=['GET'])
@require_auth
def list_animations():
    """List user's animations"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    animations = Animation.query.filter_by(user_id=request.user_id)\
        .order_by(Animation.created_at.desc())\
        .paginate(page=page, per_page=per_page)
        
    return jsonify({
        'animations': [a.to_dict() for a in animations.items],
        'total': animations.total,
        'pages': animations.pages,
        'current_page': animations.page
    })
