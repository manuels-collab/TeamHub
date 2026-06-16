"""full-text search on members with GIN index

Revision ID: f40a79909f37
Revises: 66d7d138cfe3
Create Date: 2026-06-16 10:27:32.535299

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f40a79909f37'
down_revision = '66d7d138cfe3'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE "user"
        ADD COLUMN search_vector tsvector 
        GENERATED ALWAYS AS(
            to_tsvector('english', coalesce(first_name, '') || ' ' || coalesce(last_name, '') || ' ' || coalesce(email, '') || ' ' || coalesce(username, ''))
        )STORED;
        """  
    )
    
    op.execute(
        """
        CREATE INDEX idx_user_search_vector ON "user" USING GIN (search_vector);
        """
    )


def downgrade():
    op.execute(
        """
        DROP INDEX IF EXISTS idx_user_search_vector;
        """
    )
    
    op.execute(
        """
        ALTER TABLE "user" DROP COLUMN IF EXISTS search_vector;
        """
    )