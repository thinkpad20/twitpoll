import random, string

populateDB = open("populate_db.sql", "w")
ptext = "LOAD DATA\n" + "LOCAL INFILE \"%s\"\n" + \
		"REPLACE INTO TABLE %s\n" + "FIELDS TERMINATED BY '|'\n" \
		"(%s);\n\n"

uid = 1
tid = 1
mid = 1
NUM_CITIES = 500
NUM_LOCATIONS = 200
NUM_USERS = 2000
NUM_TWEETS = 10000
NUM_HASHTAGS = 1000
NUM_MISC = 100
NUM_FOLLOWS = 1500
NUM_MESSAGES = 1000
NUM_POLLS = 300

hashtags = {}
mentions = {}
usernames = {}
def generateUsers(NUM_USERS):
	f = open("users.dat", "w")

	for i in range(0,NUM_USERS):
		u = User()
		u.randomize()
		f.write(u.itext())

	populateDB.write(ptext % ("users.dat", "User", User.ivars()))

def generateHashtags():
	f = open("hashtags.dat", "w")

	for key in hashtags.keys():
		for tweetID in hashtags[key]:
			f.write(str(tweetID) + '|' + key + '\n')
	populateDB.write(ptext % ("hashtags.dat", "HashTag", "tweetID, content"))


def rand_str(N, spaces = False):
	global words
	l = 0
	output = ""
	while l < N:
		output += random.choice(words)
		if spaces:
			output += " "
		l = len(output)
	if spaces:
		output = output[:-1] + "."
	return output

def rand_tweet(tweetID):
	global words, usernames
	output = random.choice(words)
	l = len(output)
	targetlen = random.randrange(20, 140)
	while l < targetlen:
		newWord = random.choice(words)
		p = random.choice(range(100))
		if p == 0:
			# add a hashtag here
			newWord = "#" + newWord
			if newWord in hashtags:
				hashtags[newWord] += [tweetID]
			else:
				hashtags[newWord] = [tweetID]
		# else if p == 1:
		# 	# add a mention
		# 	newWord = "@" + random.choice(usernames.keys)
		# 	if newWord in mentions:
		# 		mentions[newWord] += [(tweetID, ]
		# 	else:
		# 		hashtags[newWord] = [tweetID]
		output += newWord + " "
		l = len(output)
	output = output[:-1] + "."
	return output

words = []

for letter in string.uppercase:
	wordslist = [line.strip() for line in open("words/%s Words.csv" % letter)]
	words = words + wordslist
# for i in range(10):
# 	print words[i]

states = [line.strip() for line in open("words/states.txt")]
cities = [random.choice(words).title() for i in range(NUM_CITIES)]
locations = [("Somewhere", "Illinois")]


class User:
	username = "U"
	userID = 0
	fullName = "FN"
	passwordHash = "PWH"
	email = "EM"
	imageURL = "iURL"
	facebookURL = "fbURL"
	tagline = "tgln"
	age = 20
	sex = 'Male'
	def randomize(self):
		global uid, locations, usernames

		# generate unique user name
		username = rand_str(10)
		while username in usernames:
			username = rand_str(10)
		self.username = username
		usernames[self.username] = True

		self.fullName = "FN" + rand_str(20)
		self.userID = uid
		uid += 1
		self.city, self.state = random.choice(locations)
		self.passwordHash = "PWH" + rand_str(50)
		self.email = self.username + '@' + self.username + '.com'
		self.imageURL = "http://www.iURL.com/" + rand_str(10)
		self.facebookURL = "http://www.facebook.com/" + self.username
		self.tagline = "tgln" + rand_str(100)
		self.age = random.randrange(15, 65)
		self.sex = random.choice(["Male", "Female"])
	def itext(self):
		return "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%d\n" % (self.username, self.fullName, \
													 self.passwordHash, self.email, \
													 self.imageURL, self.facebookURL,\
													 self.tagline, self.city, self.state, \
													 self.sex, self.age)
	@staticmethod
	def ivars():
		return "username, fullName, passwordHash, email, imageURL, " \
			    "facebookURL, tagline, city, state, sex, age"


class Tweet:
	tweetID = 0
	userID = 0
	content = "content"
	def randomize(self):
		global uid, tid
		self.tweetID = tid
		tid += 1
		self.userID = random.randrange(1, uid)
		self.content = rand_tweet(self.tweetID)

class Hashtag:
	tweetID = 0
	content = "#content"
	def randomize(self):
		global tid
		self.tweetID = random.randrange(2, tid)
		self.content = "#" + rand_str(15)
	
class Follows:
	follower = 0
	followee = 0
	def randomize(self):
		global uid
		self.follower = random.randrange(1, uid)
		self.followee = random.randrange(1, uid)
		while (self.follower == self.followee):
			self.followee = random.randrange(1, uid)

