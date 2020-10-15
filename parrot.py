"""Markov chain inspired tweets"""
# INFO: Markov chain inspired tweets
import configparser

import markovify  # type: ignore
import tweepy  # type: ignore

config = configparser.ConfigParser()
config.read("twitter.tokens")

api_key = config["secrets"]["api_key"]
api_secret = config["secrets"]["api_secret"]
consumer_token = config["secrets"]["consumer_token"]
consumer_secret = config["secrets"]["consumer_secret"]


auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(consumer_token, consumer_secret)

api = tweepy.API(auth)


public_tweets = api.user_timeline(id="ruimvieira", count=1000)

text = []

for tweet in public_tweets:
    body = tweet.text
    if not body.startswith("RT "):
        text.extend(body.split("\n"))

# Build the model.
text_model = markovify.Text(". ".join(text))

# # Print five randomly-generated sentences
for i in range(20):
    tweet = text_model.make_sentence()
    if tweet:
        print("=" * 80)
        print(tweet)
