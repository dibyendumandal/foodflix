from flask import current_app, session
import pandas as pd
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random
from FoodFlix.db import get_recipes

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

        # Store this to a SQL database
        db = get_db()

        # Store TF-IDF features to database as well
        tfidf_df = pd.DataFrame(X.toarray(), index=data.index)
        tfidf_df.to_sql(name='tfidf', con=db, if_exists='replace')

        return

    def predict(self, cals_per_day, w_like=1.5, w_dislike=0.3, n_closest=4, add_random=False):
        """
        Generate predictions

        Parameters
        ==========
        cals_per_day : float
            Total recommended calories per day for a user.
        w_like : float
            Weighting for liked recipes in computing recommendations.
        w_dislike : float
            Weighting for disliked recipes in computing recommendations.
        n_closest : int
            Number of recommended recipes 
        add_random : bool
            Whether including a random suggestion for testing
        """
        # Divide the daily calories into five meals
        cals_per_day /= 5

        # Connect to the database to grab user information
        db = get_db()

        # Get liked and disliked recipes
        liked = get_liked(session.get('user_id'))
        disliked = get_disliked(session.get('user_id'))

        # The TF-IDF db uses recipe_id as the index as integers...
        # TODO kjb: make all recipe_id indices either string or integer
        liked = [int(l) for l in liked]
        disliked = [int(l) for l in disliked]

        # Grab the TF-IDF features to compute scores
        tfidf_query = 'SELECT * FROM tfidf;'
        tfidf = pd.read_sql(sql=tfidf_query, con=db, index_col='recipe_id')

        # Grab the feature vectors for the liked and disliked recipes
        likes = tfidf.loc[liked]
        dislikes = tfidf.loc[disliked]

        # Compute the Rocchio topic
        topic = self.compute_rocchio_topic(likes, dislikes, w_like, w_dislike)

        # Find recipes similar to the Rocchio topic
        similarity = cosine_similarity(np.atleast_2d(topic), tfidf)
        similarity = pd.Series(similarity[0], index=tfidf.index)

        recommendations = similarity.sort_values(ascending=False)
        recommendations = list(recommendations.index)

        # Create a container to hold recommended recipes
        recipes = []
        n_recs = 0
        for rec in recommendations:
            recipe_query = db.execute(
                'SELECT * '
                'FROM recipes '
                'WHERE recipe_id == ? ',
                (rec,)
            ).fetchone()

            # Only recommend things that you don't already like
            if recipe_query['recipe_id'] not in liked:

                recipe_dict = dict( recipe_query ) #convert to dict to allow addition of elements
                recipe_dict['generator'] = 'Recommender TF-IDF'
                # # Recommend only recipes around your cal/week goal
                # cals = int(recipe_query['calorie_count'].replace('cals',''))
                # if cals > cals_per_day * 0.8 and cals < cals_per_day * 1.2:
                recipes.append(recipe_dict)
                n_recs+=1

            if n_recs >= n_closest:
                break

        # Include random suggestion if enabled
        if add_random:
            # Get all recipes from DB
            all_recipes = get_recipes('','','')
            recipe_rand = dict( random.choice(all_recipes) )
            recipe_rand['generator'] = 'Random'
            recipes.append( recipe_rand )

        # Shuffle around
        random.shuffle(recipes)

        return recipes

    def compute_rocchio_topic(self, like, dislike, w_like, w_dislike):
        """
        Compute the Rocchio topic. This weights what the user likes and dislikes
        to generate recommendations.

        Parameters
        ==========
        like : DataFrame
            DataFrame containing TF-IDF features of liked recipes.
        dislike : DataFrame
            DataFrame containing TF-IDF features of disliked recipes.
        w_like : float
            Weighting for liked recipes in computing recommendations.
        w_dislike : float
            Weighting for disliked recipes in computing recommendations.

        Returns
        =======
        rocchio_topic : array
            Array containing recommended recipe.
        """
        n_features = like.shape[1]

        # Get the mean value of the liked recipes
        topic_like = like.mean(axis=0)

        # Account for the case where the user doesn't dislike anything
        if len(dislike) == 0:
            topic_dislike = np.zeros(n_features)
        # Otherwise compute the mean of what is disliked
        else:
            topic_dislike = dislike.mean(axis=0)

        # Compute the Rocchio topic
        rocchio_topic = w_like * topic_like - w_dislike * topic_dislike

        return rocchio_topic.values
