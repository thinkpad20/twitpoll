-- Join queries

-- list all tweets and users who tweeted them
select username, dateTime, content
	from User natural join Tweet;

-- list all tweets made by users older than 15
select username, content, age
	from User join Tweet using(userID)
	where age > 15;

-- list all users who user snidesttided has favorited the tweets of
select u.username 
from Favorites f 
inner join Tweet t on f.tweetID = t.tweetID 
inner join User u on u.userID = t.userID 
where f.userID in (select userID from User where username = "snidesttided");


-- list all tweets who user 1995 has favorited
select * from Tweet where Tweet.tweetID in (
	select f.tweetID from User join Favorites f using(userID) where userID = 1995
);

-- list all users to whom user "userA" has sent a message
select username 
	from User u 
	inner join Message m on m.receiverID = u.userID
	where m.senderID = (select userID from User where username = "userA")

-- list all pairs of users who have the same age and are male
select u1.username, u2.username 
	from User u1 join User u2 on (
		u1.age = u2.age and u1.sex ='Male' and u2.sex ='Male' and u1.userID < u2.userID
	);

-- list all messages cohabiting sent to user morphemics
select u2.username, u1.username, m.content 
from Message m 
inner join User u1 on m.receiverID = u1.userID 
inner join User u2 on m.senderID = u2.userID
where u1.username = "morphemics" and u2.username = "cohabiting";

-- given two users, list all of the people they both follow
select username
from User
where userID in (
	select f.followee
	from Follows f
	inner join User u1 on f.follower = u1.userID
	where u1.username = "userA"
)
and userID in (
	select f.followee
	from Follows f
	inner join User u1 on f.follower = u1.userID
	where u1.username = "userB"
);

-- find all of the tweets containing hashtag "#ankers"
select distinct * 
from Tweet 
inner join HashTag 
	on HashTag.tweetID = Tweet.tweetID 
	and HashTag.content = "#ankers";
