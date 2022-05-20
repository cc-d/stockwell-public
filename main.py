from flask import Flask, render_template, session, flash, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
import json
from time import time
from google_images_search import GoogleImagesSearch

root_path = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + root_path + '/sqlite.db'
app.config['SECRET_KEY'] = 'doesnt-matter'
db = SQLAlchemy(app)

# load the json data
with open(root_path + '/static/data.json', 'r') as f:
    json_data = json.loads(f.read())

# import database models/functions
from models import *

# this is the "before request" function in flask, it runs before every
# request, in this case logging a user out if they have been inactive for
# longer than 60 seconds
@app.before_request
def before_req():
    if 'last_active' not in session:
        session['last_active'] = time()
    else:
        if 'username' in session:
            if 'last_active' in session:
                if session['last_active'] < (time() - 60):
                    return logout(message='login expired')
                else:
                    session['last_active'] = time()
            else:
                session['last_active'] = time()
        else:
            session['last_active'] = time()

@app.route('/')
def render_home():
    """
    Renders the home page, this is a fairly heavy series of database calls which
    I would avoid either by caching, or not running certain queries under certain
    conditions (user not logged in, user is logged in and only needs specific data,
    etc).
    """
    users = db.session.query(User).all()
    words = db.session.query(Word).all()

    # to easily exclude any words that have been, or are being, processed
    processed = [word.text for word in words]

    # I could calculate the required info in jinja2 but I think it's
    # cleaner to calculate the stats here
    stats = {
        'json_count': len(json_data),
        'skipped': len([w for w in words if w.status == 'skipped']),
        'completed': len([w for w in words if w.status == 'completed']),
        'reviewing': len([w for w in words if w.status == 'reviewing']),
    }

    return render_template('home.html', json_data=json_data, users=users,
                                        stats=stats, words=words, processed=processed)

@app.route('/login', methods=['POST'])
def login():
    """
    Registers a new user if they do not exist when a username is provided, otherwise
    logs them in as normal.

    No inputs are verified, all records are case sensitive, for this app it doesn't
    really matter but in a real app I'd obviously handle a ton of input edge cases.
    """
    username = request.form['username']

    # prevent empty input from being submitted
    if not username:
        flash('empty user name')
        return redirect('/')

    # check if username already exists in db (case sensitive)
    db_user = db.session.query(User).filter_by(username=username).first()

    if db_user:
        flash('successfully logged in')
        session.clear()
        session['username'] = db_user.username
        db_user.log_in_out(True)
    else:
        db.session.add(User(username=username, logged_in=True))
        db.session.commit()
        flash('created new user: ' + username)
        session['username'] = username

    return redirect('/')

@app.route('/logout')
def logout(message=None):
    """
    General logout routine, clears session if any exists and clears any 
    words the user is currently reviewing
    """
    # if a user had a valid login, ensure proper logout protocols are followed
    if 'username' in session:
        db_user = db.session.query(User).filter_by(username=session['username']).first()

        if db_user:
            db_user.log_in_out(False)

    session.clear()

    if message:
        flash(message)
    else:
        flash('successfully logged out')

    return redirect('/')

@app.route('/word/<string:word>')
def word_page(word):
    """
    Renders the image grid for an individual word
    """
    # fetch matching word from db if exists
    db_word = db.session.query(Word).filter_by(text=word).first()
    
    # if a record with a matching word does not exist, create a new record
    if not db_word:
        new_word = Word(text=word, reviewer=session['username'])
        db.session.add(new_word)
        db.session.commit()

        flash('added new word ' + word + ' to user ' + session['username'])
        db_word = new_word

    # querys the google search api with the provided word
    images = get_google_images(word)

    return render_template('word.html', word=db_word, images=images)

# I am not checking for input validation to save time
@app.route('/word/<string:word>/<string:action>', methods=['POST'])
def word_action(word, action):
    """
    Handles both the 'skip' and 'select' functionality for processing images
    """

    word = db.session.query(Word).filter_by(text=word).first()

    if action == 'select':
        url = request.form['url']
        img = GoogleImage(text=word.text, url=url)
        word.status = 'completed'
    elif action == 'skip':
        img = GoogleImage(text=word.text, url=None)
        word.status = 'skipped'

    db.session.add(img)
    db.session.add(word)
    db.session.commit()

    print(word.status, word.text, word.reviewer, img.url)
    return redirect('/')

def get_google_images(query, num=10):
    """
    Queries the google search api with the values set in secret.txt
    """
    with open('secret.txt', 'r') as f:
        secrets = f.read().splitlines()

    gis = GoogleImagesSearch(secrets[0], secrets[1])
    search_params = {
        'q': query,
        'num': num
    }
    gis.search(search_params=search_params)
    return gis.results()
