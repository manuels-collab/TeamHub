from flask import jsonify

class AuthService:
    @staticmethod
    def generate_token(user, member=None, response=None):
        from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies

        # 1. If no redirect or custom response is passed, fall back to a default JSON response
        if response is None:
            response = jsonify({
                "msg": "Login successful",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username
                }
            })

        user_id_str = str(user.id)
        
        # 2. Extract role safely whether it's an Enum object (.value) or a standard string
        if member and hasattr(member, 'role'):
            role_value = member.role.value if hasattr(member.role, 'value') else member.role
        else:
            role_value = 'guest'

        additional_claims = {
            "email": user.email, 
            "roles": role_value
        }
        
        # 3. Build token strings
        access_token = create_access_token(identity=user_id_str, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=user_id_str)
        
        # 4. Inject cookies directly into the designated response container
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        
        return response

    @staticmethod
    def delete_token(response=None):
        from flask_jwt_extended import unset_jwt_cookies

        # If a redirect response isn't specified for logouts, return standard JSON message
        if response is None:
            response = jsonify({"msg": "Logged out successfully"})

        # Wipe out all tracking tokens 
        unset_jwt_cookies(response)
        
        return response