from flask import g, session

def data_from_cursor(cursor):
	return [dict((cursor.description[idx][0], value) for idx, value in enumerate(row)) \
													 for row in cursor.fetchall()]

def sql_search(q):
	if q[-1] != ';': q += ';'
	print "SQL QUERY:", q
	cursor = g.db.cursor()
	num_results = cursor.execute(q)
	res = data_from_cursor(cursor)
	print "RESULTS:", res
	return res

def sql_execute(q):
	if q[-1] != ';': q += ';'
	print "EXEC QUERY:", q
	cursor = g.db.cursor()
	cursor.execute(q)
	g.db.commit()
	res = cursor.lastrowid
	print "RESULT LAST ROWID:", res
	return res

add_quotes = lambda s : '"' + s + '"'

#### USERS ####

## this is a class which gives us easy access to a user
class User(object):
	def __init__(self, userdic):
		self.vals = userdic

	@staticmethod
	def current():
		if 'userID' in session:
			print "found userID:", session['userID']
			return User.find_by_id(session['userID'])
		return None

	@staticmethod
	def current_id():
		return int(session.get('userID', 1))

	@staticmethod
	def find_by_username(username):
		found = sql_search("select * from Users where username = " + add_quotes(username))
		if len(found) > 0 and found[0]: 
			return User(found[0])
		else: 
			return None

	@staticmethod
	def where(tbl = None):
		q = "select * from Users"
		if tbl:
			q += " where"
			for key in tbl.keys():
				q += " %s = '%s'" % (key, tbl[key])
		q += ";"
		res = sql_search(q)
		print "res:", res
		if res is not None:
			return [User(u) for u in res]
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
	def current_is(user, byID = False):
		if byID:
			print "looking up user by id", user
			user = User.find_by_id(user)
		if not user:
			print "user was not found"
		if not User.current(): 
			print "not logged in"
			return False
		if User.current_id() != user.userID():
			print "ids", User.current_id(), user.userID(), "don't match"
			return False
		return True

	@staticmethod
	def get(limit = None):
		q = "select * from Users"
		if limit: q += " order by userID desc limit " + str(limit)
		data = sql_search(q)
		return [ Tweet(tweetdic) for tweetdic in data ]

	@staticmethod
	def exists(userID):
		return User.find_by_id(userID) is not None

	@staticmethod
	def all():
		return User.where()

	@staticmethod
	def get_n(n):
		q = "select * from Users order by userID desc limit %d;" % n
		return [User(u) for u in sql_search(q)]
	
	@staticmethod
	def logged_in():
		return 'userID' in session

	@staticmethod
	def validate_new(username, password, email):
		user = User.find_by_username(username)
		print "User: ", user
		if not user:
			return None
		else:
			print "This user already exists: ", user
			return { "username":"already exists", "general":"Error creating new user account"}

	@staticmethod
	def add(username, password, email):
		error = User.validate_new(username, password, email)
		if error: return error
		q = "insert into Users (username, passwordHash, email) values ('%s', '%s', '%s')" \
															% (username, password, email)
		res = sql_execute(q)
		return None

	@staticmethod
	def delete(userID):
		q = "delete from Users where userID = %d" % int(userID)
		sql_execute(q)

	def attrs_to_display(self):
		return ["username", "fullName", "email", "tagline"]

	def __str__(self):
		vals_to_print = ["username", "fullName", "userID", "email"]
		ret = ""
		for key in self.vals:
			if key in vals_to_print:
				ret += " %s: %s" % (key, self.vals[key])
		return ret

	def is_following(self, userID):
		q = ("select * from Users u1, Users u2, Follows f "
			 "where u1.userID = f.follower "
			 "and u2.userID = f.followee "
			 "and u1.userID = %d "
			 "and u2.userID = %d " % (self.userID(), int(userID)))
		res = sql_search(q)
		if len(res) > 0:
			return True
		else:
			return False

	def username(self):
		return self.vals["username"]

	def userID(self):
		return self.vals["userID"]

	def email(self):
		return self.vals["email"]

	def full_name(self):
		return self.vals["fullName"]

	def checkpassword(self, password):
		return self.vals["passwordHash"] == password ## yes, this is horribly insecure

	def tweets(self):
		return Tweet.by_userID(self.userID())

	def favorites(self):
		q = "select f.tweetID from Favorites f where f.userID = %d" % self.userID()
		q = "select t.* from Tweets t where t.tweetID in (%s)" % q
		res = sql_search(q)
		if res:
			return [Tweet(t) for t in res]
		return []

	def add_favorite(self, tweetID):
		q = "insert into Favorites (userID, tweetID) values (%d, %d)" % \
									(int(self.userID()), int(tweetID))
		sql_execute(q)

	def remove_favorite(self, tweetID):
		q = "delete from Favorites where userID = %d and tweetID = %d" % \
									(int(self.userID()), int(tweetID))
		sql_execute(q)

	def is_favoriting(self, tweetID):
		print "++++++++++++++seeing if is favoriting"
		q = "select * from Favorites f where userID = %d and tweetID = %d" % \
												(int(self.userID()), int(tweetID))
		res = sql_search(q)
		return len(res) > 0

	def retweets(self):
		q = "select r.tweetID from Retweets r where r.userID = %d" % self.userID()
		q = "select t.* from Tweets t where t.tweetID in (%s)" % q
		res = sql_search(q)
		if res:
			return [Tweet(t) for t in res]
		return []

	def add_retweet(self, tweetID):
		q = "insert into Retweets (userID, tweetID) values (%d, %d)" % \
									(int(User.current_id()), int(tweetID))
		sql_execute(q)

	def remove_retweet(self, tweetID):
		q = "delete from Retweets where userID = %d and tweetID = %d" % \
									(int(User.current_id()), int(tweetID))
		sql_execute(q)

	def is_retweeting(self, tweetID):
		q = "select * from Retweets where userID = %d and tweetID = %d" % \
												(int(self.userID()), int(tweetID))
		res = sql_search(q)
		return len(res) > 0

	def followed_tweets(self):
		q = ("select t.* "
			"from Tweets t, Users followee, Follows f "
			"where followee.userID = f.followee "
			"and f.follower = %s "
			"and t.userID = followee.userID "
			"and t.visible = 1 "
			"order by t.tweetID desc" % self.userID())
		return [Tweet(t) for t in sql_search(q)]

	def followers(self):
		q = ("select follower.* "
			 "from Users follower, Users followee, Follows f "
			 "where follower.userID = f.follower "
			 "and followee.userID = f.followee " 
			 "and followee.userID = %d;") % self.userID()
		res = sql_search(q)
		if res:
			print "len: ", len(res)
			return [User(u) for u in res]
		return []

	def followed_users(self):
		q = ("select followee.* "
			 "from Users follower, Users followee, Follows f "
			 "where follower.userID = f.follower "
			 "and followee.userID = f.followee " 
			 "and follower.userID = %d;") % self.userID()
		print "++++++++++++++++++GETTING FOLLOWED USERS"
		res = sql_search(q)

		if res:
			print "len: ", len(res)
			return [User(u) for u in res]
		return []

	def follow(self, userID):
		if self.is_following(userID): return
		q = "insert into Follows (follower, followee) values (%d, %d)" % (self.userID(), userID)
		return sql_execute(q)

	def unfollow(self, userID):
		if not self.is_following(userID):return
		q = "delete from Follows where follower = %d and followee = %d" \
												% (self.userID(), userID)
		return sql_execute(q)

	def num_followed_users(self):
		return len(self.followed_users())

	def num_followers(self):
		return len(self.followers())

	def update(self, params):
		print "updating a user!"
		numvals = 0
		res = {}
		if 'password' in params and params['password'] != params.get('password_conf', ""):
			res["passwordconf"] = "passwords don't match"
		if 'username' in params and params['username'] != self.username():
			if len(params['username']) > 50:
				res["username"] = "Username is too long"
			else:
				q = "select * from Users where username = %s" % add_quotes(params['username'])
				r = sql_search(q)
				if r:
					res["username"] = "Username is not available"
		if 'email' in params:
			q = "select * from Users where email = %s" % add_quotes(params['email'])
			r = sql_search(q)
			if r:
				res["email"] = "Email is not available"
		if res: 
			print "Errors found!", res
			return res

		print "No errors detected so far."
		q = "update Users set "
		for val in params:
			if not val or not params[val] or val == "password_conf":
				continue
			if numvals > 0:
				q += ", "
			if val == "age":
				q += val + "=" + params[val]
			elif val == "password":
				q += "passwordHash=" + add_quotes(params[val])
			else:
				q += val + "=" + add_quotes(params[val])
				res[val] = "updated %s successfully" % val
			numvals += 1
		if numvals == 0: return
		q += " where userID = %d" % self.userID()
		sql_execute(q)
		res['general'] = "Updated account!"
		return res


