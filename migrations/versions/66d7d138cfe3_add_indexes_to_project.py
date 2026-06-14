"""add_indexes_to_project

Revision ID: 66d7d138cfe3
Revises: e5e7aebd9dbc
Create Date: 2026-06-14 15:48:29.964825

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66d7d138cfe3'
down_revision = 'e5e7aebd9dbc'
branch_labels = None
depends_on = None


def upgrade():
    """Create Index for Membership"""
    
    op.create_index("ix_membership_org_id", "members", ["org_id"])
    op.create_index("ix_membership_user_id", "members", ["user_id"])


def downgrade():
    """Drop Index for Membership"""
    
    op.drop_index("ix_membership_user_id", "members")
    op.drop_index("ix_membership_org_id", "members")
