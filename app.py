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
				session["userID"] = User.find_by_username(username).userID()
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

@app.route("/users/<userid>")
def user_profile(userid):
	return render_template("user.html", user=User.find_by_id(userid))

@app.route("/users/<int:userid>/tweets")
def user_tweets(userid):
	print "here's where we should show the tweets for user %d" % userid
	return redirect(url_for("show_tweets"));

@app.route("/users/edit/<userID>", methods=["GET", "POST"])
def edit_user(userID):
	print "processing a " + request.method + " request to /users/edit/" + userID
	set_active("")
	user = User.find_by_id(userID)
	if not User.current_is(userID, True):
		return redirect(url_for("users"))
	if request.method == "GET":
		return render_template("edit_user.html", user = user)
	else:
		res = User.current().update(request.form)
		return render_template("user.html", user=user, messages=res)

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
			userid = User.current_id()
			Tweet.make(userid, content, polloptions)
			return redirect(url_for('user_tweets', userid=userid))
		else:
			errors['general'] = "You are not logged in"
			return render_template("home.html", error=errors)

@app.route("/delete/<userID>", methods=["GET", "POST"])
def delete_account(userID):
	if not User.exists(userID):
		return redirect(url_for('error404'))
	if request.method == "GET":
		return render_template("delete_confirm.html", user=User.find_by_id(userID))
	if request.method == "POST":
		set_active("home")
		if User.logged_in() and User.current_id() == int(userID):
			msg = "Sad to see you go, %s!" % User.current().username()
			User.delete(userID)
			session.clear()
			return render_template("home.html", error={'general':msg})
		else:
			return render_template("home.html", error={'general':'You are not logged in.'})

@app.route("/tweets/delete/<tweetID>", methods=["POST"])
def delete_tweet(tweetID):
	set_active("tweets")
	if Tweet.find_by_id(tweetID) is not None:
		Tweet.delete(tweetID)
	return render_template("tweets.html")

@app.route("/tweets/followedby/<userID>")
def view_followed_tweets(userID):
	set_active("followed_tweets")
	if User.exists(int(userID)):
		return render_template("followed_tweets.html", user=User.find_by_id(int(userID)))
	return render_template(url_for('show_tweets'))

@app.route("/user/follow/<userID>", methods=["POST"])
def follow(userID):
	print "Someone has requested a fol/defol!"
	if not User.exists(int(userID)):
		return render_template("home.html", error={"general":\
						"We're sorry, that user doesn't seem to exist."})
	user = User.current()
	userID = int(userID)
	tofollow = User.find_by_id(userID)
	if not User.logged_in():
		return render_template("home.html", error={'general':'You are not logged in.'})
	msg = ""
	template = request.args.get("prev", "tweets.html")
	src_userID = request.args.get("id", User.current_id())
	if user.is_following(userID):
		msg = "You have unfollowed " + tofollow.username()
		user.unfollow(userID)
	else:
		msg = "You are now following " + tofollow.username()
		user.follow(userID)
	set_active(template.split(".")[0])
	return render_template(template, user=User.find_by_id(src_userID), messages={'general':msg})

@app.route("/hashtags/<content>")
def show_hashtag(content):
	hashtag = Hashtag.find_by_content(content)
	if not hashtag:
		return redirect(url_for('home'));
	return render_template("hashtag.html", hashtag=Hashtag.find_by_content(content)[0])

@app.route("/poll/<pollID>", methods=["POST"])
def make_vote(pollID):
	print "someone wants to vote on poll", pollID
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
				session['userID'] = user.userID()
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

@app.errorhandler(404)
def error404(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(debug=True, port=port, host='0.0.0.0')