####### end of class User #######

#### TWEETS ####

class Tweet(object):
	def __init__(self, tweetdic):
		self.vals = tweetdic
		if 'content' in self.vals:
			self.vals['content'] = Tweet.render_content(self.vals['content'])

	@staticmethod
	def find_by_username(username):
		q = ("select t.* from Users u, Tweets t where u.username = %s "
			"and t.visible = 1 " % add_quotes(username))
		found = sql_search(q)
		if len(found) > 0 and found[0]: 
			return Tweet(found[0])
		else: 
			return None

	@staticmethod
	def find_by_id(tweetID):
		q = "select * from Tweets where tweetID = %d and visible = 1" % int(tweetID)
		found = sql_search(q)
		if len(found) > 0 and found[0]: 
			return Tweet(found[0])
		else: 
			return None

	@staticmethod
	def by_userID(userID):
		q = "select * from Tweets where userID = %d and visible = 1" % int(userID)
		found = sql_search(q)
		return [ Tweet(tweet) for tweet in found ]

	@staticmethod
	def render_content(content):
		content = content.replace("|", "'").replace("_", '"')
		words = content.split(" ")
		res = ""
		for word in words:
			if word[0] == '@':
				print "++++++++++++++++++++++++++++++++++++AT MENTION FOUND"
				link = "/users/"
				user = User.find_by_username(word[1:])
				if user:
					link += str(user.userID())
					res += " <a href=\"%s\">%s</a>" % (link, word)
				else:
					res += " " + word
			elif word[0] == '#':
				res += " <a href=\"/hashtags/%s\">%s</a>" % (word[1:], word)
			else:
				res += " " + word
		return res

	@staticmethod
	def get(limit = None):
		q = "select * from Tweets where visible = 1 order by tweetID desc"
		if limit: q += " limit " + str(limit)
		data = sql_search(q)
		return [ Tweet(tweetdic) for tweetdic in data ]

	@staticmethod
	def make(userID, content, polloptions = []):
		if not User.logged_in(): return
		print "polloptions:", polloptions, "length:", len(polloptions)
		has_poll = 1 if len(polloptions) > 0 else 0
		print "Making a new tweet"
		q = "insert into Tweets (userID, content, hasPoll) values (%s, '%s', %d)" \
											% (str(userID), Tweet.escape(content), has_poll)
		tweetID = sql_execute(q)
		if has_poll == 1:
			print "User submitted a tweet with a poll! Options are:", polloptions
			Poll.make_new(tweetID, content, polloptions)
		for hashtag in Hashtag.detect(content):
			Hashtag.insert(tweetID, hashtag)
		for mention in Mention.detect(content):
			Mention.insert(tweetID, mention)

	@staticmethod
	def delete(tweetID):
		q = "update Tweets set visible=0 where tweetID = %d" % int(tweetID)
		return sql_execute(q)

	@staticmethod
	def search(keyword):
		q = "select * from Tweets where visible = 1 and content like \"%" + keyword + "%\")"
		return [Tweet(tweet) for tweet in sql_search(q)]

	@staticmethod
	def escape(strng):
		res = strng.replace("'", "|").replace('"', "_")
		return res

	def userID(self):
		return int(self.vals['userID'])

	def tweetID(self):
		return int(self.vals['tweetID'])

	def has_poll(self):
		poll = Poll.find_by_tweet(self.vals['tweetID'])
		if poll is not None:
			self.poll_cache = poll
			return True
		else:
			self.poll_cache = None
			return False

	def poll(self):
		if self.poll_cache:
			return self.poll_cache
		else:
			res = Poll.find_by_tweet(self.vals['tweetID'])
			if not res: print "Warning!! Poll was not found!"
			return res

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
		found = sql_search("select * from Hashtags where content = %s;" % add_quotes(content))
		if len(found) > 0:
			return [Hashtag(res) for res in found]
		return None

	@staticmethod
	def exists(content):
		q = "select * from Hashtags where content=%s" % add_quotes(content)
		res = sql_search(q)
		return True if len(res) > 0 else False

	@staticmethod
	def insert(tweetID, content):
		sql_execute("insert into Hashtags (content, tweetID) values (%s, %d);" \
														% (add_quotes(content), tweetID))
		
	@staticmethod
	def detect(tweet_content):
		return list(set([ word.strip().split()[0] for word in tweet_content.split("#")[1:]]))

	def tweets(self):
		found = sql_search(("select t.content, t.userID, t.dateTime "
						   "from Tweets t "
						   "inner join Hashtags h "
						   "on t.tweetID = h.tweetID "
						   "where h.content = %s "
						   "and t.visible = 1") % add_quotes(self.vals['content']))
		print "FOUND: ", found
		return [ Tweet(tweet) for tweet in found ]

	def content(self):
		return self.vals['content']

