import sqlite3
from flask import Flask, g, render_template, flash, redirect, url_for, session, logging, request
from datetime import date, datetime
from wtforms import Form, StringField, validators

app = Flask(__name__)
DATABASE = 'user.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

class formReg(Form):
  first_name = StringField('First Name', [validators.length(min=1, max=50)])
  last_name = StringField('Last Name', [validators.length(min=1, max=50)])
  address1 = StringField('Address 1', [validators.length(min=1, max=95)])
  address2 = StringField('Address 2')
  city = StringField('City', [validators.length(min=1, max=35)])
  state = StringField('State', [validators.length(min=1, max=2)])
  zipCode = StringField('Zip Code', [validators.length(min=5, max=9)])
  country = StringField('Country', [validators.length(min=1, max=2)])

@app.route('/', methods=['GET', 'POST'])
def index():
    form = formReg(request.form)
    if request.method == 'POST' and form.validate():
      fn = form.first_name.data
      ln = form.last_name.data
      add1 = form.address1.data
      add2 = form.address2.data
      city = form.city.data
      state = form.state.data
      zc = form.zipCode.data
      country = form.country.data

      today = date.today()

      #Get the database and insert into the table
      conn = get_db()
      c = conn.cursor()
      c.execute("INSERT INTO USER (first_name, last_name, address1, address2, city, state, zip, country, created_at) \
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (fn, ln, add1, add2, city, state, zc, country, today))
      conn.commit()

      #Testing to see if it works
      c.execute("SELECT * from USER")
      print(c.fetchall())
      conn.close()

      #Flash the notice that the record was added
      flash('Successfully Registered')
      return render_template('admin.html')

    return render_template('index.html', form=form)

@app.route('/admin')
def about():
  return render_template('admin.html')

if __name__ == '__main__':
  app.secret_key='superSecret'
  
  conn = sqlite3.connect('user.db')
  conn.execute('''CREATE TABLE IF NOT EXISTS USER
  (first_name TEXT NOT NULL,
  last_name TEXT OT NULL,
  address1 TEXT NOT NULL,
  address2 TEXT,
  city TEXT NOT NULL,
  state TEXT NOT NULL,
  zip TEXT NOT NULL,
  country TEXT NOT NULL,
  created_at DATE);''')

  app.run(debug=True)
