import time
import sys

####
# Get tweepy set up
import tweepy
from tweepy import Cursor

consumer_key="A1Pn5OSpVOpXuKV9Blz8xKvKP"
consumer_secret="QVJXB5XwF3AkOjZ83HJi3mK9n9icrArgGJXZxcZP01lzZZOsaU"
access_token="70217990-LkSAiEc4UHjSQvQGVacKl21qzDQoA2m4QVpxdVEym"
access_token_secret="pLuYblWKcSSMSYzEexenxfuHT7RDpfcGNidxsDWL63Qab"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

####
# Get neo4j set up
from py2neo import Graph, authenticate

# Remember to change these credentials if you've changed the default User/Pass.
# Also, this assumes you have neo4j running on the default port on localhost
authenticate("localhost:7474", "neo4j", "guereca1996")

graph_db = Graph("http://localhost:7474/db/data")

####
# End of boilerplate, interesting code starts here:
try:
	graph_db.run("""
        CREATE CONSTRAINT ON (u:User)
        ASSERT u.id_str IS UNIQUE
    """)
except:
    pass

def create_or_get_node(tweet_with_hashtag,labels=[]):
    data = {'id_str': tweet_with_hashtag.id_str,
        'user': tweet_with_hashtag.user.screen_name,
        'created_at': tweet_with_hashtag.created_at,
		'hashtags': tweet_with_hashtag.entities['hashtags'][0]['text'],
        'text': tweet_with_hashtag.text,
        'lang': tweet_with_hashtag.lang,
    }
    query_string = """
        MERGE (u:Status {id_str:{id_str}})
        ON CREATE SET
"""+   (('u:'+',u:'.join(labels)+",") if labels else '') +"""
            u.user={user},
            u.created_at={created_at},
			u.hashtags={hashtags},
            u.text={text},
            u.lang={lang},
""" +   (("ON MATCH SET\n  u:"+',u:'.join(labels)) if labels else '') +"""
        RETURN u
    """
    n=graph_db.run(query_string, parameters=None, **data)
    return n


def insert_user_with_friends(hashtag,labels=[]):
    if isinstance(hashtag, str):
    create_or_get_node(tweet_with_hashtag,user_labels)
    hashTweet = Cursor(api.friends, user_id=twitter_user.id_str, count=200).items()
    try:
		for tweet_with_hashtag in hashTweet:
			try:
                create_or_get_node(tweet_with_hashtag,labels)
            except tweepy.TweepError:
                print("exceeded rate limit. waiting")
                time.sleep(60 * 16)
            n=graph_db.run("""
                MATCH (hashtag:Status {id_str:{user_id_str}}),(friend:User {id_str:{friend_id_str}})
                CREATE UNIQUE (user)-[:FOLLOWS]->(friend)
            """, parameters=None, user_id_str=twitter_user.id_str, friend_id_str=friend.id_str)
    except StopIteration:
        print(u"\n    Total Friend Count = {}".format(friend_count))




# Add me and all my colleagues to the db along with all of our friends.
insert_user_with_friends('softwaredoug',["OSC"])
insert_user_with_friends('jnbrymn',["OSC","Neo"])
insert_user_with_friends('patriciagorla',["OSC"])
insert_user_with_friends('scottstults',["OSC"])
insert_user_with_friends('dep4b',["OSC","Neo"])
insert_user_with_friends('o19s',["OSC"])
insert_user_with_friends('jwoodell',["OSC"])
insert_user_with_friends('omnifroodle',["OSC"])
insert_user_with_friends('danielbeach',["OSC"])


# Add prominent Neo folks and those they follow
insert_user_with_friends('neo4j',["Neo"])
insert_user_with_friends('mesirii',["Neo"])
insert_user_with_friends('emileifrem',["Neo"])
insert_user_with_friends('jimwebber',["Neo"])
insert_user_with_friends('peterneubauer',["Neo"])
insert_user_with_friends('p3rnilla',["Neo"])
insert_user_with_friends('maxdemarzi',["Neo"])
insert_user_with_friends('rvanbruggen',["Neo"])
insert_user_with_friends('wefreema',["Neo"])
insert_user_with_friends('ayeeson',["Neo"])
insert_user_with_friends('akollegger',["Neo"])
insert_user_with_friends('markhneedham',["Neo"])
insert_user_with_friends('technige',["Neo"])

# Add the guy that made this stuff work with Python 3.4 and neo4j 2.x
insert_user_with_friends('hwaldstein1997',["CoolGuy"])

#Now you add yourself and add those that you find interesting.
