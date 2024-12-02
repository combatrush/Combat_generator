from typing import Dict, List
import os

class Config:
    # Base paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    ASSET_DIR = os.path.join(BASE_DIR, 'assets')
    
    # Asset generation settings
    ASSET_GENERATION = {
        'character': {
            'model_id': 'stabilityai/stable-diffusion-2-1',
            'inference_steps': 50,
            'guidance_scale': 7.5,
            'trait_categories': {
                'personality': ['friendly', 'aggressive', 'mysterious', 'heroic', 'villainous'],
                'appearance': ['tall', 'short', 'muscular', 'slim', 'armored', 'magical'],
                'abilities': ['magic', 'martial_arts', 'technology', 'supernatural', 'weapons']
            },
            'supported_styles': ['modern', 'fantasy', 'sci-fi', 'historical'],
            'body_types': ['athletic', 'slim', 'muscular', 'heavy'],
            'age_ranges': ['child', 'teen', 'adult', 'elderly'],
            'max_polygon_count': 50000,
            'texture_resolution': 2048,
            'rigging_type': 'mixamo_compatible'
        },
        'effects': {
            'particle_systems': ['fire', 'water', 'smoke', 'magic', 'electricity'],
            'max_particle_count': 10000,
            'physics_enabled': True,
            'supported_formats': ['vfx', 'particle_json', 'houdini_compatible']
        },
        'sound': {
            'sample_rate': 44100,
            'channels': 2,
            'formats': ['wav', 'mp3', 'ogg'],
            'max_duration': 300,  # seconds
            'categories': ['effects', 'music', 'ambient', 'voice']
        },
        'environment': {
            'max_scene_size': 1000,  # meters
            'lod_levels': 3,
            'lighting_types': ['realtime', 'baked', 'mixed'],
            'weather_systems': ['clear', 'rain', 'snow', 'storm']
        }
    }
    
    # Asset sources configuration
    ASSET_SOURCES = {
        'mixamo': {
            'api_endpoint': 'https://www.mixamo.com/api',
            'auth_required': True,
            'supported_types': ['characters', 'animations'],
            'rate_limit': 100  # requests per hour
        },
        'sketchfab': {
            'api_endpoint': 'https://api.sketchfab.com/v3',
            'auth_required': True,
            'supported_types': ['models', 'textures'],
            'rate_limit': 100
        },
        'freesound': {
            'api_endpoint': 'https://freesound.org/apiv2',
            'auth_required': True,
            'supported_types': ['sound_effects', 'ambient'],
            'rate_limit': 200
        },
        'turbosquid': {
            'api_endpoint': 'https://api.turbosquid.com/v1',
            'auth_required': True,
            'supported_types': ['models', 'textures', 'environments'],
            'rate_limit': 50
        }
    }
    
    # Marketplace settings
    MARKETPLACE = {
        'commission_rate': 0.15,
        'min_price': 0.99,
        'supported_currencies': ['USD', 'EUR', 'GBP'],
        'featured_slots': 10,
        'categories': {
            'characters': ['humanoid', 'creatures', 'robots'],
            'animations': ['combat', 'movement', 'gestures'],
            'effects': ['natural', 'magical', 'sci-fi'],
            'environments': ['indoor', 'outdoor', 'space']
        }
    }
    
    # Asset optimization settings
    OPTIMIZATION = {
        'max_texture_size': 4096,
        'supported_formats': {
            'models': ['fbx', 'obj', 'gltf'],
            'textures': ['png', 'jpg', 'tga'],
            'animations': ['fbx', 'bvh'],
            'audio': ['wav', 'mp3', 'ogg']
        },
        'compression': {
            'texture_compression': 'BC7',
            'mesh_compression': True,
            'audio_compression': 'vorbis'
        }
    }
    
    # Search and organization
    SEARCH = {
        'elasticsearch_url': 'http://localhost:9200',
        'index_prefix': 'combat_gods_',
        'search_fields': ['name', 'description', 'tags', 'category'],
        'aggregations': ['category', 'style', 'rating']
    }
    
    # Legal and licensing
    LEGAL = {
        'supported_licenses': {
            'creative_commons': ['CC0', 'CC-BY', 'CC-BY-SA'],
            'commercial': ['standard', 'extended', 'enterprise']
        },
        'required_metadata': [
            'creator', 'license_type', 'usage_rights', 'attribution'
        ],
        'content_filters': {
            'violence_level': ['none', 'mild', 'moderate'],
            'age_rating': ['all', 'teen', 'mature']
        }
    }
    
    # Basic Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-replace-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis and Celery configs
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # Storage Configuration
    UPLOAD_FOLDER = 'uploads'
    ASSET_LIBRARY_PATH = 'assets'
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    
    # Rendering Configuration
    RENDER_PRESETS = {
        'preview': {
            'resolution': (854, 480),
            'fps': 30,
            'quality': 'low',
            'max_duration': 300  # 5 minutes
        },
        'standard': {
            'resolution': (1920, 1080),
            'fps': 60,
            'quality': 'high',
            'max_duration': 1800  # 30 minutes
        },
        '4k': {
            'resolution': (3840, 2160),
            'fps': 60,
            'quality': 'ultra',
            'max_duration': 3600  # 1 hour
        }
    }
    
    # Subscription Tiers
    SUBSCRIPTION_TIERS = {
        'free': {
            'max_projects': 2,
            'max_duration': 300,  # 5 minutes
            'max_resolution': '1080p',
            'storage_limit': 1024 * 1024 * 1024,  # 1GB
            'collaboration': False,
            'features': ['basic_assets', 'basic_effects']
        },
        'pro': {
            'max_projects': 10,
            'max_duration': 1800,  # 30 minutes
            'max_resolution': '4k',
            'storage_limit': 50 * 1024 * 1024 * 1024,  # 50GB
            'collaboration': True,
            'features': ['all_assets', 'advanced_effects', 'custom_assets']
        },
        'enterprise': {
            'max_projects': -1,  # unlimited
            'max_duration': -1,   # unlimited
            'max_resolution': '4k',
            'storage_limit': -1,  # unlimited
            'collaboration': True,
            'features': ['all_features', 'api_access', 'priority_rendering']
        }
    }
    
    # Asset Categories
    ASSET_CATEGORIES = {
        'characters': ['human', 'fantasy', 'sci-fi', 'animal', 'monster'],
        'environments': ['urban', 'nature', 'fantasy', 'sci-fi', 'indoor'],
        'props': ['weapons', 'vehicles', 'furniture', 'effects'],
        'animations': ['combat', 'movement', 'idle', 'special']
    }
    
    # Physics Simulation
    PHYSICS_SETTINGS = {
        'timestep': 1/240,  # High precision physics
        'gravity': -9.81,
        'collision_margin': 0.001,
        'solver_iterations': 50
    }
    
    # Real-time Collaboration
    WEBSOCKET_PING_TIMEOUT = 60
    WEBSOCKET_PING_INTERVAL = 25
    MAX_COLLABORATORS = 10
    
    # API Rate Limits
    API_RATE_LIMITS = {
        'free': '100/hour',
        'pro': '1000/hour',
        'enterprise': '10000/hour'
    }
    
    # Cache Configuration
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Export Formats
    EXPORT_FORMATS = {
        'video': ['mp4', 'webm', 'mov'],
        'animation': ['fbx', 'gltf', 'bvh'],
        'image': ['png', 'jpg', 'gif']
    }
