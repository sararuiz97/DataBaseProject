import tweepy
import json
from tweepy import OAuthHandler

consumer_key = 'A1Pn5OSpVOpXuKV9Blz8xKvKP'
consumer_secret = 'QVJXB5XwF3AkOjZ83HJi3mK9n9icrArgGJXZxcZP01lzZZOsaU'
access_token = '70217990-LkSAiEc4UHjSQvQGVacKl21qzDQoA2m4QVpxdVEym'
access_secret = 'pLuYblWKcSSMSYzEexenxfuHT7RDpfcGNidxsDWL63Qab'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
auth.secure = True

api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)

def process_or_store(tweet):
    print(json.dumps(tweet))

for tweet in tweepy.Cursor(api.home_timeline).items(5):
    #print(tweet)
    process_or_store(tweet.json)
