import os
import psycopg2
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify
from fastai.tabular.all import *
from fastai.collab import *


app = Flask(__name__)

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
    connection = None
    try:
        print("Attempting Database Connection...")
        url = "jdbc:postgresql://localhost:5432/ulu_prod"
        # Remove the prefix
        pgsql_url = url.replace("jdbc:postgresql://", "")
        # Split the remaining string into host, port, and database
        host, port_database = pgsql_url.split(":")
        port, database = port_database.split("/")

        user = "ulu_backend"
        password = os.environ.get("DB_PASSWORD")

        connection = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )

        cursor = connection.cursor()

        print("Connected to Database, retrieving Ratings")

        query = "SELECT user, whiskey, rating FROM Rating"

        cursor.execute(query)
        rows = cursor.fetchall()

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=['user', 'whiskey', 'rating'])
        print(df.head())  # Just printing the first few rows
        print("Ratings retrieved, Dataframe created.")
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



#Separation, scikit vs fastai

def getMockData (): #Uses mock data from the Movielens 100k dataset
    ratings = pd.read_csv('assets/ml-100k/u.data', delimiter='\t', header=None, usecols=(0,1,2), names=['user','whiskey','rating'])

    dls = CollabDataLoaders.from_df(ratings, bs=64)
    print("Mock Data Loaded")
    learn = collab_learner(dls, n_factors=50, y_range=(0, 5.5))
    learn.fit_one_cycle(5, 5e-3, wd=0.1)
    print("Learned Model")


# ----------------------------------------------------------- #

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

getMockData()

@app.route('/process', methods=['POST'])
def process_request():
    # Extract the integer from the request. Assuming it's sent as JSON for this example
    print(request)

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    print(data)
    if 'number' not in data:
        return jsonify({"error": "No number provided"}), 400

    number = data['number']

    # Example processing based on the received number
    if number == 1:
        response_data = {"message": "You sent one!"}
    elif number == 2:
        response_data = {"message": "Number two, coming right up!"}
    else:
        response_data = {"message": f"Received {number}, but I'm not sure what to do with it."}

    return jsonify(response_data)


if __name__ == "__main__":
    if df is None:
        app.run(debug=False)
    else:
        print("Data retrival failed, exiting application")