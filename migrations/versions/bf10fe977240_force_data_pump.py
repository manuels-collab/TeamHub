"""force_data_pump

Revision ID: bf10fe977240
Revises: 
Create Date: 2026-06-12 13:39:00.268876

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf10fe977240'
down_revision = None
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
    
    # Connect to MySQL engine to read the records
    mysql_engine = create_engine(MYSQL_URI)
    mysql_meta = sa.MetaData()
    
    print("Connecting to MySQL database...")
    mysql_user_table = sa.Table('user', mysql_meta, autoload_with=mysql_engine)
    
    with mysql_engine.connect() as mysql_conn:
        user_rows = mysql_conn.execute(mysql_user_table.select()).fetchall()
        
    print(f"DEBUG: Found {len(user_rows)} total rows inside MySQL user table.")
    
    if user_rows:
        # Convert rows cleanly to dictionaries
        users_to_insert = [dict(row._mapping) for row in user_rows]
        
        # 2. Extract the active transaction connection channel from Alembic
        pg_conn = op.get_bind()
        print(f"DEBUG: Piping {len(users_to_insert)} users into PostgreSQL via Alembic channel...")
        
        # Reflect PostgreSQL target structure dynamically using Alembic's active bind channel
        pg_meta = sa.MetaData()
        pg_user_table = sa.Table('user', pg_meta, autoload_with=pg_conn)
        
        # Execute the bulk insertion through Alembic's open connection channel
        pg_conn.execute(pg_user_table.insert(), users_to_insert)
        
        # 3. Explicitly reset the auto-increment sequence inside the same block
        seq_fix = 'SELECT setval(pg_get_serial_sequence(\'user\', \'id\'), COALESCE(MAX(id), 1)) FROM "user";'
        pg_conn.execute(sa.text(seq_fix))
        
        print("Data pipeline executed inside Alembic frame context.")

def downgrade():
    from alembic import op
    import sqlalchemy as sa
    pg_conn = op.get_bind()
    pg_conn.execute(sa.text('TRUNCATE TABLE "user" CASCADE;'))
