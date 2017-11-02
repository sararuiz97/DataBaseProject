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

hashTweet = tweepy.Cursor(api.search, q='Happiest5WordSentence').items(1)

print (api.get_user("drag0409"))

for tweet in hashTweet:
    print("\n")
    print(tweet)
    #print (tweet.id_str)
    #print (tweet.user.screen_name)
    #print (tweet.created_at)
    #print (tweet.entities['hashtags'][0]['text'])
    #print (tweet.text)
    #print (tweet.lang)
