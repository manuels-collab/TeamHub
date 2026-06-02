from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from app.repo.member_repo import Member_Repository
from app.repo.org_repo import Organization_Repository
from app.repo.user_repo import User_Repository
from app.services.AuthService import AuthService
from app.services.roleService import check_role_condition
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from app.extensions import db

org = Blueprint("org", __name__, url_prefix="/orgs")


@org.route("/org", methods=['POST', 'GET'])
@jwt_required()
def create_org():
    if request.method == 'POST':
        data = request.form
        try:
            user_id = get_jwt_identity()
            new_org = Organization_Repository.create_organization(
                name=data['name'],
                slug=data['slug'],
                description=data['description'],
                owner_id=user_id
            )
            first_member = Member_Repository.create_member(
                user_id=user_id,
                role='admin',
                org_id=new_org.id
            )
            db.session.add(new_org)
            db.session.add(first_member)
            db.session.commit()
            
            response = redirect(url_for('org.get_orgs'))
            response = AuthService.generate_token(current_user, member=first_member, response=response)
            return response
            
        except Exception as e:
            db.session.rollback()
            return render_template("org_form.html", error=str(e)), 500 
    else:
        return render_template("org_form.html")


@org.route("/get_orgs", methods=["GET"])
@jwt_required()
def get_orgs():
    user_id = get_jwt_identity()
    organisations = Organization_Repository.get_organizations(user_id)

    return render_template(
        "org_list.html",
        organisations=organisations
    )
    
    
@org.route("/get_org/<int:org_id>", methods=['GET'])
@jwt_required()
def get_org_details(org_id):
    org_item = Organization_Repository.get_organization_by_id(org_id)
    if not org_item:
        return render_template("org_list.html", error="Organization not found"), 404
        
    result_data = Member_Repository.get_organisation_members(org_id)
    members = result_data.get("members", []) if isinstance(result_data, dict) else result_data

    return render_template(
        "org_details.html", 
        organization=org_item, 
        members=members
    )
    
    
@org.route("/<int:org_id>/create_member", methods=['POST', 'GET'])
@jwt_required()
@check_role_condition()
def invite_members(org_id):
    org_item = Organization_Repository.get_organization_by_id(org_id)
    if not org_item:
        return redirect(url_for('org.get_orgs'))
    
    if request.method == 'POST':
        data = request.form
        user_email = data['email']
        user = User_Repository.get_user_by_email(user_email)
        
        if not user:
            return render_template("invite_member_form.html", org=org_item, error="User email not found"), 404
            
        try:
            create_members = Member_Repository.create_member(
                user_id=user.id,
                org_id=org_item.id,
                role=data['roles']
            )
            db.session.add(create_members)
            db.session.commit()
            
            return redirect(url_for('org.get_org_details', org_id=org_id))
        except Exception as e:
            db.session.rollback()
            return render_template("invite_member_form.html", org=org_item, error=str(e)), 500

    return render_template("invite_member_form.html", org=org_item)


@org.route("/delete_members/<int:org_id>/<int:user_id>", methods=['POST'])
@jwt_required()
@check_role_condition()
def delete_members(org_id, user_id):
    org_item = Organization_Repository.get_organization_by_id(org_id)
    user_item = User_Repository.get_user_by_id(user_id)

    if org_item and user_item:
        Member_Repository.delete_members_by_org_id(org_item.id, user_item.id)
    
    return redirect(url_for('org.get_org_details', org_id=org_id))