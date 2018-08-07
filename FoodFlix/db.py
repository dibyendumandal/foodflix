import sqlite3
import pandas as pd
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_restrictions(user_id):
    db = get_db()
    try:
        restrictions = db.execute(
            'SELECT restrictions '
            'FROM user '
            'WHERE id = ?',
            (user_id,)
        ).fetchone()['restrictions'].replace(',',' ').split(' ')
    except:
        restrictions = []
    if restrictions == ['']:
        restrictions = []
    return restrictions


def get_liked(user_id):
    db = get_db()
    try:
        liked = db.execute(
            'SELECT liked '
            'FROM user '
            'WHERE id = ?',
            (user_id,)
        ).fetchone()['liked'].split(',')
    except:
        liked = []
    return liked

def get_disliked(user_id):
    db = get_db()
    try:
        disliked = db.execute(
            'SELECT disliked '
            'FROM user '
            'WHERE id = ?',
            (user_id,)
        ).fetchone()['disliked'].split(',')
    except:
        disliked = []
    return disliked


def get_recipes(ingredients,restrictions,user_id):
    db = get_db()
    recipes_query = '''
    SELECT *
    FROM recipes
    WHERE review_count > "1 reviews"
    '''
    query_like = "AND ingredients LIKE '%%%s%%' "
    recipes_query += ''.join([query_like%ingr for ingr in ingredients])
    query_restr = "AND ingredients NOT LIKE '%%%s%%' "
    recipes_query += ''.join([query_restr%restr for restr in restrictions])
    if user_id is not '':
        try:
            liked_str = db.execute(
                'SELECT liked '
                'FROM user '
                'WHERE id = ?',
                (user_id,)
            ).fetchone()['liked']
            recipes_query += 'AND recipe_id IN (%s) '%liked_str
        except:
            print('No user id')
    recipes_query += 'ORDER BY overall_rating DESC '
    try:
        recipes = db.execute(recipes_query).fetchall()
        return recipes
    except:
        return []


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    try:
        recipes = pd.read_csv('FoodFlix/static/data/recipes_all_data.csv')
        recipes.to_sql(name='recipes',con=db)
    except:
        print('Table recipes already exists.')

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

if __name__ == '__main__':
    init_db()
