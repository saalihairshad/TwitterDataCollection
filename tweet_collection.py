from twitter_authenticator import TwitterAuthenticator
from tweet_storage import TwitterStorage
from tweet_thread import TweetThread
from tweepy import API
from tweepy import Cursor
import json
import geocoder
import tweepy
import time
from datetime import datetime


class CollectTweets():
    """
    This class collects Tweets using the Tweepy library.
    Tweepy uses Twitter's Standard Search API to get random Tweets of past 5 to 7 days
    """
    orignal_tweet = []

    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app_for_tweepy()
        self.auth_api = API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.twitter_user = twitter_user
        self.mongoDB = TwitterStorage()
        self.google_api_key = TwitterAuthenticator().get_google_geocode_api_key()

    def tweet_info(self, status):

        """ Prints the tweet information on command-line """

        print('Text: ', status['full_text'])
        print('created at: ', status['created_at'])
        print('Reply By: ', status['user']['screen_name'])
        print('Location: ', status['user']['location'])
        print('Reply to: ', status['in_reply_to_screen_name'])
        print('tweet ID: ', status['id'])
        print('In Reply to status ID: ', status['in_reply_to_status_id_str'])

    def get_original_status(self, status_id):

        """ 
        Recursive method to get the orignal tweet of the user
        
        Takes the recent tweet id and iterate over the tweet ids in  the thread (from bottom to top) to get the original tweet id.
        """
        status = self.auth_api.get_status(status_id, tweet_mode="extended")
        if status.in_reply_to_status_id != None:
            print('In Reply to status ID', status.in_reply_to_status_id)
            status = self.get_original_status(status.in_reply_to_status_id)

        return status

    def get_all_tweets_and_replies(self):

        unique_tweets = 0
        total_tweets = 0
        tweet_thread = TweetThread()
        start = time.time()

        # Pass the Twitter Handel (screen_name) of a Twitter user i.e. @AdobeCare will be AdobeCare
        twitter_accounts = ['AdobeCare', 'SlackHQ', 'LinkedInHelp', 'SpotifyCares', 'snapchatsupport', 'DropboxSupport',
                            'msonenote', 'TeamYouTube', 'evernotehelps', 'googlemaps', 'Netflixhelps']

        for app in twitter_accounts:
            for page in Cursor(self.auth_api.user_timeline, id=app, tweet_mode="extended", count=100).pages(1):
                for i, status in enumerate(page):
                    try:
                        if status.id is None:
                            pass

                        if i:

                            print(f'*************************** TWEET {i} ***************************')

                            if status.in_reply_to_status_id is None:
                                break

                            status_id = status.in_reply_to_status_id
                            status = self.get_original_status(status_id)

                            # Convert from Python dict-like structure to JSON format
                            jsoned_data = json.dumps(status._json)
                            status = json.loads(jsoned_data)

                            # Only get Tweets that are in English and have a Location
                            if status['lang'] == 'en':
                                if status['user']['location'] != "":
                                    print("--------------- USER LOCATION: --------------------",
                                          status['user']['location'])

                                    # insert the information in the database
                                    tweet_collection = self.mongoDB.set_MongoDB_client()
                                    tweet = tweet_collection.find_one({"id": status['id']})

                                    # Store the name of the app/account from which tweets are being collected in the DB
                                    status['app_name'] = app
                                    status['timestamp'] = datetime.now()

                                    # Uncomment next two lines if you want to store the country and country code
                                    # status['country'] = self.get_country(status['user']['location'])[0]
                                    # status['country_code'] = self.get_country(status['user']['location'])[1]

                                    # Only store unique tweets
                                    if tweet is None:
                                        # Insert the tweet in the DB
                                        tweet_collection.insert_one(status)

                                        # Get the replies for the inserted tweet
                                        tweet_thread.main(status['id'], status['user']['screen_name'])
                                        unique_tweets += 1

                                    # Print the info related to tweets on command line
                                    self.tweet_info(status)
                                    total_tweets += 1

                    except tweepy.TweepError as e:
                        print('============= ', e.api_code, ' =============')
                        pass

            # Shows the unique tweets, total tweets and code execution time
            print("unique_tweets: ", unique_tweets)
            print("total_tweets: ", total_tweets)
            print('It took', time.time() - start, 'seconds to execute.')

    def get_country(self, location):

        result = geocoder.google(location, key=self.google_api_key)
        country = result.country_long
        country_code = result.country

        return country, country_code


if __name__ == "__main__":
    collect_tweets = CollectTweets()
    collect_tweets.get_all_tweets_and_replies()
