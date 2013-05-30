LOAD DATA
LOCAL INFILE "locations.dat"
REPLACE INTO TABLE Location
FIELDS TERMINATED BY '|'
(city, state);

LOAD DATA
LOCAL INFILE "users.dat"
REPLACE INTO TABLE User
FIELDS TERMINATED BY '|'
(username, fullName, passwordHash, email, imageURL, facebookURL, tagline, city, state, sex, age);

LOAD DATA
LOCAL INFILE "tweets.dat"
REPLACE INTO TABLE Tweet
FIELDS TERMINATED BY '|'
(userID, content);

LOAD DATA
LOCAL INFILE "hashtags.dat"
REPLACE INTO TABLE HashTag
FIELDS TERMINATED BY '|'
(tweetID, content);

LOAD DATA
LOCAL INFILE "follows.dat"
REPLACE INTO TABLE Follows
FIELDS TERMINATED BY '|'
(follower, followee);

LOAD DATA
LOCAL INFILE "retweets.dat"
REPLACE INTO TABLE Retweets
FIELDS TERMINATED BY '|'
(tweetID, userID);

LOAD DATA
LOCAL INFILE "mentions.dat"
REPLACE INTO TABLE Mentions
FIELDS TERMINATED BY '|'
(tweetID, userID);

LOAD DATA
LOCAL INFILE "favorites.dat"
REPLACE INTO TABLE Favorites
FIELDS TERMINATED BY '|'
(tweetID, userID);

LOAD DATA
LOCAL INFILE "cansee.dat"
REPLACE INTO TABLE CanSee
FIELDS TERMINATED BY '|'
(tweetID, userID);

LOAD DATA
LOCAL INFILE "messages.dat"
REPLACE INTO TABLE Message
FIELDS TERMINATED BY '|'
(senderID, receiverID, content);

LOAD DATA
LOCAL INFILE "polls.dat"
REPLACE INTO TABLE Poll
FIELDS TERMINATED BY '|'
(pollID, tweetID, pollOptionText);

