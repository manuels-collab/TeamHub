from flask import Blueprint, request, render_template, redirect, url_for, abort, jsonify
from app.repo.member_repo import Member_Repository
from app.repo.org_repo import Organization_Repository
from app.repo.user_repo import User_Repository
from app.services.AuthService import AuthService
from app.models.dbModel import Members
from app.services.roleService import check_role_condition
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from app.extensions import db
import base64
from app.services import cacheService


org = Blueprint("org", __name__, url_prefix="/orgs")

def encode_cursor(entity_id: int):
    return base64.urlsafe_b64encode(str(entity_id).encode()).decode()


def decode_cursor(token: str):
    try:
        return int(base64.urlsafe_b64decode(token.encode()).decode())
    except Exception as e:
        abort(400, description=f"Invalid cursor token: {e}")


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

    cursor_token = request.args.get("cursor", None)
    try:
        limit = int(request.args.get("limit", 20))
        if limit < 1 or limit > 100:
            limit = 20
    except ValueError:
        limit = 20


    cache_key = f"org:{org_id}:members:cursor_{cursor_token}:limit_{limit}"

    cached_data = cacheService.get_cache(cache_key)
    if cached_data:
        return render_template(
            "org_details.html", 
            organization=org_item, 
            members=cached_data["members"], 
            next_cursor=cached_data["next_cursor"],
            has_more=cached_data["has_more"]
        )

    query = db.session.query(Members).filter(Members.org_id == org_id).order_by(Members.id.asc())
    
    if cursor_token:
        decoded_id = decode_cursor(cursor_token)
        query = query.filter(Members.id > decoded_id)
    
    results = query.limit(limit + 1).all()
        
    has_more = len(results) > limit
    db_members = results[:limit]

    next_cursor = None
    if db_members and has_more:
        next_cursor = encode_cursor(db_members[-1].id)


    serialized_members = [member.to_dict() for member in db_members]

    data_to_cache = {
        "members": serialized_members,
        "next_cursor": next_cursor,
        "has_more": has_more
    }

    cacheService.set_cache(cache_key, data_to_cache, 60)

    return render_template(
        "org_details.html", 
        organization=org_item, 
        members=serialized_members, 
        next_cursor=next_cursor,
        has_more=has_more
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
            
            cacheService.delete_cache(f"org:{org_id}:members:*")
            
            return redirect(url_for('org.get_org_details', org_id=org_id))
        except Exception as e:
            db.session.rollback()
            return render_template("invite_member_form.html", org=org_item, error=str(e)), 500

    return render_template("invite_member_form.html", org=org_item)



@org.route('/orgs/<int:org_id>/members/search', methods=['GET'])
@jwt_required()
def get_members_search(org_id):
    query = request.args.get('q', '').strip()
    
    members = [] 
    
    cache_key = f"org:{org_id}:members:{query}"
    
    cached_members = cacheService.get_cache(cache_key)
    if cached_members:
        return render_template('search_members.html', members=cached_members)
    
    data_to_cache = [member.to_dict() for member in members]
    cacheService.set_cache(cache_key, data_to_cache, 60)
    
    if query:
        members = Member_Repository.get_member_by_name(query, org_id)
        
    return render_template('search_members.html', members=members)


@org.route("/delete_members/<int:org_id>/<int:user_id>", methods=['POST'])
@jwt_required()
@check_role_condition()
def delete_members(org_id, user_id):
    org_item = Organization_Repository.get_organization_by_id(org_id)
    user_item = User_Repository.get_user_by_id(user_id)

    if org_item and user_item:
        Member_Repository.delete_members_by_org_id(org_item.id, user_item.id)
        cacheService.delete_cache(f"org:{org_id}:members:*")
    return redirect(url_for('org.get_org_details', org_id=org_id))