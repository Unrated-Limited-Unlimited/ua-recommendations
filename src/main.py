import psycopg2
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import socket
import json


# ----------------------------------------------------------- #
def get_recommendations(user_id, user_similarity_df, user_item_matrix, top_n=10):
    # Get similarity scores for the target user with all other users
    sim_scores = user_similarity_df[user_id]

    # Exclude the target user's own similarity score
    sim_scores = sim_scores.drop(user_id)

    # Multiply the similarity scores by the user-item ratings matrix (excluding the target user's row)
    sim_scores_matrix = user_item_matrix.drop(user_id).mul(sim_scores, axis=0)

    # Sum the weighted ratings for each whiskey
    weighted_sum_ratings = sim_scores_matrix.sum(axis=0)

    # Get the count of non-zero ratings (to handle division by zero)
    non_zero_ratings = (sim_scores_matrix != 0).sum(axis=0)

    # Calculate the average weighted rating for each whiskey
    avg_weighted_ratings = weighted_sum_ratings / non_zero_ratings

    # Filter out whiskeys the user has already rated
    rated_whiskeys = user_item_matrix.loc[user_id].nonzero()[0]
    recommendations = avg_weighted_ratings.drop(index=rated_whiskeys).nlargest(top_n)

    return recommendations


def get_data_from_database():
    try:
        url = "jdbc:postgresql://localhost:5432/ulu_prod"
        # Remove the prefix
        pgsql_url = url.replace("jdbc:postgresql://", "")
        # Split the remaining string into host, port, and database
        host, port_database = pgsql_url.split(":")
        port, database = port_database.split("/")

        user = "ulu_backend"
        password = "${DB_PASSWORD:}"  # Use environment variable or similar to insert the actuall password

        connection = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )

        cursor = connection.cursor()

        query = "SELECT user, whiskey, rating FROM Rating"

        cursor.execute(query)
        rows = cursor.fetchall()

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=['user', 'whiskey', 'rating'])
        print(df.head())  # Just printing the first few rows

        return df

    except psycopg2.OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None

    except psycopg2.Error as e:
        print(f"Error executing query: {e}")
        return None

    finally:
        # Close the cursor and connection
        if connection is not None:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
# ----------------------------------------------------------- #


def main():
    df = get_data_from_database()

    if df is None:
        print("Data retrieval failed.")
    else:
        print("Starting machine learning sequence")
        # Convert the ratings DataFrame into a user-item matrix
        user_item_matrix = df.pivot(index='user', columns='whiskey', values='rating').fillna(0)
        user_similarity = cosine_similarity(user_item_matrix)
        user_similarity_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)
        print("sequence complete... entering server mode")
        host = 'localhost'
        port = 65432
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()
            print(f"Server listening on {host}:{port}")

            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        # Assuming data is sent as a JSON string with 'user_id'
                        request_data = json.loads(data.decode('utf-8'))
                        user_id = request_data['user_id']
                        # top_n = request_data.get('top_n', 5)

                        recommendations = get_recommendations(user_id, user_similarity_df, user_item_matrix)

                        # Send back the recommendations as a JSON string
                        conn.sendall(json.dumps(recommendations).encode('utf-8'))


main()
