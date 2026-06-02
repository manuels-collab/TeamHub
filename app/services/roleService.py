# app/services/roleService.py
from functools import wraps
from flask import render_template, request, redirect, url_for
from flask_jwt_extended import get_jwt_identity
from app.repo.member_repo import Member_Repository
from app.repo.org_repo import Organization_Repository
from app.models.dbModel import RolesEnum

def check_role_condition():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            org_id = kwargs.get('org_id')
            user_id = get_jwt_identity()
            
            if not org_id or not user_id:
                return redirect(url_for('org.get_orgs'))

            member = Member_Repository.get_member_by_user_and_org(user_id=int(user_id), org_id=int(org_id))
            
            has_permission = False
            if member and member.role:
                role_value = member.role.value if hasattr(member.role, 'value') else member.role
                if role_value in ['admin', 'owner'] or member.role in [RolesEnum.admin, RolesEnum.owner]:
                    has_permission = True

            if not has_permission:
                org_item = Organization_Repository.get_organization_by_id(org_id)
                result_data = Member_Repository.get_organisation_members(org_id)
                members_list = result_data.get("members", []) if isinstance(result_data, dict) else result_data
                
                return render_template(
                    "org_details.html", 
                    organization=org_item, 
                    members=members_list,
                    error="Unauthorized access: You must be an organization Admin or Owner to perform that task."
                ), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator