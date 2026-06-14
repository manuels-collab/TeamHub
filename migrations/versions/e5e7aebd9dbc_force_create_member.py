"""force_create_member

Revision ID: e5e7aebd9dbc
Revises: c54b4d41e1e5
Create Date: 2026-06-12 15:28:07.864392

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5e7aebd9dbc'
down_revision = 'c54b4d41e1e5'
branch_labels = None
depends_on = None


def upgrade():
    import sqlalchemy as sa
    from sqlalchemy.engine import create_engine
    from alembic import op
    
    from dotenv import load_dotenv
    import os
    
    load_dotenv()  # Load environment variables from .env file if present
    
    # 1. Update this connection string with your exact MySQL credentials
    MYSQL_URI = 'SQLALCHEMY_DATABASE_URI'
    mysql_engine = create_engine(MYSQL_URI)
    mysql_metadata = sa.MetaData()
    
    my_sql_table = sa.Table("members", mysql_metadata, autoload_with=mysql_engine)
    
    print("Connecting to MySQL database...")
    
    with mysql_engine.connect() as my_sql_conn:
        member_rows = my_sql_conn.execute(my_sql_table.select()).fetchall()
        
    print(f"DEBUG: Found {len(member_rows)} total rows inside MySQL user table.")
    
    if member_rows:
        clean_data = [dict(rows._mapping) for rows in member_rows] 
        
        
        pg_conn = op.get_bind()       
        
        pg_metadata = sa.MetaData()
        pg_table = sa.Table("members", pg_metadata, autoload_with=pg_conn)
        
        pg_conn.execute(pg_table.insert(), clean_data)
        
        seq_fix = 'SELECT setval(pg_get_serial_sequence(\'user\', \'id\'), COALESCE(MAX(id), 1)) FROM "user";'
        pg_conn.execute(sa.text(seq_fix))
        
        print("Data pipeline executed inside Alembic frame context.")

def downgrade():
    from alembic import op
    import sqlalchemy as sa
    pg_conn = op.get_bind()
    pg_conn.execute(sa.text('TRUNCATE TABLE "members" CASCADE;'))

  