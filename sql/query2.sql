SELECT *
	FROM User
	ORDER BY userID;

SELECT content
	FROM Tweet
	WHERE userID > 5
	ORDER BY tweetID;

SELECT *
	FROM Follows
	WHERE followee < follower
	ORDER BY followee;

SELECT content
	FROM HashTag
	WHERE tweetID > 5;

SELECT senderID, receiverID, content
	FROM Message
	WHERE messageID < 100 AND receiverID > senderID
	LIMIT 3;

SELECT distinct *
	FROM Retweets, Favorites, CanSee, Mentions
	WHERE Retweets.userID = 1 AND Favorites.userID = 2 AND CanSee.userID = 3 AND Mentions.userID = 4;