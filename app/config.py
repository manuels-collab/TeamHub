import os

class Config:
    SECRET_KEY=os.getenv("SECRET_KEY", "fallback-secret-key")
    SQLALCHEMY_DATABASE_URI=os.getenv("POSTGRES_URI")
    JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "fallback-jwt-secret")
    SQLALCHEMY_ECHO=True
    JWT_TOKEN_LOCATION=["cookies"]
    JWT_COOKIE_SECURE=False
    JWT_COOKIE_CSRF_PROTECT=False
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    
    
class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('POSTGRES_URL', 'sqlite:///dev.db')
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

class StagingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('POSTGRES_URL')
    REDIS_URL = os.environ.get("REDIS_URL")

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('POSTGRES_URL')
    REDIS_URL = os.environ.get("REDIS_URL") # Automatically provided by Railway