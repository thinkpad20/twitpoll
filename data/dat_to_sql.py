import random

uids = [1]
for i in range(199):
	uids.append(uids[-1] + 10)

tids = [1]
for i in range(199):
	tids.append(tids[-1] + 10)


def line_to_sql(vals, val_names, no_quotes, table_name, delim = "|"):
	if len(vals) != len(val_names):
		print "Error, length mismatch"
		return
	val_name_list = val_names[0]
	if val_names[0] == "userID" or val_names[0] == "follower" or val_names[0] == "followee":
		val_list = str(random.choice(uids))
	elif val_names[0] == "tweetID":
		val_list = str(random.choice(tids))
	else:
		val_list = vals[0] if 0 in no_quotes else "'%s'" % vals[0]
	has_poll = 0
	for i in range(1, len(val_names)):
		val_name_list += ", " + val_names[i]
		if val_names[i] == "userID" or val_names[i] == "follower" or val_names[i] == "followee":
			val_list += ", " + str(random.choice(uids))
		elif val_names[i] == "tweetID":
			val_list += ", " + str(random.choice(tids))
		elif i in no_quotes:
			val_list += ", " + vals[i]
		else:
			val_list += ", '" + vals[i] + "'"
	if table_name = "Tweets":
		val_name_list += ", hasPoll"
		val_list += ", " + has_poll
	return "INSERT INTO %s (%s) VALUES (%s);\n" % (table_name, val_name_list, val_list)

def process(val_names, no_quotes, in_file, out_file, table_name, skip = None):
	f = open(in_file)
	r = open(out_file, "w")
	for line in f.readlines():
		lin = line.strip().split("|")
		if skip:
			for idx in skip:
				del lin[idx]
		r.write(line_to_sql(lin, val_names, no_quotes, table_name))

user_val_names = ["username", "fullName", "passwordHash", "email", "imageURL", \
			    "facebookURL", "tagline", "city", "state", "sex", "age"]
user_no_quotes = [10]

process(user_val_names, user_no_quotes, "users.dat", "users.sql", "Users")

tweet_val_names = ["userID", "content"]
tweet_no_quotes = [0]

process(tweet_val_names, tweet_no_quotes, "tweets.dat", "tweets.sql", "Tweets")

misc_val_names = ["tweetID", "userID"]
misc_no_quotes = [0,1]

for t in ["Mentions", "Retweets", "Favorites"]:
	process(misc_val_names, misc_no_quotes, t.lower() + ".dat", t.lower() + ".sql", t)

poll_val_names = ["tweetID", "pollOptionText"]
poll_no_quotes = [0]

process(poll_val_names, poll_no_quotes, "polls.dat", "polls.sql", "Polls", [0])

follow_val_names = ["follower", "followee"]
follow_no_quotes = [0,1]

process(follow_val_names, follow_no_quotes, "follows.dat", "follows.sql", "Follows")