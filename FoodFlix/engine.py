from flask import current_app
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Internal functions
from FoodFlix.db import get_db

class FoodFlixEngine(object):

    def train(self, restrictions, min_df=10, n_closest=3):
        """
        Fit the engine model to the given data

        Parameters
        ==========
        restrictions : list
            List containing strings of dietary restrictions.
        min_df : int
            Minimum number of occurences of a given ingredient in recipes.
        n_closest : int
            The number of closest recipes.
        """

        # Read in cleaned data from CSV
        data = pd.read_csv('FoodFlix/static/clean_ingredients.csv',
                           header=0)
        data.set_index('recipe_id', inplace=True)

        # Drop recipes that contain keywords from the dietary restrictions
        data = data[~data['ingredients'].str.contains('|'.join(restrictions))]

        # Put ingredients in a list to be passed to TF-IDF
        ingredients = list(data['ingredients'])

        # Build the TF-IDF Model using 1, 2, and 3-grams on words
        vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 3),
                                     min_df=min_df, stop_words='english')

        # Fit the TF-IDF model using the given data
        X = vectorizer.fit_transform(ingredients)

        # Calculate the similarity
        similarity = cosine_similarity(X)

        # Create a DataFrame to hold the recommendations then pass to SQL
        recommendations = pd.DataFrame(index=data.index,
                                       columns=np.arange(n_closest))

        # Get the most similar values
        for idx in range(recommendations.shape[0]):
            # Don't include the first one since it's the similarity with itself
            similar_idx = similarity[idx].argsort()[-2:-(n_closest+2):-1]
            recommendations.iloc[idx] = recommendations.index[similar_idx]

        # Store this to a SQL database
        db = get_db()

        # TODO kjb: maybe do this without replacement...
        recommendations.to_sql(name='recommendations',con=db,
                               if_exists='replace')
        return

    def predict(self, liked):
        """
        Generate predictions

        liked : list
            List containing recipe_id for each recipe that a user liked.
        """

        # Connect to the database to grab user information
        db = get_db()

        # Create a container to hold recommended recipes
        recipes = []

        # Iterate over all of the recipes that a user has liked
        for recipe in liked:
            rec_query = db.execute(
                'SELECT * '
                'FROM recommendations '
                'WHERE recipe_id == ?',
                (recipe,)
            ).fetchone()

            # Skip the first one, since it's the item we are comparing to
            for k in rec_query[1:]:
                recipe_query = db.execute(
                    'SELECT * '
                    'FROM recipes '
                    'WHERE recipe_id == ?',
                    (k,)
                ).fetchone()

                recipes.append(recipe_query)

        return recipes
