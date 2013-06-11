from flask import Flask, render_template, url_for, \
				  g, session, request, redirect
from data import *
import os
from flaskext.mysql import MySQL

app = Flask(__name__)
app.jinja_env.globals["site_name"] = "TwitPoll"
app.jinja_env.globals.update(Tweet=Tweet, User=User, navclass = {}, type=type, len=len)

#####################################################
################# DATABASE SETUP ####################
#####################################################

app.config['MYSQL_DATABASE_HOST'] 		= os.environ['MYSQL_DATABASE_HOST']
app.config['MYSQL_DATABASE_PORT'] 		= int(os.environ['MYSQL_DATABASE_PORT'])
app.config['MYSQL_DATABASE_USER'] 		= os.environ['MYSQL_DATABASE_USER']
app.config['MYSQL_DATABASE_PASSWORD'] 	= os.environ['MYSQL_DATABASE_PASSWORD']
app.config['MYSQL_DATABASE_DB'] 		= os.environ['MYSQL_DATABASE_DB']

# connect database to our app
mysql = MySQL()
mysql.init_app(app)

######################################################

if 'SECRET_KEY' in os.environ: app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
else: app.config['SECRET_KEY'] = os.urandom(24)

@app.before_request
def before():
	g.db = mysql.connect()
	
@app.teardown_request
def after(ex):
	if ex: print ex
	g.db.close()

######################################################

def set_active(page):
	app.jinja_env.globals.update(navclass = {page: 'active'})


@app.route("/")
def home():
	set_active("home")
	return render_template("home.html")


@app.route("/users", methods=["GET", "POST"])
def users():
	if request.method == "GET":
		set_active("users")
		return render_template("users.html")
	elif request.method == "POST": # make a new user account
		# return "hello"
		print "Processing a new user account request. Form: ", request.form
		username = request.form.get("username", "")
		password = request.form.get("password", "")
		passwordconf = request.form.get("passwordconf", "")
		email = request.form.get("email", "")
		
		error = {}
		if username and password and email and password == passwordconf:
			error = User.add(username, password, email)
			if not error:
				session["username"] = username
				return render_template("users.html", messages = {'general': 'welcome to TwitPoll!'})
			else:
				return render_template("signup.html", error=error)
		else:
			error = {"general":"Incorrect user entry"}
			if not username:
				error['username'] = "Please put in a username"
			if not password:
				error['password'] = "Please enter a password"
			if password != passwordconf:
				error['passwordconf'] = "Passwords don't match"
			if not email:
				error['email'] = "Please enter an email address"
			return render_template("signup.html", error=error)

@app.route("/users/<userid>/")
def user_profile(userid):
	return render_template("user.html", user=User.find_by_id(userid))

@app.route("/users/<int:userid>/tweets")
def user_tweets(userid):
	print "here's where we should show the tweets for user %d" % userid
	return redirect(url_for("show_tweets"));

@app.route("/users/<userid>/edit")
def edit_user(userid):
	print "to edit a user's profile"
	return redirect(url_for("users"))

@app.route("/tweets")
def show_tweets():
	set_active("tweets")
	return render_template("tweets.html")

@app.route("/tweets/new", methods=["GET", "POST"])
def tweet():
	set_active("newtweet")
	if request.method == "GET":
		if User.logged_in():
			return render_template("newtweet.html")
		else:
			return redirect(url_for("signup"))
	elif request.method == "POST":
		content = request.form.get("content", "")
		polloptions = []
		for i in range(1, 7):
			op = 'option' + str(i) 
			if op in request.form and request.form[op] != "":
				polloptions.append(request.form[op])
		errors = {}
		if User.logged_in():
			userid = User.current().userID()
			Tweet.make(userid, content, polloptions)
			return redirect(url_for('user_tweets', userid=userid))
		else:
			errors['general'] = "You are not logged in"
			return render_template("home.html", error=errors)

@app.route("/hashtags/<content>")
def show_hashtag(content):
	hashtag = Hashtag.find_by_content(content)
	if not hashtag:
		return redirect(url_for('home'));
	return render_template("hashtag.html", hashtag=Hashtag.find_by_content(content))

@app.route("/poll/<pollID>", methods=["POST"])
def make_vote(pollID):
	if not User.logged_in():
		return render_template("home.html", error={'general': "You are not logged in"})		
	if 'option_num' in request.form:
		num = request.form['option_num']
		Poll.vote(pollID, num)
		return render_template("tweets.html")

@app.route("/signout")
def signout():
	session.clear()
	return redirect(url_for('home'))

@app.route("/signup")
def signup():
	set_active("signup")
	return render_template("signup.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
	if request.method == "GET":
		set_active("signin")
		return render_template("signin.html")
	else:
		username = request.form.get("username", "")
		password = request.form.get("password", "")
		if username and password:
			user, error = User.authenticate(username, password)
			if user is not None:
				session['username'] = username
				return redirect(url_for('user_profile', userid=user.userID()))
			else:
				return render_template('signin.html', error=error)
		else:
			error = {}
			if not username:
				error['username'] = "please enter a username"
			if not password:
				error['password'] = "please enter a password"
			return render_template('signin.html', error=error)

if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(debug=True, port=port, host='0.0.0.0')