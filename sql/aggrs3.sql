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

-- number of tweets by people living in each state
select state, count(tweetID) as tweetCount 
from User u 
inner join Tweet t 
	on u.userID = t.userID 
group by state;

-- number of followers of user "teschenite"
select count(*) from Follows f where f.followee in (select userID from User where username = "teschenite");



