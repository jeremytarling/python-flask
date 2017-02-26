# for flask webapp
from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from .forms import LoginForm
from .models import User
# for 6 music now playing
import urllib.request
import json


# login shizz

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user



# front page
@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    posts = [  # fake array of posts
        { 
            'author': {'nickname': 'John'}, 
            'body': 'Beautiful day in Portland!' 
        },
        { 
            'author': {'nickname': 'Susan'}, 
            'body': 'The Avengers movie was so cool!' 
        },
        {
        	'author': {'nickname': 'The Duke of Kent'},
        	'body': 'They don\'t like it up \'em'
        }
    ]
    return render_template("index.html",
                           title='Home',
                           user=user,
                           posts=posts)


# more login shizz
@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html', 
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])


@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# 6 music now playing 

@app.route('/now_playing')
def now_playing_on_6_music():
    # fetch data from BBC Radio API
    page = urllib.request.urlopen("http://polling.bbc.co.uk/radio/realtime/bbc_6music.json")
    # turn the HTTPResponse object into a string
    text = page.read().decode("utf8")
    # parse the string as JSON into a dictionary (hash)
    data = json.loads(text)
    # sometimes the musicbrainz_artist hash is missing so we need 2 template versions
    if "musicbrainz_artist" in data["realtime"]: 
        return render_template("now_playing_on_6.html",
                                title='now playing on BBC 6 music',
                                track=data["realtime"]["title"],
                                artist=data["realtime"]["artist"],
                                version_pid = data["realtime"]["version_pid"],
                                musicbrainz_artist = data["realtime"]["musicbrainz_artist"]["id"]
                                )
    else:
        return render_template("now_playing_on_6.html",
                                title='now playing on BBC 6 music',
                                track=data["realtime"]["title"],
                                artist=data["realtime"]["artist"],
                                version_pid = data["realtime"]["version_pid"],
                                musicbrainz_artist = "not available"                        
                                )

@app.route('/tarot')
def tarot():
    return render_template("tarot.html")




