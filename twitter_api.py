import re
import time
import sys
import tweepy
import os
from json import dumps, dump, loads
from tweepy import OAuthHandler
from textblob import TextBlob
from graph import *

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

def clean_tweet(tweet):

    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

def get_tweet_sentiment(tweet):

    analysis = TextBlob(clean_tweet(tweet))
    # set sentiment
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'

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

    tweets = api.search(q = hashtag_string,rpp = 1000, count=1000)["statuses"]

    print(tweets)

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

    users_tweets_query= """
    MATCH (n:User)-[r:POSTS]->(m:Tweet) where  NOT (m)-[:RETWEETS]->()
    MATCH (p:Hashtag {name:'"""+hashtag_string.lower()+"""'})-[:TAGS]->(m)
    RETURN type(r) as type, m.id as tweet_id,  m.text as tweet_text, n.screen_name as screen_name, n.name as name, n.followers as followers, n.following as following LIMIT 100
    """

    mentions_tweets_query= """
    MATCH (n:User)<-[r:MENTIONS]-(m:Tweet) where  NOT (m)-[:RETWEETS]->()
    MATCH (p:Hashtag {name:'"""+hashtag_string.lower()+"""'})-[:TAGS]->(m)
    RETURN type(r) as type, m.id as tweet_id,  m.text as tweet_text, n.screen_name as screen_name, n.name as name, n.followers as followers, n.following as following ORDER BY tweet_id LIMIT 150
    """

    query_users = graph_db.run(users_tweets_query).data()
    query_mentions = graph_db.run(mentions_tweets_query).data()

    query_users_string = dumps(query_users, sort_keys=True, indent=2, separators=(',', ': '))
    query_mentions_string = dumps(query_mentions, sort_keys=True, indent=2, separators=(',', ': '))

    #print(query_users_string)
    #print(query_mentions_string)

    g = graph()
    opJson = {"links":[], "nodes":[]};

    g.insert(Node(hashtag_string))

    for item in query_users:
        g.insert(Node(item['tweet_text']))
        g.insert(Node(item['screen_name']))
        g.nodes[item['screen_name']].insertAdj(g.nodes[item['tweet_text']], 5)
        g.nodes[hashtag_string].insertAdj(g.nodes[item['tweet_text']], 5)

    for item in query_users:
        for user in query_mentions:
            if (user['tweet_text'] == item['tweet_text']):
                g.insert(Node(user['screen_name']))
                g.nodes[item['screen_name']].insertAdj(g.nodes[user['tweet_text']], 5)

    k = g.nodes.keys()
    for i in range(5):
        for key in k:
            g.nodes[key].updateRank(0.85)

    first = 0

    for item in query_users:
        #print(get_tweet_sentiment(item['tweet_text']))
        opJson["nodes"].append({"group":"00E6DD", "name":item['tweet_text'] + "<br>Impact: " + get_tweet_sentiment(item['tweet_text']), "r":g.nodes[item['tweet_text']].rank})
        first += 1

    counter = 0

    for item in query_users:
        opJson["nodes"].append({"group":"FFA900", "name":"Screen name: " + item['screen_name'] + "<br>Name: " + item['name'] + "<br>Followers: " + str(item['followers']) + "<br>Following: " + str(item['following']), "r":g.nodes[item['screen_name']].rank})
        opJson["links"].append({"source":counter,"target":first,"weight":1})
        counter += 1
        first += 1

    tweet = 0

    for item in query_users:
        for user in query_mentions:
            if (item['tweet_id'] == user['tweet_id']):
                opJson["nodes"].append({"group":"FF7100", "name":"Screen name: " + item['screen_name'] + "<br>Name: " + item['name'] + "<br>Followers: " + str(item['followers']) + "<br>Following: " + str(item['following']), "r":g.nodes[item['screen_name']].rank})
                opJson["links"].append({"source":tweet,"target":first,"weight":1})
                first += 1
        tweet += 1

    opJson["nodes"].append({"group":"000000", "name":hashtag_string, "r":g.nodes[hashtag_string].rank})
    more = 0

    for item in query_users:
        opJson["links"].append({"source":first,"target":more,"weight":1})
        more += 1

    with open('templates/graphFile.json', "a+") as outfile:
        outfile.seek(0)
        outfile.truncate()
        dump(opJson, outfile)

    outfile.closed

    return(query_users_string)
