from flask import Flask, jsonify, g
from flask_restful import Api
from flask import abort
from flask import make_response, request, session, flash, redirect, current_app, url_for, render_template
from sqlite3 import dbapi2 as sqlite3


app = Flask(__name__)

app.config.update(dict(
        DATABASE=r"C:/Projects/Chad/House/house.db",
        DEBUG=True,
        SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/',
        USERNAME='admin',
        PASSWORD='admin'
    ))

api = Api(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(current_app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.route("/house", methods=["GET"])
def get_home():
    return make_response("Hello, world!")


@app.route("/house/items", methods=["GET"])
def get_items():
    conn = get_db()
    query = conn.execute("SELECT * FROM house")
    rows = query.fetchall()
    return render_template("list.html", rows=rows)


@app.route("/house/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    conn = get_db()
    item_query = conn.execute("SELECT * FROM house WHERE id = {0}".format(item_id))
    rows = item_query.fetchall()
    return render_template("list.html", rows=rows)


@app.route("/house/items/categories/<string:cat>", methods=["GET"])
def get_items_by_category(cat):
    conn = get_db()
    cat_query = conn.execute("SELECT * FROM house WHERE category LIKE '{0}'".format(cat))
    rows = cat_query.fetchall()
    return render_template("list.html", rows=rows)


@app.route("/house/items/categories", methods=["GET"])
def get_categories():
    conn = get_db()
    cats_query = conn.execute("SELECT DISTINCT category FROM house")
    rows = cats_query.fetchall()
    return render_template("categories.html", rows=rows)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    conn = get_db()
    conn.execute('insert into house (room, category) values (?, ?)',
                 [request.form['room'], request.form['cat']])
    conn.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('get_categories'))


@app.route('/house/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != "admin": #current_app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != "admin": #current_app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('get_categories'))
    return render_template('login.html', error=error)


@app.route('/house/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('get_home'))


if __name__ == "__main__":
    app.run(debug=True)