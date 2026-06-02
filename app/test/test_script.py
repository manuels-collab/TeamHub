import os 
from dotenv import load_dotenv
from app import create_app
from app.repo.user_repo import User_Repository

load_dotenv()

app = create_app()

with app.app_context():
    try:
        members = User_Repository.login_user("jay@example.com", "password")
        print(f'{members[0].email}')
    except Exception as e:
        print(f"An error occurred during user creation: {e}")
