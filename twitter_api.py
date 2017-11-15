import time
import sys
import tweepy
from json import dumps, dump
from tweepy import OAuthHandler

consumer_key = 'A1Pn5OSpVOpXuKV9Blz8xKvKP'
consumer_secret = 'QVJXB5XwF3AkOjZ83HJi3mK9n9icrArgGJXZxcZP01lzZZOsaU'
access_token = '70217990-LkSAiEc4UHjSQvQGVacKl21qzDQoA2m4QVpxdVEym'
access_secret = 'pLuYblWKcSSMSYzEexenxfuHT7RDpfcGNidxsDWL63Qab'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
auth.secure = True

api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True, parser=tweepy.parsers.JSONParser())


from py2neo import Graph, authenticate

authenticate("localhost:7474", "neo4j", "guereca1996")

graph_db = Graph("http://localhost:7474/db/data")

def post_tweets(hashtag_string):

    try:
        graph_db.run("""
            CREATE CONSTRAINT ON (t:Tweet) ASSERT t.id IS UNIQUE
            CREATE CONSTRAINT ON (u:User) ASSERT u.screen_name IS UNIQUE
            CREATE CONSTRAINT ON (h:Hashtag) ASSERT h.name IS UNIQUE
            CREATE CONSTRAINT ON (l:Link) ASSERT l.url IS UNIQUE
            CREATE CONSTRAINT ON (s:Source) ASSERT s.name IS UNIQUE
        """)
    except:
        pass

    tweets = api.search(q = hashtag_string,rpp = 100, count=1000)["statuses"]

    query_string = """
    UNWIND {tweets} AS t
    WITH t
    ORDER BY t.id

    WITH t,
        t.entities AS e,
        t.user AS u,
        t.retweeted_status AS retweet
    MERGE (tweet:Tweet {id:t.id})
    SET tweet.text = t.text,
        tweet.created_at = t.created_at,
        tweet.favorites = t.favorites_count

    MERGE (user:User {screen_name:u.screen_name})
    SET user.name = u.name,
        user.location = u.location,
        user.followers = u.followers_count,
        user.following = u.friends_count,
        user.statuses = u.statusus_count,
        user.profile_image_url = u.profile_image_url

    MERGE (user)-[:POSTS]->(tweet)

    MERGE (source:Source {name:t.source})
    MERGE (tweet)-[:USING]->(source)

    FOREACH (h IN e.hashtags |
        MERGE (tag:Hashtag {name:LOWER(h.text)})
        MERGE (tag)-[:TAGS]->(tweet)
    )

    FOREACH (u IN e.urls |
        MERGE (url:Link {url:u.expanded_url})
        MERGE (tweet)-[:CONTAINS]->(url)
    )

    FOREACH (m IN e.user_mentions |
        MERGE (mentioned:User {screen_name:m.screen_name})
        ON CREATE SET mentioned.name = m.name
        MERGE (tweet)-[:MENTIONS]->(mentioned)
    )

    FOREACH (r IN [r IN [t.in_reply_to_status_id] WHERE r IS NOt NULL] |
        MERGE (reply_tweet:Tweet {id:r})
        MERGE (tweet)-[:REPLY_TO]->(reply_tweet)
    )

    FOREACH (retweet_id IN [x IN [retweet.id] WHERE x IS NOt NULL] |
        MERGE (reply_tweet:Tweet {id:retweet_id})
        MERGE (tweet)-[:RETWEETS]->(retweet_tweet)
    )
    """
    graph_db.run(query_string, {'tweets':tweets})
    print("Tweets added to graph!\n")

def get_JSON(hashtag_string):

    req_query= """
    MATCH p=(n:Hashtag {name:'"""+hashtag_string.lower()+"""'})-[r*]->(m) where NONE( rel in r WHERE type(rel)="RETWEETS") RETURN n as Tweet, extract(x IN rels(p)| type(x)) AS types, m as Related LIMIT 150
    """

    print (req_query)

    query = graph_db.run(req_query).data()
    test = dumps(query, sort_keys=True, indent=4, separators=(',', ': '))

    with open('data.txt', 'w') as outfile:
        dump(query, outfile)
    #print (test)
    return(test)
