from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, set_access_cookies, unset_jwt_cookies
from app.repo.user_repo import User_Repository
from app.services.AuthService import AuthService
from app.services.paswordService import PasswordService

auth = Blueprint('auth', __name__, url_prefix='/')

@auth.route('/', methods=['GET'])
def home():
    return redirect(url_for('org.get_orgs'))

@auth.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        data = request.form
        try:
            new_user = User_Repository.create_user(
                data['first_name'], data['last_name'], data['username'],
                data['email'], data['phone_no'], data['password']
            )
            
            response = redirect(url_for('org.get_orgs'))
            response = AuthService.generate_token(new_user,response=response) 
            return response
            
        except ValueError as e:
            return render_template('registerform.html', error=str(e)), 400
            
    return render_template('registerform.html')
@auth.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('loginform.html')
    
    data = request.form
    email = data.get('email')
    password = data.get('password')
    
    user = User_Repository.get_user_by_email(email)
    
    if not user or not PasswordService.check_password_hash(user.password_hash, password):
        return render_template('loginform.html', error="Invalid Email or Password"), 401
        
    response = redirect(url_for('org.get_orgs'))
    
    response = AuthService.generate_token(user, response=response) 
    
    return response
@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)  
def refresh():
    user_id = get_jwt_identity()
    response = jsonify({"msg": "Token refreshed successfully"})
    new_access_token = create_access_token(identity=str(user_id))
    set_access_cookies(response, new_access_token)
    return response, 200

@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        response = redirect(url_for('auth.login'))
        unset_jwt_cookies(response)
        
        # AuthService.delete_token() 
        
        return response

    return render_template('logout.html')