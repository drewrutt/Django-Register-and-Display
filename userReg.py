import sqlite3
from flask import Flask, g, render_template, flash, redirect, url_for, session, request
from datetime import datetime
from wtforms import Form, StringField, validators

#Create the app and set the "super secret" key
app = Flask(__name__)
app.secret_key='superSecret'

DATABASE = 'user.db'

#The arrays for the form field validation
states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
"SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
countries = ["US"]

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#WTForms registration form fields.
class formReg(Form):
  first_name = StringField('First Name', [validators.length(min=1, max=50)])
  last_name = StringField('Last Name', [validators.length(min=1, max=50)])
  address1 = StringField('Address 1', [validators.length(min=1, max=95)])
  address2 = StringField('Address 2')
  city = StringField('City', [validators.length(min=1, max=35)])
  state = StringField('State (2 Digit Code)', [validators.any_of(states), validators.length(min=1, max=2)])
  zipCode = StringField('Zip Code', [validators.length(min=5, max=9)])
  country = StringField('Country (US Only)', [validators.any_of(countries), validators.length(min=1, max=2)])

@app.route('/', methods=['GET', 'POST'])
def index():
  #Connect to the database and create the table if it doesnt exist already.
  conn = get_db()
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

  #Get the form and if there is a POST request and there is a form,
  #insert the form information into the database.
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

    #Get the current date and time
    today = datetime.now()
    today = today.strftime("%Y-%m-%d %H:%M:%S")

    #Get the database and insert into the table
    c = conn.cursor()
    c.execute("INSERT INTO USER (first_name, last_name, address1, address2, city, state, zip, country, created_at) \
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (fn, ln, add1, add2, city, state, zc, country, today))
    conn.commit()

    #Flash the notice that the record was added
    flash('Successfully Registered')
    return render_template('confirmation.html')

  return render_template('index.html', form=form)

#App route for the admin page
@app.route('/admin', methods=['GET', 'POST'])
def admin():
  rows = []
  conn = get_db()
  c = conn.cursor()

  #Select all rows in the table and turn them into dictionaries
  c.execute("SELECT * FROM USER ORDER BY created_at DESC")
  rowstemp = c.fetchall()
  for row in rowstemp:
    rows.append(make_dicts(c, row))


  #If there is a POST request, run the reset database query
  if request.method == 'POST':
    c.execute("DELETE FROM USER")
    conn.commit()
    conn.close()
    rows = []

    return render_template('admin.html', rows=rows)

  conn.close()
  return render_template('admin.html', rows=rows)

@app.route('/confirmation')
def confirmation():
  return render_template('confirmation.html')

#main
if __name__ == '__main__':
  app.run(debug=True)
