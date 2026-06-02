from sqlalchemy import select, update, delete
from ..models.dbModel import Organisation, db, User

class Organization_Repository:
    @staticmethod
    def create_organization(name, slug, description, owner_id):
        new_org = Organisation(name=name, slug=slug, description=description, owner_id=owner_id)
        try:
            db.session.add(new_org)
            db.session.commit()
            return new_org
        except Exception as e: 
            db.session.rollback()
            return 'An error occurred on our end. Try again later.'
        
        
    def get_organizations(user_id):

        query = select(Organisation).where(Organisation.owner_id == user_id)
        
        orgs = db.session.scalars(query).all() 
        return orgs
    
    def get_organization_by_id(org_id):
        query = select(Organisation).where(Organisation.id == org_id)
        org = db.session.scalars(query).first()
        return org
    