class RetweetsMentionsFavoritesCanSee:
	userID = 0
	tweetID = 0
	def randomize(self):
		global uid, tid
		self.userID = random.randrange(1, uid)
		self.tweetID = random.randrange(2, tid)

class Message:
	messageID = 0
	senderID = 0
	receiverID = 0
	content = "content"
	def randomize(self):
		global uid, mid
		self.messageID = mid
		mid += 1
		self.content = rand_str(100, True)
		self.senderID = random.randrange(1, uid)
		self.receiverID = random.randrange(1, uid)
		while (self.senderID == self.receiverID):
			self.senderID = random.randrange(1, uid)

class Location:
	def __init__(self):
		self.state = ""
		self.city = ""
	def randomize(self):
		self.state = random.choice(states)
		self.city = random.choice(cities)		

class TweetPoll:
	# the format of a pollOptionText is (<text>###<nvotes)
	def __init__(self, pollID, tweetID, optionarr = []):
		self.pollID = pollID
		self.tweetID = tweetID
		self.optionarr = optionarr
		self.nvotes = {}
		for option in optionarr:
			self.nvotes[option] = 0
	def addOption(self, optionText):
		if optionText not in self.nvotes:
			optionarr.append(optionText)
			self.nvotes[optionText] = 0
	def getNumVotes(self, optionText):
		if optionText in self.nvotes:
			return self.nvotes[optionText]
	def vote(self, optionText):
		if optionText in self.nvotes:
			self.nvotes[optionText] += 1
	def renderText(self):
		txt = ""
		for option in self.optionarr:
			txt += "(%s###%s)" % (option, self.nvotes[option])
		return txt
	def itext(self):
		return "%d|%d|%s\n" % (self.pollID, self.tweetID, self.renderText())
	def parseText(self, text):
		self.optionarr = []
		self.nvotes = {}
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

			optionarr.append(option)
			nvotes[option] = nvotes
			i += 1
		



def generateData():
	global locations
	f = open("locations.dat", "w")
	for i in range(0,NUM_LOCATIONS):
		fo = Location()
		fo.randomize()
		f.write(fo.city + '|' + fo.state + '\n')
		locations += [(fo.city, fo.state)]
	populateDB.write(ptext % ("locations.dat", "Location", "city, state"))

	##################
	# USERS
	#####################
	generateUsers(NUM_USERS)
	##################
	# TWEETS
	#####################

	f = open("tweets.dat", "w")

	for i in range(0,NUM_TWEETS):
		t = Tweet()
		t.randomize()
		f.write(str(t.userID) + '|' + t.content + '\n')

	populateDB.write(ptext % ("tweets.dat", "Tweet", "userID, content"))

	##################
	# HASHTAGS
	#####################
	generateHashtags()
	##################
	# FOLLOWS
	#####################

	f = open("follows.dat", "w")

	for i in range(0,NUM_FOLLOWS):
		fo = Follows()
		fo.randomize()
		f.write(str(fo.follower) + '|' + str(fo.followee) + '\n')

	populateDB.write(ptext % ("follows.dat", "Follows", "follower, followee"))

	##################
	# Retweets, etc
	#####################

	schema = {"retweets.dat":"Retweets", "mentions.dat":"Mentions", "favorites.dat":"Favorites", "cansee.dat":"CanSee"}

	for filename in ["retweets.dat", "mentions.dat", "favorites.dat", "cansee.dat"]:
		f = open(filename, "w")
		for i in range(0,NUM_MISC):
			fo = RetweetsMentionsFavoritesCanSee()
			fo.randomize()
			f.write(str(fo.tweetID) + '|' + str(fo.userID) + '\n')
		populateDB.write(ptext % (filename, schema[filename], "tweetID, userID"))

	##################
	# Messages
	#####################

	f = open("messages.dat", "w")
	for i in range(0,NUM_MESSAGES):
		fo = Message()
		fo.randomize()
		f.write(str(fo.senderID) + '|' + str(fo.receiverID) + '|' + fo.content + '\n')
	populateDB.write(ptext % ("messages.dat", "Message", "senderID, receiverID, content"))

	##################
	# Polls
	##################
	tweetsUsed = {}
	f = open("polls.dat", "w")
	for i in range(0, NUM_POLLS):
		numopts = random.randrange(4) + 2
		opts = []
		for j in range(numopts):
			opts.append(rand_str(20, True))
		tweetID = random.randrange(3, NUM_TWEETS - 3)
		while tweetID in tweetsUsed:
			tweetID = random.randrange(3, NUM_TWEETS - 3)
		tweetsUsed[tweetID] = True
		tp = TweetPoll(i, tweetID, opts)
		f.write(tp.itext())
	populateDB.write(ptext % ("polls.dat", "Poll", "pollID, tweetID, pollOptionText"))



generateData()
