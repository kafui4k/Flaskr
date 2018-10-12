import os
import sqlite3

from flask import (Flask, request, session, g, redirect, url_for, abort, render_template, flash)

app = Flask(__name__) #Create the applications instance
app.config.from_object(__name__) #load configurations from thsi 'flaskr.py' file

#Load deafult config and override config from an environment variable
app.config.update(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY = 'b_5#y2L"F4Q8zn\xec]/',
    USERNAME = 'admin',
    PASSWORD = 'default'
)

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """connects to the specific databse"""

    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()

    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())

    db.commit()  

@app.cli.command('init_db')
def initdb_command():
    """Initializes the database"""

    init_db()
    print('Initialized the Database')


def get_db():
    """Opens a new dataase connection if there is none
    yet current open for the application context"""

    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):    
    """Closes the database again at the end of the request"""

    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('SELECT title, text FROM entries ORDER BY id DESC')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()        
    db.execute('INSERT INTO entries (title, text) VALUES (?, ?)', [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid Password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)            

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


