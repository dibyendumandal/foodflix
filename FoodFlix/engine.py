from flask import current_app, session
import pandas as pd
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Internal functions
from FoodFlix.db import get_db, get_liked, get_disliked

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
        data = pd.read_csv('FoodFlix/static/data/clean_ingredients.csv',
                           header=0)
        data.set_index('recipe_id', inplace=True)

        # Drop recipes that contain keywords from the dietary restrictions
        if restrictions:
            data = (data[~data['ingredients'].str
                                            .contains('|'.join(restrictions))])

        # Put ingredients in a list to be passed to TF-IDF
        ingredients = list(data['ingredients'])

        # Build the TF-IDF Model using 1, 2, and 3-grams on words
        vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 3),
                                     min_df=min_df, stop_words='english',
                                     max_features=512)

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

        recommendations.to_sql(name='recommendations',con=db,
                               if_exists='replace')

        # Store TF-IDF features to database as well
        tfidf_df = pd.DataFrame(X.toarray(), index=data.index)
        tfidf_df.to_sql(name='tfidf', con=db, if_exists='replace')

        return

    def load_trained(self, restrictions):
        """
        Load a previously fit model.

        Parameters
        ==========
        restrictions : list
            List containing strings of dietary restrictions.
        """

        # Read in cleaned data from CSV
        data = pd.read_csv('FoodFlix/static/data/clean_ingredients.csv',
                           header=0)
        data.set_index('recipe_id', inplace=True)

        # Load in the preprocessed similarity data
        sim = (sparse.load_npz('FoodFlix/static/data/similarities.npz')
                     .toarray())

        # Give recipes containing restrictions a similarity of -1
        if restrictions:
            mask = data['ingredients'].str.contains('|'.join(restrictions))
            sim[mask] = -1
            sim[:, mask] = -1

        # Create a DataFrame to hold the recommendations then pass to SQL
        recommendations = pd.DataFrame(index=data.index,
                                       columns=np.arange(n_closest))

        # Get the most similar values
        for idx in range(recommendations.shape[0]):
            # Don't include the first one since it's the similarity with itself
            similar_idx = sim[idx].argsort()[-2:-(n_closest+2):-1]
            recommendations.iloc[idx] = recommendations.index[similar_idx]

        # Store this to a SQL database
        db = get_db()

        print(recommendations.shape)
        recommendations.to_sql(name='recommendations',con=db,
                               if_exists='replace')
        return

    def predict(self, cals_per_day):
        """
        Generate predictions
        """
        # Divide the daily calories into five meals
        cals_per_day /= 5 # 5 meals/day

        # Connect to the database to grab user information
        db = get_db()

        # Get liked and disliked recipes
        liked = get_liked(session.get('user_id'))
        disliked = get_disliked(session.get('user_id'))

        # Grab the TF-IDF features to compute scores
        tfidf_query = 'SELECT * FROM tfidf;'
        tfidf = pd.read_sql(sql=tfidf_query, con=db, index_col='recipe_id')

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
                    'WHERE recipe_id == ? ',
                    (k,)
                ).fetchone()

                # Recommend only recipes around your cal/week goal
                cals = int(recipe_query['calorie_count'].replace('cals',''))
                if cals > cals_per_day-100 and cals < cals_per_day+100:
                    recipes.append(recipe_query)

        return recipes
