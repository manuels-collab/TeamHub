from app.extensions import bcrypt


class PasswordService:
    @staticmethod
    def hash_password(password):
        return bcrypt.generate_password_hash(password).decode('utf-8')

    @staticmethod
    def check_password_hash(password_hash, password):
        return bcrypt.check_password_hash(password_hash, password)