######## end of class Hashtag #########

class Poll(object):
	def __init__(self, tweet_text, options, votes, pollID):
		self.text = tweet_text
		self.options = options
		self.votes = votes
		self.set_pollID(pollID)

	@staticmethod
	def make_new(tweetID, tweet_text, options):
		votes = {}
		for option in options:
			votes[option] = 0
		option_text = ""
		for option in options:
			option_text += "(%s###0)" % option
		q = "insert into Polls (pollOptionText, tweetID) values (%s, %d)" \
													% (add_quotes(option_text), tweetID)
		pollID = sql_execute(q)
		return Poll(tweet_text, options, votes, pollID)

	@staticmethod
	def find_by_id(pollID):
		q = ("select p.*, t.content from Polls p "
			"inner join Tweets t "
			"on p.tweetID = t.tweetID "
			"where p.pollID = %d "
			"and t.visible = 1") % int(pollID)
		res = sql_search(q)
		if res:
			res = res[0]
			tweet_text = res['content']
			options, votes = Poll.parse(res['pollOptionText'])
			pollID = res['pollID']
			return Poll(tweet_text, options, votes, pollID)
		else: return None


	@staticmethod
	def find_by_tweet(tweetID):
		q = ("select p.*, t.content from Polls p "
			"inner join Tweets t "
			"on p.tweetID = t.tweetID "
			"where t.tweetID = %d "
			"and t.visible = 1") % tweetID
		res = sql_search(q)[0] if sql_search(q) else []
		if res:
			tweet_text = res['content']
			options, votes = Poll.parse(res['pollOptionText'])
			pollID = res['pollID']
			return Poll(tweet_text, options, votes, pollID)
		else: return None

	@staticmethod
	def parse(text):
		arr = []
		dic = {}
		optionnum, nvotes, i = 0, 0, 0
		while i < len(text):
			optionnumtext = ""
			option = ""
			numtext = ""
			if text[i] == '(':
				i += 1

				while text[i:i+3] != '###':
					option += text[i]
					i += 1
				i += 3

				while text[i] != ')':
					numtext += text[i]
					i += 1
				nvotes = int(numtext)

			arr.append(option)
			dic[option] = nvotes
			i += 1
		return (arr, dic)

	@staticmethod
	def vote(pollID, optionnum):
		poll = Poll.find_by_id(pollID)
		if poll:
			poll.record_vote(optionnum)

	def tweet_text(self):
		return self.tweet_text

	def set_pollID(self, pollID):
		self.pollID = pollID

	def get_pollID(self):
		return self.pollID

	def render_code(self):
		code = ""
		for option in self.options:
			code += "(%s###%d)" % (option, self.votes[option])
		return code

	def record_vote(self, index):
		index = int(index)
		if index < len(self.options):
			self.votes[self.options[index]] += 1
		q = "update Polls set pollOptionText = %s where pollID = %d" \
									% (add_quotes(self.render_code()), self.get_pollID())
		sql_execute(q)


