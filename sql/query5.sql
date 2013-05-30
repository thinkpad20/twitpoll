-- all users who have made tweetpolls
select username 
	from User u 
	where u.userID in (
		select t.userID 
		from Tweet t 
		join Poll p 
			on t.tweetID = p.tweetID
	);

-- get all tweets from the first 10 users
select content 
	from Tweet 
	natural join User 
	where User.userID < 10;

-- users who have posted empty tweets
select username, email
	from User 
	left join Tweet
		on User.userID = Tweet.userID 
	where content is null;

-- top 10 users who have posted the most tweetpolls
select userID, count(Tweet.tweetID) as tweetCount 
	from Tweet 
	natural join Poll 
	group by userID 
	order by tweetCount desc 
	limit 10;

-- usernames of those users
select username 
	from User 
	where userID in (
		select userID 
		from Tweet t
		join Poll p
		on t.tweetID = p.tweetID
		group by userID 
		order by count(t.tweetID) desc
	) 
	limit 10;

-- users who have a follower in common
select u1.username, u2.username
	from User u1
	inner join User u2
		on u1.userID <> u2.userID
			and exists (-- follows where u1 is followee intersect follows where u2 is followee
				select * 
					from Follows f1 
					inner join Follows f2 
					on f1.follower = f2.follower
					where f1.followee = u1.userID and f2.followee = u2.userID
				);

-- all users who have been mentioned in a tweet
select username 
	from User u
	where u.userID in (
		select m.userID
		from Tweet t
		join Mentions m
		using (tweetID)
	);

-- all tweets mentioning some username sennachies
select content 
	from Tweet t
	join Mentions m
	using (tweetID)
	where m.userID in (
		select u.userID 
		from User u
		where u.username = "sennachies"
		);