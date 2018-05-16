from flask import Flask, jsonify, g
from flask_restful import Api
from flask import abort
from flask import make_response, request, session, flash, redirect, current_app, url_for, render_template
from sqlite3 import dbapi2 as sqlite3
from forms import ItemForm


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
    #return make_response("Hello, world!")
    #return render_template('login.html')
    return redirect(url_for('login'))


# Prolly dont really need an /items route
@app.route("/house/items", methods=["GET"])
def get_items():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        conn = get_db()
        query = conn.execute("SELECT * FROM house")
        rows = query.fetchall()
        return render_template("list.html", rows=rows)


@app.route("/house/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        conn = get_db()
        item_query = conn.execute("SELECT * FROM house WHERE id = {0}".format(item_id))
        rows = item_query.fetchall()

        header_query = conn.execute("SELECT DISTINCT category FROM house")
        rows_header = header_query.fetchall()

        return render_template("details.html", rows=rows, header_rows=rows_header)


@app.route("/house/items/categories/<string:cat>", methods=["GET"])
def get_items_by_category(cat):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        conn = get_db()
        cat_query = conn.execute("SELECT * FROM house WHERE category LIKE '{0}'".format(cat))
        rows = cat_query.fetchall()

        header_query = conn.execute("SELECT DISTINCT category FROM house")
        rows_header = header_query.fetchall()

        return render_template("list.html", rows=rows, header_rows=rows_header)


@app.route("/house/items/categories", methods=["GET"])
def get_categories():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        conn = get_db()
        cats_query = conn.execute("SELECT DISTINCT category FROM house")
        rows_header = cats_query.fetchall()
        return render_template("categories.html", header_rows=rows_header, rows=rows_header)


@app.route('/entries', methods=['GET'])
def entries():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        conn = get_db()
        header_query = conn.execute("SELECT DISTINCT category FROM house")
        rows_header = header_query.fetchall()
        return render_template('add.html', header_rows=rows_header)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        conn = get_db()
        conn.execute('INSERT INTO house (description, room, category, subcategory, whenpurchased, wherepurchased, generacolor, brand, finish, code, pic1, pic2, url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     [request.form['desc'],
                      request.form['room'],
                      request.form['cat'],
                      request.form['sub-cat'],
                      request.form['date-purchased'],
                      request.form['where-purchased'],
                      request.form['color'],
                      request.form['brand'],
                      request.form['finish'],
                      request.form['code'],
                      request.form['photo-1'],
                      request.form['photo-2'],
                      request.form['url']])
        conn.commit()
        flash('New entry was successfully posted')

        return redirect(url_for('entries'))


@app.route('/update/<string:item_id>', methods=['GET', 'POST'])
def update_entry(item_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        conn = get_db()
        conn.execute("UPDATE house SET description = {0}, room = {1}} WHERE id = {3}".format(request.form['desc'], request.form['room'],
                                                                                                 item_id))
        conn.commit()
        flash("Entry for ID '{0}' updated.".format(item_id))
        return redirect(url_for('get_item', item_id=item_id))



@app.route('/delete/<string:item_id>', methods=['GET', 'POST'])
def remove_entry(item_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        conn = get_db()
        conn.execute("DELETE FROM house WHERE id = {0}".format(item_id))
        conn.commit()
        flash("Entry for ID '{0}' deleted.".format(item_id))
        return redirect(url_for('get_categories'))


@app.route('/house/login', methods=['GET', 'POST'])
def login():
    conn = get_db()
    header_query = conn.execute("SELECT DISTINCT category FROM house")
    rows_header = header_query.fetchall()
    error = None

    if session.get('logged_in'):
        return redirect(url_for('get_categories'))
    else:
        if request.method == 'POST':
            if request.form['username'] != "admin": #current_app.config['USERNAME']:
                error = 'Invalid username'
            elif request.form['password'] != "admin": #current_app.config['PASSWORD']:
                error = 'Invalid password'
            else:
                session['logged_in'] = True
                flash('You were logged in')
                return redirect(url_for('get_categories'))
        return render_template('login.html', error=error, header_rows=rows_header)


@app.route('/house/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))


@app.route('/new_item', methods=['GET', 'POST'])
def new_item():
    form = ItemForm(request.form)

    if request.method == 'POST' and form.validate():
        conn = get_db()
        conn.execute(
            'INSERT INTO house (description, room) VALUES (?, ?)',
            [request.form['desc'],
             request.form['room']])
        conn.commit()
        flash('New entry was successfully posted')

    return render_template('new_item.html', form=form)


def save_changes(item, form, new=False):



if __name__ == "__main__":
    app.run(debug=True)