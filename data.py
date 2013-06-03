from flask import g, session

def data_from_cursor(cursor):
	return [dict((cursor.description[idx][0], value) for idx, value in enumerate(row)) \
													 for row in cursor.fetchall()]

def sql_search(q):
	if q[-1] != ';': q += ';'
	print "SQL QUERY:", q
	cursor = g.db.cursor()
	num_results = cursor.execute(q)
	return data_from_cursor(cursor)

def sql_execute(q):
	if q[-1] != ';': q += ';'
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
	def find_by_id(userID):
		found = sql_search("select * from Users where userID = " + str(userID))
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

	@staticmethod
	def userID_from_username(username):
		username_r = sql_search("select userID from Users where username = " + add_quotes(username))
		if len(username_r) == 0:
			return None
		return username_r[0]['userID']

	@staticmethod
	def get(limit = None):
		q = "select * from Users"
		if limit: q += " order by userID desc limit " + str(limit)
		data = sql_search(q)
		return [ Tweet(tweetdic) for tweetdic in data ]
			
	
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
		return self.vals["passwordHash"] == password ## yes, this is horribly insecure

	def tweets(self):
		return Tweet.by_userID(self.userID()) 

####### end of class User #######

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
		if 'content' in self.vals:
			self.vals['content'] = Tweet.render_content(self.vals['content'])

	@staticmethod
	def find_by_username(username):
		found = sql_search("select * from Users, Tweets where username = " + add_quotes(username))
		if len(found) > 0 and found[0]: 
			return Tweet(found[0])
		else: 
			return None

	@staticmethod
	def find_by_id(tweetID):
		found = sql_search("select * from Tweets where tweetID = " + str(tweetID))
		if len(found) > 0 and found[0]: 
			return User(found[0])
		else: 
			return None

	@staticmethod
	def by_userID(userID):
		found = sql_search("select * from Tweets where userID = " + str(userID))
		return [ Tweet(tweet) for tweet in found ]

	@staticmethod
	def render_content(content):
		words = content.split(" ")
		res = ""
		for word in words:
			if word[0] == '@':
				link = "/users/"
				user = User.find_by_username(word[1:])
				if user:
					link += user.vals['userID']
				res += " <a href=\"%s\">%s</a>" % (link, word)
			elif word[0] == '#':
				res += " <a href=\"/hashtags/%s\">%s</a>" % (word[1:], word)
			else:
				res += " " + word
		return res

	@staticmethod
	def get(limit = None):
		q = "select * from Tweets"
		if limit: q += " order by tweetID desc limit " + str(limit)
		data = sql_search(q)
		return [ Tweet(tweetdic) for tweetdic in data ]

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

####### end of class Tweet #######

class Hashtag(object):
	def __init__(self, hashtagdic):
		self.vals = hashtagdic

	@staticmethod
	def find_by_content(content):
		found = sql_search("select * from ContainsHashtag where content = %s;" % add_quotes(content))
		if len(found) > 0:
			return Hashtag(found[0])
		return None

	@staticmethod
	def exists(content):
		q = "select * from Hashtags where content=%s" % add_quotes(content)
		res = sql_search(q)
		return True if len(res) > 0 else False

	@staticmethod
	def insert_hashtag(tweetID, content):
		if not Hashtag.exists(content):
			sql_execute("insert into Hashtags (content) values (%s);" % add_quotes(content))
		sql_execute("insert into ContainsHashtag (content, tweetID) values (%s, %d);" % \
														(add_quotes(content), tweetID))

	def tweets(self):
		found = sql_search("select t.content, t.userID, t.dateTime "
						   "from Tweets t "
						   "inner join ContainsHashtag ch "
						   "on t.tweetID = ch.tweetID "
						   "where ch.content = %s;" % add_quotes(self.vals['content']))
		print "FOUND: ", found
		return [ Tweet(tweet) for tweet in found ]

	def content(self):
		return self.vals['content']

get_hashtags = lambda content: list(set([ word.strip().split()[0] for word in content.split("#")[1:]]))
get_mentions = lambda content: list(set([ word.strip().split()[0] for word in content.split("@")[1:]]))

def make_tweet(userID, content):
	if not user_logged_in(): return
	print "Making a new tweet"
	q = "insert into Tweets (userID, content) values (%s, '%s')" % (str(userID), content)
	tweetID = sql_execute(q)
	print "Hashtags:", get_hashtags(content)
	for hashtag in get_hashtags(content):
		Hashtag.insert_hashtag(tweetID, hashtag)
	# for mention in get_mentions(content):
	# 	make_hashtag(tweetID, hashtag)