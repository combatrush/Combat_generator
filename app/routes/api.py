from flask import Blueprint, request, jsonify
from ..models.animation import Animation
from ..services.animator import AnimationTask
from .. import db, celery

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/animations', methods=['POST'])
def create_animation():
    data = request.get_json()
    
    # Create new animation record
    animation = Animation(
        title=data.get('title', 'Untitled Animation'),
        description=data.get('description', ''),
        user_id=data.get('user_id'),  # TODO: Get from auth
        scene_data=data.get('scene_data', {})
    )
    
    db.session.add(animation)
    db.session.commit()
    
    # Start async rendering task
    task = AnimationTask().delay(
        animation.scene_data,
        f'outputs/{animation.id}.mp4'
    )
    
    return jsonify({
        'animation_id': animation.id,
        'task_id': task.id
    }), 201

@bp.route('/animations/<int:id>', methods=['GET'])
def get_animation(id):
    animation = Animation.query.get_or_404(id)
    return jsonify(animation.to_dict())

@bp.route('/animations/<int:id>/status', methods=['GET'])
def get_animation_status(id):
    animation = Animation.query.get_or_404(id)
    return jsonify({
        'status': animation.status,
        'progress': animation.render_progress
    })

@bp.route('/animations/<int:id>', methods=['PUT'])
def update_animation(id):
    animation = Animation.query.get_or_404(id)
    data = request.get_json()
    
    # Update allowed fields
    for field in ['title', 'description', 'scene_data']:
        if field in data:
            setattr(animation, field, data[field])
    
    db.session.commit()
    return jsonify(animation.to_dict())
