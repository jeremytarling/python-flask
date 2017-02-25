# for flask webapp
from flask import render_template, flash, redirect
from app import app
# for the WTF form
from .forms import LoginForm
# for 6 music now playing
import urllib.request
import json


@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Miguel'}  # fake user
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


# login formx

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for OpenID="%s", remember_me=%s' %
          (form.openid.data, str(form.remember_me.data)))
        return redirect('/index')
    return render_template('login.html', 
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])


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

