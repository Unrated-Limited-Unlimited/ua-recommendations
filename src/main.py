import psycopg2
import pandas as pd

url = "jdbc:postgresql://localhost:5432/ulu_prod"
# Remove the prefix
pgsql_url = url.replace("jdbc:postgresql://", "")
# Split the remaining string into host, port, and database
host, port_database = pgsql_url.split(":")
port, database = port_database.split("/")


user = "ulu_backend"
password = "${DB_PASSWORD:}" #Use environment variable or similar to insert the actuall passwoord


try:
    connection = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
except psycopg2.OperationalError as e:
    print(f"Error connecting to the database: {e}")
    # Handle the error or exit

try:
    cursor = connection.cursor()

    query = "SELECT user, whiskey, rating FROM Rating"

    cursor.execute(query)
    rows = cursor.fetchall()

    # Convert to DataFrame
    df = pd.DataFrame(rows, columns=['user', 'whiskey', 'rating'])
    print(df.head())  # Just printing the first few rows

except psycopg2.Error as e:
    print(f"Error executing query: {e}")
    # Handle query error
finally:
    # Close the cursor and connection
    if connection is not None:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")