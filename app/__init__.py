from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from celery import Celery
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
celery = Celery('combat_generator',
                broker='redis://localhost:6379/0',
                backend='redis://localhost:6379/0')
cors = CORS()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    celery.conf.update(app.config)
    cors.init_app(app)

    # Register blueprints
    from .routes import main, api, auth, animation
    app.register_blueprint(main.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(animation.bp)

    return app
