from twitter_authenticator import TwitterAuthenticator
from tweet_storage import TwitterStorage
import json
import time
import twitter
import requests
from requests.adapters import HTTPAdapter

s = requests.Session()
s.mount('http', HTTPAdapter(max_retries=3))
s.mount('https', HTTPAdapter(max_retries=3))

try:
    import urllib  # python 2.7
except ImportError:
    import urllib.parse  # python 3


class TweetThread():
    """
    This class fetches replies thread for of the original tweet.

    The code used in this class was taken from https://github.com/gmellini/twitter-scraper and modified accordingly.
    The original code used python-twitter library for fetching the replies.
    """

    def __init__(self, tweet_url=None, tweet_user=None, twitter_id=None, twitter_screen_name=None,
                 short_output=False, ):
        self.t = TwitterAuthenticator().authenticate_twitter_app_for_python_twitter()
        self.tweet_url = tweet_url
        self.tweet_user = tweet_user
        self.twitter_id = twitter_id
        self.twitter_screen_name = twitter_screen_name
        self.short_output = short_output

    def get_tweets(self):

        mongoDB = TwitterStorage()
        for document in mongoDB.fetch_tweets_from_db():
            twitter_screen_name = document['user']['screen_name']
            twitter_id = str(document['id'])
            twitter_json = '{"user":{"screen_name": "' + twitter_screen_name + '"},"id": ' + twitter_id + '}'

            yield twitter.Status.NewFromJsonDict(json.loads(twitter_json))

    def get_replies(self, tweet):

        tweet_user = tweet.user.screen_name
        tweet_id = tweet.id
        max_id = None
        page_index = 0

        while True:
            page_index += 1
            try:
                term = "to:%s" % tweet_user
                replies = self.t.GetSearch(
                    term=term,
                    since_id=tweet_id,
                    max_id=max_id,
                    count=100,
                )
            except twitter.error.TwitterError as e:
                print('[WARNING] Caught twitter api error, sleep for 60s: %s', (e))
                time.sleep(60)
                break

            try:
                for reply in replies:
                    if reply:
                        if reply.in_reply_to_status_id == tweet_id:
                            yield reply

                            # recursive magic to also get replies to the reply
                            for reply_to_reply in self.get_replies(reply):
                                yield reply_to_reply
                        max_id = reply.id

                    max_id = reply.id - 1

                if len(replies) != 100:
                    break

            except twitter.error.TwitterError as e:
                print('------ TWITTER ERROR CODE -------: ', (e))
                pass

    def main(self, twitter_id, twitter_screen_name):

        twitter_json = '{"user":{"screen_name": "' + twitter_screen_name + '"}, "id": ' + str(twitter_id) + '}'
        tweet = twitter.Status.NewFromJsonDict(json.loads(twitter_json))

        if twitter_id is not None:
            tabs = ''
            last = None
            reply_count = 0

            thread_replies = []
            for reply in self.get_replies(tweet):

                j = json.loads(reply.AsJsonString())
                thread_replies.append(j)

                if int(reply.in_reply_to_status_id) == int(twitter_id):
                    tabs = ''
                elif int(reply.in_reply_to_status_id) == int(last):
                    tabs = '%s  ' % tabs
                else:
                    tabs = '%s\b\b' % tabs

                last = j['id']

                reply_count += 1

            mongoDB = TwitterStorage()
            tweet_collection = mongoDB.set_MongoDB_client()

            tweet_collection.update({"id": tweet.id}, {"$set": {"replies": thread_replies}, })

            if not self.short_output:
                print('')
                print('[INFO] Total replies: %s' % reply_count)

        if not self.short_output: print('========================================================================')
