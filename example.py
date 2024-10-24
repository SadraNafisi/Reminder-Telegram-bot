from sqlalchemy import create_engine, MetaData

# Create your database engine
url = 'database_url'
engine = create_engine(url)

# Create a MetaData instance
metadata = MetaData()

# Reflect the database
metadata.reflect(bind=engine)

# List the table names
print(metadata.tables.keys())