from flask import g, session

def data_from_cursor(cursor):
	return [dict((cursor.description[idx][0], value) for idx, value in enumerate(row)) \
													 for row in cursor.fetchall()]

def sql_search(q):
	print "SQL QUERY:", q
	cursor = g.db.cursor()
	num_results = cursor.execute(q)
	return data_from_cursor(cursor)

def sql_execute(q):
	print "EXEC QUERY:", q
	cursor = g.db.cursor()
	cursor.execute(q)
	g.db.commit()
	return cursor.lastrowid

add_quotes = lambda s : '"' + s + '"'

#### USERS ####

## this is a class which gives us easy access to a user
class User(object):
	def __init__(self, userdic):
		self.vals = userdic

	@staticmethod
	def find_by_username(username):
		found = sql_search("select * from Users where username = " + add_quotes(username))
		if len(found) > 0 and found[0]: 
			return User(found[0])
		else: 
			return None

	@staticmethod
	def find_by_id(userid):
		found = sql_search("select * from Users where userID = " + str(userid))
		if len(found) > 0 and found[0]: 
			return User(found[0])
		else: 
			return None

	@staticmethod
	def authenticate(username, password):
		user = User.find_by_username(username)
		if not user:
			return None, {'username':"This user doesn't exist"}
		if not user.checkpassword(password):
			return None, {'password':"Password doesn't match"}
		return user, None
	
	def attrs_to_display(self):
		return ["username", "fullName", "email", "tagline"]

	def __str__(self):
		vals_to_print = ["username", "fullName", "userID", "email"]
		ret = ""
		for key in self.vals:
			if key in vals_to_print:
				ret += " %s: %s" % (key, self.vals[key])
		return ret

	def username(self):
		return self.vals["username"]

	def userID(self):
		return self.vals["userID"]

	def checkpassword(self, password):
		return self.vals["passwordHash"] == password

def current_user():
	res = User.find_by_username(session['username'])
	print "Here's what we found: ", res
	return res

def get_user_where(tbl = None):
	q = "select * from Users"
	if tbl:
		q += " where"
		for key in tbl.keys():
			q += " %s = '%s'" % (key, tbl[key])
	q += ";"
	return sql_search(q)

def get_all_users():
	return get_user_where()

def user_logged_in():
	return 'username' in session

def validate_new_user(username, password, email):
	user = User.find_by_username(username)
	print "User: ", user
	if not user:
		return None
	else:
		print "This user already exists: ", user
		return { "username":"already exists", "general":"Error creating new user account"}

def add_user(username, password, email):
	error = validate_new_user(username, password, email)
	if error:
		return error
	q = "insert into Users (username, passwordHash, email) values ('%s', '%s', '%s')" \
														% (username, password, email)
	sql_execute(q)

#### TWEETS ####

class Tweet(object):
	def __init__(self, tweetdic):
		self.vals = tweetdic

	@staticmethod
	def find_by_username(username):
		found = sql_search("select * from Users, Tweets where username = " + add_quotes(username))
		if len(found) > 0 and found[0]: 
			return User(found[0])
		else: 
			return None

	@staticmethod
	def find_by_id(tweetid):
		found = sql_search("select * from Tweets where tweetID = " + str(tweetid))
		if len(found) > 0 and found[0]: 
			return User(found[0])
		else: 
			return None

	def username(self):
		user = sql_search("select * from Users where userID=%s" % str(self.vals['userID']))[0]
		return user['username']

	def attrs_to_display(self):
		return ["username", "fullName", "email", "tagline"]

	def __str__(self):
		vals_to_print = ["tweetID", "dateTime"]
		ret = self.username()
		for key in self.vals:
			if key in vals_to_print:
				ret += " %s: %s" % (key, self.vals[key])
		return ret


get_hashtags = lambda content : list(set([ word.strip().split()[0] for word in content.split("#")[1:]]))
get_mentions = lambda content : list(set([ word.strip().split()[0] for word in content.split("@")[1:]]))

def get_tweets():
	data = sql_search("select * from Tweets;")
	print "data:", data
	return [ Tweet(tweetdic) for tweetdic in data ]

def make_tweet(userid, content):
	if not user_logged_in(): return
	print "Making a new tweet"
	q = "insert into Tweets (userid, content) values (%s, '%s')" % (str(userid), content)
	tweetid = sql_execute(q)
	print "Hashtags:", get_hashtags(content)
	for hashtag in get_hashtags(content):
		make_hashtag(tweetid, hashtag)
	# for mention in get_mentions(content):
	# 	make_hashtag(tweetid, hashtag)

def render_tweet(content):
	print "yo"


#### HASHTAGS ####

def hashtag_exists(hashtag):
	q = "select * from Hashtags where content=" % add_quotes(hashtag)
	res = sql_search(q)
	return True if len(res) > 0 else False

def make_hashtag(tweetid, hashtag):
	if not hashtag_exists(hashtag):
		sql_execute("insert into Hashtags (content) values (%s)") % add_quotes(hashtag)
	sql_execute("insert into ContainsHashtag (content, tweetID) values (%s, %d)") % \
															(add_quotes(hashtag), tweetid)