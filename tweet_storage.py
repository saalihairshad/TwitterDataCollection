import pymongo
from pymongo import MongoClient


class TwitterStorage():

    """
    This class sets up the database client 
    The current implementation uses MongoDB 
    """

    def set_MongoDB_client(self):
       
        # Set up the MongoDB client   
        client = MongoClient()

        # Specify the database 
        db = client.tweet_db

        # Specify the one or more collections for the database 
        tweet_collection = db.tweets
      
        # Creates a unique document in the DB collection
        tweet_collection.create_index([("id", pymongo.ASCENDING)], unique=True)
        
        return tweet_collection
        
    def fetch_tweets_from_db(self):
        tweet_collection = self.set_MongoDB_client()
        return tweet_collection.find()






