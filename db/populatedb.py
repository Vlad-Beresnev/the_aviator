import os
import sys
import mysql.connector
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

conn = mysql.connector.connect(
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME"),
)

# Open the SQL file and read the contents
with open('lp_project_base.sql', 'r') as sql_file:
    sql_script = sql_file.read()

# Split the SQL script into separate queries
queries = sql_script.split(';')


# Create a cursor object
cursor = conn.cursor()

# Execute each query
for query in queries:
    cursor.execute(query)
    cursor.fetchall() # fetch any results, even if it's just an empty result set

# Commit the changes
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()
