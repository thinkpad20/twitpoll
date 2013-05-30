-- queries to write:

-- Find the users who have tweeted the most and list their number of tweets
-- Find the user whose tweets have been favorited the most
-- Find the tweet which has been favorited the most
-- Find all tweets which mention some user
-- Show all users who follow a user who has no tweets
--		" 					"		     the most tweets
--		"					"			 the same number of tweets
-- Person who has tweeted the most about their pets

-- all users who have tweeted some hashtag
select u.username, u.userID from User u 
	where u.userID in ( 
		select t.userID from Tweet t, HashTag ht 
		where t.tweetID = ht.tweetID
	);

-- users who have been mentioned
-- all tweets which include a hashtag
-- all tweets which include a mention

-- users who have been followed
select u.username 
	from User u, Mentions m
	where u.userID = m.userID
	;

-- user who has been followed the most
select u.username, count(*) as c 
	from User u, Mentions m 
	where u.userID = m.userID 
	group by u.userID 
	order by c desc 
	limit 1;


-- Aggregation queries:

-- who made the first tweet
select * from User where User.userID in (
	select Tweet.userID from Tweet where tweetID in (
		select min(tweetID) from Tweet
	)
);

-- who signed up the first
select username from User where userID in (
	select min(userID) from User
);

-- what's the average age
select avg(age) from User;

-- what's the average number of tweets
select avg(tweetCount) from (
	select username, count(tweetID) as tweetCount 
	from User u, Tweet t 
	where u.userID = t.userID 
	group by t.userID
) as tweetCounts;

-- whats the smallest number of tweets
select min(tweetCount) from (
	select username, count(tweetID) as tweetCount 
	from User u, Tweet t 
	where u.userID = t.userID
	group by t.userID
) as tweetCounts;

-- who's the youngest person who has a follower
select username, age from User u, Follows f 
	where u.userID = f.followee 
	order by age asc limit 1;

-- all of the users who have made exactly 10 tweets
select username, count(t.tweetID) as tweetCount 
	from User u, Tweet t 
	where u.userID = t.userID 
	group by t.userID 
	having tweetCount = 10;

-- number of messages sent by people living in each state


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
-- select username
-- from User
-- where userID in (
-- 	select userID
-- 	from User u
-- 	inner join Message m
-- 		on m.receiverID = u.userID
-- 		and m.senderID in (
-- 			select userID
-- 			from User
-- 			where username = "userA"
-- 		)
-- )

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













