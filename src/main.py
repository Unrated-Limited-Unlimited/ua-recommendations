import psycopg2
import pandas as pd
# from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify
from fastai.tabular.all import *
from fastai.collab import *



app = Flask(__name__)

# ----------------------------------------------------------- #
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

        ratings = pd.DataFrame(rows, columns=['user', 'whiskey', 'rating'])

        ratings['user'] = ratings['user'].astype(int)
        ratings['whiskey'] = ratings['whiskey'].astype(int)
        ratings['rating'] = ratings['rating'].astype(float)

        # Create DataLoaders from the DataFrame
        dls = CollabDataLoaders.from_df(ratings, bs=64, user_name='user', item_name='whiskey', rating_name='rating')

        print("Ratings retrieved, DataLoader created.")
        learn = collab_learner(dls, n_factors=50, y_range=(0, 1))
        learn.fit_one_cycle(5, 5e-3, wd=0.1)
        print("Learned Model")
        return learn, dls, ratings

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



def getMockData (): #Uses mock data from the Movielens 100k dataset
    ratings = pd.read_csv('assets/ml-100k/u.data', delimiter='\t', header=None, usecols=(0,1,2), names=['user','whiskey','rating'])

    ratings = ratings[ratings['whiskey'] >= 100]
    ratings = ratings[ratings['whiskey'] <= 1286]

    dls = CollabDataLoaders.from_df(ratings, bs=64)
    print("Mock Data Loaded")
    learn = collab_learner(dls, n_factors=50, y_range=(0, 5.5))
    learn.fit_one_cycle(5, 5e-3, wd=0.1)
    print("Learned Model")
    return learn, dls, ratings


def get_recommendations2(user_id, dls, learn, df):
    items_already_rated = df[df['user'] == user_id]['whiskey'].unique()
    all_items = df['whiskey'].unique()
    items_to_predict = [item for item in all_items if item not in items_already_rated]

    # Create a DataFrame for predictions
    predict_df = pd.DataFrame({'user': [user_id] * len(items_to_predict), 'whiskey': items_to_predict})

    # Get predictions
    test_dl = dls.test_dl(predict_df)
    predictions = learn.get_preds(dl=test_dl)[0]

    # Combine predictions with item IDs
    recommendations = pd.DataFrame({'whiskey': items_to_predict, 'Prediction': predictions.numpy().flatten()})

    # Sort by predictions to get the top recommended items
    recommendations = recommendations.sort_values(by='Prediction', ascending=False)
    return recommendations.head(10)

# ----------------------------------------------------------- #

routine = 1

if (routine == 0):
    print("Starting Routine 0, getting data from database")
    learn1, dls1, df1 = get_data_from_database()
else:
    print("Starting Routine 1, getting data from mock data")
    learn1, dls1, df1 = getMockData()



print (get_recommendations2(user_id=1, dls=dls1, learn=learn1, df=df1))

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

    recommendations = get_recommendations2(number, dls1, learn1, df1)
    whiskey_ids = recommendations['whiskey'].tolist()
    response_data = {"list": whiskey_ids}

    return jsonify(response_data)

@app.route('/version', methods=['GET'])
def get_version():
    return jsonify("Version 1.2")


if __name__ == "__main__":
    if dls1 is None:
        print("Data retrival failed, exiting application")
    else:
        print("Data retrival completed, starting application")
        app.run(debug=False)