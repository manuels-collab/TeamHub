
'''



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

'''

import base64

from flask import abort

def encode_cursor(entity_id: int):
    return base64.urlsafe_b64encode(str(entity_id).encode()).decode()


def decode_cursor(token: str):
    try:
        return int(base64.urlsafe_b64decode(token.encode()).decode())
    except Exception as e:
        abort(400, description=f"Invalid cursor token: {e}")


strname = encode_cursor(888)
encoded_value = decode_cursor(strname)
print(encoded_value)  # Output: b'888'
print(strname)  # Output: b'123'