class Mention(object):
	@staticmethod
	def find_by_id(userID):
		return sql_search("select * from Mentions where userID = %d;" % int(userID))

	@staticmethod
	def find_by_username(username):
		mentions = ("select * from Mentions m where m.userID in ("
					   "select u.userID from Users u "
					   "where u.username = %s") % add_quotes(username)
		return sql_search(mentions)

	@staticmethod
	def insert(tweetID, username):
		user = User.find_by_username(username)
		if not user: return
		sql_execute("insert into Mentions (userID, tweetID) values (%d, %d);" % \
														(user.userID(), tweetID))

	@staticmethod
	def detect(tweet_content):
		return list(set([ word.strip().split()[0] for word in tweet_content.split("@")[1:]]))

	@staticmethod
	def tweets_by_userID(userID):
		found = sql_search(("select t.content, t.userID, t.dateTime "
						   "from Tweets t "
						   "inner join Mentions m "
						   "on t.tweetID = m.tweetID "
						   "where m.userID = %d "
						   "and t.visible = 1") % userID)
		return [ Tweet(tweet) for tweet in found ]

	@staticmethod
	def tweets_by_username(username):
		found = sql_search(("select t.content, t.userID, t.dateTime "
						   "from Tweets t "
						   "inner join Mentions m "
						   "on t.tweetID = m.tweetID "
						   "where m.userID in ("
						   "select u.userID from Users u "
						   "where u.username = %s "
						   "and t.visible = 1 limit 1)") % add_quotes(username))
		return [ Tweet(tweet) for tweet in found ]