from app.extensions import db
from ..models.dbModel import User
from sqlalchemy import select
from app.services.paswordService import PasswordService
from sqlalchemy.exc import IntegrityError

class User_Repository:
    @staticmethod
    def create_user(first_name, last_name, username, email, phone_no, password):
        password_hash = PasswordService.hash_password(password)
        new_user = User(
            first_name=first_name, 
            last_name=last_name,
            username=username,
            email=email,
            phone_no=phone_no,
            password_hash=password_hash
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            return new_user 
        except IntegrityError:
            db.session.rollback()
            raise ValueError("A user with this email, username, or phone number already exists.")
        except Exception as e:
            db.session.rollback()
            raise e 
        
    @staticmethod
    def get_user_by_email(email):
        query = select(User).where(User.email == email)
        return db.session.scalars(query).first()
    
    @staticmethod
    def get_user_by_id(user_id):
        query = select(User).where(User.id == user_id)
        return db.session.scalars(query).first()
