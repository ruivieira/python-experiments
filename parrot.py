"""Markov chain inspired tweets"""
# INFO: Markov chain inspired tweets
import configparser
from typing import List

import markovify  # type: ignore
import tweepy  # type: ignore


class Parrot:
    """Class to generate fake tweets"""

    def __init__(self, api: tweepy.API):
        self._api = api
        self._data: List[str] = []

    def train_user(self, username: str, number: int) -> None:
        """Train the Markov model using a certain user's timeline"""
        public_tweets = self._api.user_timeline(id=username, count=number)

        for parrot_tweet in public_tweets:
            body = parrot_tweet.text
            if not body.startswith("RT "):
                self._data.extend(body.split("\n"))

    def generate(self, number: int) -> List[str]:
        """Generate fake tweets"""
        _model = markovify.Text(". ".join(self._data))
        result = []
        for _ in range(number):
            parrot_tweet = _model.make_short_sentence(280)
            if parrot_tweet:
                result.append(parrot_tweet)
        return result


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("twitter.tokens")

    api_key = config["secrets"]["api_key"]
    api_secret = config["secrets"]["api_secret"]
    consumer_token = config["secrets"]["consumer_token"]
    consumer_secret = config["secrets"]["consumer_secret"]

    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(consumer_token, consumer_secret)

    parrot = Parrot(api=tweepy.API(auth))
    parrot.train_user(username="ruimvieira", number=1000)
    tweets = parrot.generate(20)
    for tweet in tweets:
        print(tweets)
