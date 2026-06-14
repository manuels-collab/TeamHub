"""force_push_organisations

Revision ID: c54b4d41e1e5
Revises: bf10fe977240
Create Date: 2026-06-12 14:05:12.498325

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c54b4d41e1e5'
down_revision = 'bf10fe977240'
branch_labels = None
depends_on = None


def upgrade():
    import sqlalchemy
    from sqlalchemy.engine import create_engine
    from alembic import op
    
    from dotenv import load_dotenv
    import os
    
    load_dotenv()  # Load environment variables from .env file if present
    
    # 1. Update this connection string with your exact MySQL credentials
    MYSQL_URI = 'SQLALCHEMY_DATABASE_URI'
    
    my_sql_engine = create_engine(MYSQL_URI)
    sql_metadata = sqlalchemy.MetaData()
    
    
    print('Connecting to MYSQL Database')
    my_sql_org_table = sqlalchemy.Table("org", sql_metadata, autoload_with=my_sql_engine)
    
    
    with my_sql_engine.connect() as sql_connect:
        org_rows = sql_connect.execute(my_sql_org_table.select()).fetchall()
        
        
    print(f"We found a total of {len(org_rows)} in the Organisation table")


    if org_rows:
        org_to_insert = [dict(row._mapping) for row in org_rows]
        
        pg_conn = op.get_bind()
        print(f"DEBUG: Piping {len(org_to_insert)} users into POSTGRESS via Alembic channel")
        
        pg_meta = sqlalchemy.MetaData()
        pg_org_table = sqlalchemy.Table("org", pg_meta, autoload_with=pg_conn)
        
        pg_conn.execute(pg_org_table.insert(), org_to_insert)
        
        seq_fix = 'SELECT setval(pg_get_serial_sequence(\'org\', \'id\'), COALESCE(MAX(id), 1)) FROM "org";'
        pg_conn.execute(sa.text(seq_fix))
        
        print("Data pipeline executed inside Alembic frame context.")

def downgrade():
    from alembic import op
    import sqlalchemy as sa
    pg_conn = op.get_bind()
    pg_conn.execute(sa.text('TRUNCATE TABLE "org" CASCADE;'))
