import os
from flask import Flask, url_for, redirect
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from sqlalchemy import select
from flask_migrate import Migrate

from .extensions import db, bcrypt

load_dotenv()


jwt = JWTManager()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is not None:
        app.config.from_mapping(test_config)
    else:
        app.config.from_pyfile('config.py', silent=True)


    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "fallback-secret-key"),
        SQLALCHEMY_DATABASE_URI=os.getenv("POSTGRES_URI"),
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "fallback-jwt-secret"),
        SQLALCHEMY_ECHO=True,
        JWT_TOKEN_LOCATION=["cookies"],
        JWT_COOKIE_SECURE=False,
        JWT_COOKIE_CSRF_PROTECT=False
    )


    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate = Migrate(app, db)


    from .routes.auth.auth import auth
    from .routes.orgs.orgs import org
    app.register_blueprint(auth)
    app.register_blueprint(org)
    

    with app.app_context():
        db.create_all()

    return app



@jwt.user_identity_loader
def user_identity_lookup(identity):
    """Converts whatever identity structure is provided into a clean string."""
    if hasattr(identity, "id"):
        return str(identity.id)
    return str(identity)


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """Automatically loads the full User database object using the token payload."""
    from app.models.dbModel import User
    
    identity = int(jwt_data["sub"])
    query = select(User).where(User.id == identity)
    return db.session.scalars(query).first()



@jwt.unauthorized_loader
def handle_missing_cookie_callback(error_string):
    return redirect(url_for('auth.register'))

@jwt.expired_token_loader
def handle_expired_cookie_callback(jwt_header, jwt_data):
    return redirect(url_for('auth.register'))
