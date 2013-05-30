-- modifications:
-- insert some users

-- add age and gender to user
ALTER TABLE User
	ADD age INTEGER;

ALTER TABLE User
	ADD sex VARCHAR(10);

-- update the users with random ages and sexes
source userupdate.sql

-- change email address and city of a user
UPDATE User SET email="heynow@yoyo.com" where userID=10;
UPDATE User SET city="Chicago" where userID=100;

-- tweet something
INSERT INTO Tweet (content, userID) VALUES ("I frickin love databases #w00t", 131);
-- add a hashtag
INSERT INTO HashTag (content, tweetID) VALUES ("#w00t", 1234);

-- delete a message
DELETE FROM Message where messageID = 12;