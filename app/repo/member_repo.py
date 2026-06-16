from sqlalchemy import select, delete, func, desc
from ..models.dbModel import Members as Member, db, User, Organisation

class Member_Repository:
    
    @staticmethod
    def create_member(user_id, org_id, role):
        query = select(Member).where(
            Member.user_id == user_id, 
            Member.org_id == org_id
        )
        
        existing_member = db.session.scalars(query).first()
        if existing_member: 
            raise ValueError("Member is already invited to this organization.")
        

        new_member = Member(user_id=user_id, org_id=org_id, role=role)
        return new_member
   


        
    @staticmethod
    def get_member_by_user_and_org(user_id, org_id):
        """
        CRITICAL: Used by roleService.py to evaluate live permissions
        """
        query = select(Member).where(
            Member.user_id == user_id,
            Member.org_id == org_id
        )
        return db.session.scalars(query).first()

        
    @staticmethod
    def delete_members_by_org_id(org_id, user_id):
        user_data = select(User, Member).join(User, Member.user_id == User.id).where(Member.org_id == org_id, Member.user_id == user_id)
        result = db.session.execute(user_data).first()
        if not result:
            return 'No members found for this organization.'
        
        user, member = result
        
        role_string = member.role.value if hasattr(member.role, 'value') else member.role
        
        user_info = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': role_string
        }
        
        try:
            db.session.delete(member)
            db.session.commit()
            return user_info
        except Exception as e:
            db.session.rollback()
            return 'An error occurred on our end. Try again later.'


    @staticmethod
    def get_members_by_id(user_id):
        get_members = select(User, Member).join(User, Member.user_id == User.id).where(Member.user_id == user_id)
        result = db.session.execute(get_members).first()
        if not result:
            return 'No members found for this user.'
        user, member = result
        
        role_string = member.role.value if hasattr(member.role, 'value') else member.role
        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': role_string
        }
    
    @staticmethod
    def get_member_by_name(query, org_id):
        if not query or not query.strip():
            return []
        words = [f"{word.strip()}:*" for word in query.split() if word.strip()]
        tsquery_str = " & ".join(words)

        tsquery = func.to_tsquery('english', tsquery_str)
        rank_expr = func.ts_rank(User.search_vector, tsquery)
        
        stmt = (
            select(User, Member, rank_expr.label('rank'))
            .join(User, Member.user_id == User.id)
            .where(User.search_vector.op('@@')(tsquery)) 
            .where(Member.org_id == org_id)
            .order_by(desc('rank'))
        )
        
        result = db.session.execute(stmt).all()
        
        if not result:
            return []

        members_list = []
        for user, member, rank in result:
            role_string = member.role.value if hasattr(member.role, 'value') else member.role
            members_list.append({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': role_string,
                'rank': rank  
            })
            
        return members_list

    
    @staticmethod
    def get_organisation_members(org_id):
        query = (
            select(Member, User)
            .join(Organisation, Member.org_id == Organisation.id)
            .join(User, Member.user_id == User.id)
            .where(Member.org_id == org_id)
        )  
    
        results = db.session.execute(query).all()
    
        if not results:
            return {"message": "This organisation doesn't have any members yet", "members": []}

        return {
            "message": "Members found",
            "members": [
                {
                    "member_id": member.id,
                    "role": member.role.value if hasattr(member.role, 'value') else member.role,
                    "user_id": user.id,
                    "username": user.username,       
                    "email": user.email      
                }
                for member, user in results  
            ]
        }