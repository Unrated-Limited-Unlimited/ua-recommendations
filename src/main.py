import psycopg2
import pandas as pd

url = "jdbc:postgresql://localhost:5432/ulu_prod"
# Remove the prefix
pgsql_url = url.replace("jdbc:postgresql://", "")
# Split the remaining string into host, port, and database
host, port_database = pgsql_url.split(":")
port, database = port_database.split("/")


user = "ulu_backend"
password = "your_password"


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
    # Cursor to execute queries
    cursor = connection.cursor()

    # Your SQL query
    query = "SELECT UserID, WhiskeyID, Rating FROM Ratings"

    # Execute the query
    cursor.execute(query)

    # Fetch the results
    rows = cursor.fetchall()

    # Optional: Convert to DataFrame
    df = pd.DataFrame(rows, columns=['UserID', 'WhiskeyID', 'Rating'])
    print(df.head())  # Just printing the first few rows as an example

except psycopg2.Error as e:
    print(f"Error executing query: {e}")
    # Handle query error
finally:
    # Close the cursor and connection
    if connection is not None:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")