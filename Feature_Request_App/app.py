import dbobject as db
from boto.roboto import param
from flask import Flask, request, Request, render_template, url_for, redirect, flash, session
from flask_restful import Api, Resource, fields, marshal_with
import ast
import os
from functools import wraps
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
api = Api(app)
app.secret_key = os.urandom(24)
ticket_fields = {"id": fields.Integer,
                 "title": fields.String,
                 "description": fields.String,
                 "client": fields.String,
                 "client_priority": fields.Integer,
                 "target_date": fields.DateTime,
                 "ticket_url": fields.String,
                 "product_area": fields.String}


class FeatureRequest_api(Resource):
    @marshal_with(ticket_fields)
    def get(self, param):
        if param == "all":
           output = db.get_all(session['user_id'])
        return output, 200


    def post(self, param):
        if param =="new":
           priority = request.form.get('client_priority')
           print priority
           print "in new post"
           entries_to_downgrade = db.check_priorities_EL(priority, session['user_id'])
           print entries_to_downgrade
           if len(entries_to_downgrade) > 0:
              db.downgrade_priorities(entries_to_downgrade)
              db.insert_new(title=request.form.get('title'),
                  description=request.form.get('description'),
                  client=request.form.get('client'),
                  client_priority=request.form.get('client_priority'),
                  target_date=request.form.get('target_date'),
                  url_root=request.form.get('url_root'),
                  product_area=request.form.get('product_area'),
                  user_id=session['user_id'])
           else:
                db.downgrade_priorities(entries_to_downgrade)
                db.insert_new(title=request.form.get('title'),
                   description=request.form.get('description'),
                   client=request.form.get('client'),
                   client_priority=request.form.get('client_priority'),
                   target_date=request.form.get('target_date'),
                   url_root=request.form.get('url_root'),
                   product_area=request.form.get('product_area'),
                   user_id=session['user_id'])
           return '', 201



    def delete(self, param):
        if param == 'delete':
           db.delete_entry(request.form.get('id'))
           gaps = db.get_gaps(session['user_id'])
           if len(gaps) > 0:
              db.eleminate_gaps(gaps)
        return '', 204


    def put(self, param):
        if param == 'update':
           ticket_id = request.form.get('id')
           a = str(db.get_requests_by_id_list([ticket_id])[0])
           b = ast.literal_eval(a)
           if b["client_priority"] == str(request.form.get('client_priority')):
              db.update_entry(id=request.form.get('id'),
                  title=request.form.get('title'),
                  description=request.form.get('description'),
                  client=request.form.get('client'),
                  client_priority=request.form.get('client_priority'),
                  target_date=request.form.get('target_date'),
                  url_root=request.form.get('url_root'),
                  product_area=request.form.get('product_area'))
           else:
               ticket_id = request.form.get('id')
               db.delete_entry(ticket_id)
               gaps = db.get_gaps(session['user_id'])
               if len(gaps) > 0:
                  db.eleminate_gaps(gaps)
                  entries_to_downgrade = db.check_priorities_EL(request.form.get('client_priority'), session['user_id'])
                  if len(entries_to_downgrade) > 0:
                     db.downgrade_priorities(entries_to_downgrade)
                     db.insert_new(ind=request.form.get('id'),
                     title=request.form.get('title'),
                     description=request.form.get('description'),
                     client=request.form.get('client'),
                     client_priority=request.form.get('client_priority'),
                     target_date=request.form.get('target_date'),
                     url_root=request.form.get('url_root'),
                     product_area=request.form.get('product_area'),
                     user_id=session['user_id'])
                     gaps = db.get_gaps(session['user_id'])
                     if len(gaps) > 0:
                        db.eleminate_gaps(gaps)
        return '', 201


class Utils_api(Resource):
 def get(self, param):
  if param == "client_list":
    return db.get_client_list()
  if param == "possible_priorities":
    return db.get_possible_priorities(session['user_id'])
  if param == "production_areas":
    return db.get_production_area_list()

 def post(self, param):
     pass

 def delete(self):
     pass

 def update(self):
     pass


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
      if 'logged_in' in session:
          return f(*args, **kwargs)
      else:
          flash('Log in first')
          return redirect(url_for('login'))
    return wrap

# start page
@app.route('/requests_and_tickets')
@login_required
def requests_and_tickets():
    logged = False

    if 'logged_in' in session:
      logged = True
      return render_template('request_and_tickets.html', logged=logged)


# ticket page
@app.route('/ticket/<int:ticket_id>')
def ticket(ticket_id):
    logged = False
    if 'logged_in' in session:
        logged = True
    if ticket_id in db.get_all_ticket_ids(session['user_id']):
       ticket = db.get_requests_by_id_list([ticket_id])[0]
       return render_template('ticket.html', ticket=ticket, logged=logged)
    else:
       return render_template('404ticket.html', ticket_id=ticket_id)

@app.route('/')
def home():
    logged = False
    if 'logged_in' in session:
        logged = True
        return render_template('home.html', logged=logged)
    else:
        return render_template('about.html')

@app.route('/about')
def about():
    logged = False
    if 'logged_in' in session:
        logged = True
        return render_template('about.html', logged=logged)

#login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        print "am in login post"
        try:

           username = request.form['username'].strip()
           print username
           password = request.form['password'].strip()
           print password
    # shuffle the pawwsord with username
           pswrd = password[0]+username +password[1:]
           print pswrd
           pass_response = db.login(username)[0].password
           print pass_response
           user_id = db.login(username)[0].id
           print user_id
    #print pass_response
           logged = bcrypt.check_password_hash(pass_response, pswrd)
           if logged is False:
              error = 'Invalid username+password pair. Check your spelling or contact support.'
           else:
              session['logged_in'] = True
              session['username'] = username
              session['user_id'] = user_id
              return redirect(url_for('requests_and_tickets'))


        except Exception as e:
               error = 'Invalid username+password pair. Check your spelling or contact support.'
               return render_template('login.html', error=error)
    else:
        print "am in else loop"
        return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
 """
        registration
        TODO: get
        verivficatios
        out
        of
        the
        function
 """
 error = ''
 if request.method == 'POST':
        username = request.form['username'].strip()
        print username
        email = request.form['email'].strip()
        print email
        password1 = request.form['password1'].strip()
        print password1
        password2 = request.form['password2'].strip()
        print password2
 else:
     return render_template('register.html', error=error)

 if username == "":
    error += "Username is missing. "
 if email == "":
    error += "Email is missing. "
 if password1 == "" or password2 == "":
    error += "Type in and repeat the password. "
 if password1 != password2:
    error += "Passwords are not identical. "
 elif error == "":
        # shuffle the pawwsord with username
        pswrd = password1[0]+username+password1[1:]
        # bcrypt the mix
        pw_hash = bcrypt.generate_password_hash(pswrd)
        print "Testing123"
        # put it to the db

        print username+" "+pw_hash
        print len(pw_hash)
        print pw_hash
        print type(pw_hash)

        db.register(username, email, pw_hash)
        return redirect(url_for('login'))
        #return render_template('register.html')
        #return render_template('register.html', error=error)

#logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('logged_in', None)
    return redirect(url_for('home'))

api.add_resource(FeatureRequest_api, '/api/ticket/<param>')
api.add_resource(Utils_api, '/api/<param>')


def get_root_url():
    url_root = ''
    try:
       url_root = str(Request.url_root)
       print url_root
    except Exception as e:
       url_root = 'http://127.0.0.1:5000/'
       return url_root


if __name__ == "__main__":

# will drop existing and create new tables
#db.create_tables()

     app.run()