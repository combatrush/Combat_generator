import pytest
from app.models.animation import Animation
from app.services.animator import AnimationTask
from app import db

def test_create_animation(client, auth_headers):
    """Test animation creation"""
    response = client.post('/api/animation/create', 
        headers=auth_headers,
        json={
            'title': 'Test Animation',
            'description': 'Test description',
            'scene_data': {'test': 'data'}
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'Test Animation'
    assert data['status'] == 'draft'

def test_get_animation(client, auth_headers, test_user):
    """Test getting animation details"""
    # Create test animation
    animation = Animation(
        title='Test Animation',
        user_id=test_user.id,
        scene_data={'test': 'data'}
    )
    db.session.add(animation)
    db.session.commit()

    response = client.get(f'/api/animation/{animation.id}', 
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'Test Animation'

def test_update_animation(client, auth_headers, test_user):
    """Test updating animation"""
    animation = Animation(
        title='Old Title',
        user_id=test_user.id,
        scene_data={'test': 'data'}
    )
    db.session.add(animation)
    db.session.commit()

    response = client.put(f'/api/animation/{animation.id}',
        headers=auth_headers,
        json={
            'title': 'New Title',
            'scene_data': {'updated': 'data'}
        }
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'New Title'

def test_render_animation(client, auth_headers, test_user):
    """Test animation rendering"""
    animation = Animation(
        title='Test Animation',
        user_id=test_user.id,
        scene_data={'test': 'data'}
    )
    db.session.add(animation)
    db.session.commit()

    response = client.post(f'/api/animation/{animation.id}/render',
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.get_json()
    assert 'task_id' in data
    assert data['status'] == 'rendering'

def test_generate_character(client, auth_headers):
    """Test character generation"""
    response = client.post('/api/animation/character',
        headers=auth_headers,
        json={
            'prompt': 'A tall warrior',
            'style': 'fantasy',
            'attributes': {'height': 'tall', 'class': 'warrior'}
        }
    )
    assert response.status_code == 200
    data = response.get_json()
    assert 'model_data' in data

def test_generate_effects(client, auth_headers):
    """Test effects generation"""
    response = client.post('/api/animation/effects',
        headers=auth_headers,
        json={
            'type': 'fire',
            'parameters': {'intensity': 0.8}
        }
    )
    assert response.status_code == 200
    data = response.get_json()
    assert 'effect_data' in data

def test_generate_sound(client, auth_headers):
    """Test sound generation"""
    response = client.post('/api/animation/sound',
        headers=auth_headers,
        json={
            'type': 'battle',
            'parameters': {'duration': 10}
        }
    )
    assert response.status_code == 200
    data = response.get_json()
    assert 'audio_data' in data

def test_generate_environment(client, auth_headers):
    """Test environment generation"""
    response = client.post('/api/animation/environment',
        headers=auth_headers,
        json={
            'prompt': 'Ancient temple',
            'style': 'fantasy',
            'parameters': {'time_of_day': 'sunset'}
        }
    )
    assert response.status_code == 200
    data = response.get_json()
    assert 'environment_data' in data

def test_list_animations(client, auth_headers, test_user):
    """Test listing user animations"""
    # Create test animations
    for i in range(3):
        animation = Animation(
            title=f'Animation {i}',
            user_id=test_user.id,
            scene_data={'test': 'data'}
        )
        db.session.add(animation)
    db.session.commit()

    response = client.get('/api/animation/list',
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['animations']) == 3
    assert data['total'] == 3
