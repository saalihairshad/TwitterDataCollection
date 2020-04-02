from tweepy import OAuthHandler
from os import environ as e
import twitter_credentials
import twitter

class TwitterAuthenticator():

    @staticmethod
    def authenticate_twitter_app_for_tweepy():
        """
        Authenticate the credentials for the Tweepy library
        """
        auth = OAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret)
        auth.set_access_token(twitter_credentials.access_token, twitter_credentials.access_token_secret)

        return auth

    @staticmethod
    def authenticate_twitter_app_for_python_twitter():
        """
        Authenticate the credentials for the python-twitter library
        """

        # Set your Twitter  Keys/Secrets
        e["consumer_key"] = twitter_credentials.consumer_key
        e['consumer_secret'] = twitter_credentials.consumer_secret
        e["access_token_key"] = twitter_credentials.access_token
        e['access_token_secret'] = twitter_credentials.access_token_secret


        # Global variables
        auth = twitter.Api(
            consumer_key=e["consumer_key"],
            consumer_secret=e["consumer_secret"],
            access_token_key=e["access_token_key"],
            access_token_secret=e["access_token_secret"],
            sleep_on_rate_limit=True,
            tweet_mode='extended'
        )

        return auth

    @staticmethod
    def get_google_geocode_api_key():
        return twitter_credentials.google_geocode_api_key

