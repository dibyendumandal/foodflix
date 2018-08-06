from flask import (
        Blueprint, flash, g, redirect, render_template, request, url_for, session
    )
from werkzeug.exceptions import abort, BadRequestKeyError

from FoodFlix.auth import login_required
from FoodFlix.db import (get_db, get_recipes, get_liked, get_disliked,
    get_restrictions)
from FoodFlix.engine import FoodFlixEngine
from FoodFlix.util import calc_bmi, calc_bmr, calc_calperday

import re

bp = Blueprint('blog', __name__)

@bp.route('/profile', methods=('GET', 'POST'))
@login_required
def profile():
    db = get_db()
    if request.method == 'POST':
        try:
            bmi = calc_bmi(request.form['weight'],request.form['feet'],request.form['inches'])
            bmr = calc_bmr(request.form['gender'],
                           request.form['age'],
                           request.form['weight'],
                           request.form['feet'],
                           request.form['inches'])
            cals_per_day = calc_calperday(request.form['activity'],
                                          request.form['goal'],
                                          bmr)
        except Exception as err:
            print( type(err) )
            bmi = '--'
            bmr = '--'
            cals_per_day = '--'
        db.execute(
            'UPDATE user '
            'SET fullname=?, '
            'gender=?, '
            'age=?, '
            'weight=?, '
            'feet=?, '
            'inches=?, '
            'activity=?, '
            'goal=?, '
            'bmi=?, '
            'bmr=?, '
            'cals_per_day=?, '
            'restrictions=?, '
            'is_config=?',
            (request.form['fullname'],
             request.form['gender'],
             request.form['age'],
             request.form['weight'],
             request.form['feet'],
             request.form['inches'],
             request.form['activity'],
             request.form['goal'],
             bmi,
             bmr,
             cals_per_day,
             request.form['restrictions'],
             1)
            )
        db.commit()
        flash('Saved!','success')
        return redirect(url_for('blog.profile'))
    else:
        user_info = db.execute(
            'SELECT * '
            'FROM user '
            'WHERE id = ?',
            (session.get('user_id'),)
        ).fetchone()
        return render_template('profile.html', user=user_info)


@bp.route('/', methods=('GET','POST'))
def browse():
    db = get_db()

    liked = get_liked( session.get('user_id') )
    disliked = get_disliked( session.get('user_id') )
    restrictions = get_restrictions( session.get('user_id') )

    ingredients = []

    if request.method == 'POST':
        try:
            respose = request.form['recipe_id']
            # Parse out the type of button pressed (like or dislike)
            vote = re.search('[a-z]+', respose).group()

            # Parse out the recipe id from the response
            recipe_id = re.search('[0-9]+', respose).group()

            if vote == 'like':
                # Unlike if you click the button and it's already liked
                if recipe_id in liked:
                    liked.remove(recipe_id)
                # Like the recipe
                else:
                    liked.append(recipe_id)

                    # Un-dislike if it is disliked
                    if recipe_id in disliked:
                        disliked.remove(recipe_id)
            else:
                # Un-dislike if you click the button and it's already disliked
                if recipe_id in disliked:
                    disliked.remove(recipe_id)
                # Dislike the recipe
                else:
                    disliked.append(recipe_id)

                    # Unlike if it is liked
                    if recipe_id in liked:
                        liked.remove(recipe_id)

            db.execute(
                'UPDATE user '
                'SET liked=?',
                (','.join(liked),)
            )
            db.execute(
                'UPDATE user '
                'SET disliked=?',
                (','.join(disliked),)
            )
            db.commit()
            return redirect(url_for('blog.browse',_anchor=recipe_id))

        except BadRequestKeyError:
            print('No recipe_id key')

        try:
            ingredients = request.form['ingredients'].split(' ')

        except BadRequestKeyError:
            print('No Ingredients key')

    recipes = get_recipes(ingredients,restrictions,'')
    return render_template('browse.html', recipes=recipes, liked=liked,
        disliked=disliked, keywords=ingredients, restrictions=restrictions)

@bp.route('/favs', methods=('GET','POST'))
def favs():
    db = get_db()

    liked = get_liked( session.get('user_id') )
    restrictions = get_restrictions( session.get('user_id') )

    ingredients = []
    
    if request.method == 'POST':
        try:
            recipe_id = request.form['recipe_id']
            if str(recipe_id) in liked:
                liked.remove( str(recipe_id) )
            else:
                liked.append( str(recipe_id) )
            db.execute(
                'UPDATE user '
                'SET liked=?',
                (','.join(liked),)
            )
            db.commit()
            return redirect(url_for('blog.browse',_anchor=recipe_id))
        except BadRequestKeyError:
            print('No recipe_id key')
        try:
            ingredients = request.form['ingredients'].split(' ')
        except BadRequestKeyError:
            print('No Ingredients key')

    recipes = get_recipes(ingredients,restrictions,session.get('user_id'))
    return render_template('browse.html', recipes=recipes, liked=liked, keywords=ingredients, restrictions=restrictions)


@bp.route('/recommender', methods=('GET', 'POST'))
@login_required
def recommender():
    MIN_LIKED_RECIPES = 3

    # Connect to the database
    db = get_db()

    # Get data on what the user has liked so far
    user_query = db.execute(
        'SELECT * '
        'FROM user '
    ).fetchone()

    # Pull information on what the user likes to use in the engine
    try:
        liked_str = user_query['liked']
        liked = liked_str.split(',')
    except:
        liked = []

    if len(liked) < MIN_LIKED_RECIPES:
        flash(f'You need to like at least {MIN_LIKED_RECIPES} recipes to get '
              'recommendations', 'danger')
        recipes = []
        return render_template("browse.html",recipes=recipes)

    # Get any dietary restrictions to include in the recommendation
    restriction_query = db.execute(
        'SELECT restrictions '
        'FROM user '
    ).fetchone()

    restrictions = restriction_query['restrictions'].split()

    # Build the food recommender engine and train
    engine = FoodFlixEngine()
    engine.train(restrictions=restrictions)

    # Pull some recipe recommendations
    recipes = engine.predict(liked=liked, cals_per_day=user_query['cals_per_day'] )

    return render_template("browse.html",recipes=recipes)
