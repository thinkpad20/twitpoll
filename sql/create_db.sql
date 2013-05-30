-- select "Drop CanSees" as "Action";
DROP TABLE IF EXISTS CanSees;

-- select "Drop Mentions" as "Action";
DROP TABLE IF EXISTS Mentions;

-- select "Drop Retweets" as "Action";
DROP TABLE IF EXISTS Retweets;

-- select "drop Favorites" as "Action";
DROP TABLE IF EXISTS Favorites;

-- select "drop Follows" as "Action";
DROP TABLE IF EXISTS Follows;

-- select "drop ContainsHashtag" as "Action";
DROP TABLE IF EXISTS ContainsHashtag;

-- select "drop Hashtags" as "Action";
DROP TABLE IF EXISTS Hashtags;

-- select "Drop Messages" as "Action";
DROP TABLE IF EXISTS Messages;

-- select "drop Polls" as "Action";
DROP TABLE IF EXISTS Polls;

-- select "drop Tweets" as "Action";
DROP TABLE IF EXISTS Tweets;

-- select "drop Users" as "Action";
DROP TABLE IF EXISTS Users;

-- select "drop Locations" as "Action";
DROP TABLE IF EXISTS Locations;

-- select "create Locations" as "Action";

CREATE TABLE Locations (
	city VARCHAR(100)				NOT NULL,
	state VARCHAR(50)				NOT NULL,
	PRIMARY KEY (city, state)
);

-- select "create Users" as "Action";

CREATE TABLE Users (
	username 		VARCHAR(50) 	NOT NULL UNIQUE,
	userID 			INTEGER			NOT NULL AUTO_INCREMENT,
	fullName 		VARCHAR(100),
	passwordHash 	VARCHAR(256) 	NOT NULL,
	email 			VARCHAR(256)	NOT NULL,
	imageURL 		VARCHAR(200),
	facebookURL		VARCHAR(200),
	tagline 		VARCHAR(140),
	city 			VARCHAR(100),
	state			VARCHAR(50),
	sex				VARCHAR(10),
	age				INTEGER,
	memberSince 	TIMESTAMP		NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (userID)	
);

-- select "create Tweets" as "Action";

CREATE TABLE Tweets (
	tweetID INTEGER 				NOT NULL AUTO_INCREMENT,
	userID INTEGER	 				NOT NULL,
	content VARCHAR(140)			NOT NULL,
	dateTime TIMESTAMP			 	NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (tweetID),
	FOREIGN KEY (userID) REFERENCES Users(userID)
);

-- select "create Hashtags" as "Action";

CREATE TABLE Hashtags (
	content VARCHAR(140) 			NOT NULL,
	PRIMARY KEY (content)
);

-- select "create Follows" as "Action";

CREATE TABLE Follows (
	follower INTEGER 				NOT NULL,
	followee INTEGER 				NOT NULL,
	PRIMARY KEY (follower, followee),
	FOREIGN KEY (follower) REFERENCES Users(userID),
	FOREIGN KEY (followee) REFERENCES Users(userID)
);

-- select "create Retweets" as "Action";

CREATE TABLE Retweets (
	tweetID INTEGER 				NOT NULL,
	userID INTEGER 					NOT NULL,
	dateTime TIMESTAMP				NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (userID, tweetID),
	FOREIGN KEY (userID) REFERENCES Users(userID),
	FOREIGN KEY (tweetID) REFERENCES Tweets(tweetID)
);

-- select "create Mentions" as "Action";

CREATE TABLE Mentions (
	tweetID INTEGER 				NOT NULL,
	userID INTEGER 					NOT NULL,
	PRIMARY KEY (tweetID, userID),
	FOREIGN KEY (tweetID) REFERENCES Tweets(tweetID),
	FOREIGN KEY (userID) REFERENCES Users(userID)
);

-- select "create Favorites" as "Action";

CREATE TABLE Favorites (
	tweetID INTEGER 				NOT NULL,
	userID INTEGER 					NOT NULL,
	PRIMARY KEY (tweetID, userID),
	FOREIGN KEY (tweetID) REFERENCES Tweets(tweetID),
	FOREIGN KEY (userID) REFERENCES Users(userID)
);

-- select "create CanSees" as "Action";

CREATE TABLE CanSees (
	tweetID INTEGER				 	NOT NULL,
	userID INTEGER 					NOT NULL,
	PRIMARY KEY (tweetID, userID),
	FOREIGN KEY (tweetID) REFERENCES Tweets(tweetID),
	FOREIGN KEY (userID) REFERENCES Users(userID)
);

-- select "create Messages" as "Action";

CREATE TABLE Messages (
	messageID INTEGER				NOT NULL AUTO_INCREMENT,
	senderID INTEGER 				NOT NULL,
	receiverID INTEGER	 			NOT NULL,
	content VARCHAR(140)			NOT NULL,
	dateTime TIMESTAMP			 	NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (messageID),
	FOREIGN KEY (senderID) REFERENCES Users(userID),
	FOREIGN KEY (receiverID) REFERENCES Users(userID)
);

-- select "create Polls" as "Action";

CREATE TABLE Polls (
	pollID INTEGER NOT NULL AUTO_INCREMENT,
	tweetID INTEGER NOT NULL,
	pollOptionText VARCHAR(300),
	PRIMARY KEY (pollID),
	FOREIGN KEY (tweetID) REFERENCES Tweets(tweetID)
);

-- select "create ContainsHashtag" as "Action";

CREATE TABLE ContainsHashtag (
	tweetID INTEGER NOT NULL,
	content VARCHAR(140) NOT NULL,
	PRIMARY KEY (tweetID, content),
	FOREIGN KEY (tweetID) REFERENCES Tweets(tweetID),
	FOREIGN KEY (content) REFERENCES Hashtags(content)
);