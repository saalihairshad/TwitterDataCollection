# Tweet collection Code

This code collects the original tweets and the replies thread from the twitter support accounts. 

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the following libraries.

```bash
pip install tweepy
pip install python-twitter
pip install geocoder
pip install pymongo
```


## Usage

Enter authentication credentials in the ``twitter_credentials.py`` file and replace the following.

* ``consumer_key = "CONSUMER_KEY"`` 
* ``consumer_secret = "CONSUMER_SECRET"``
* ``access_key = "ACCESS_TOKEN"``
* ``access_secret = "ACCESS_TOKEN_SECRET"``

In case, you want to fetch the country from a user's location set Google's Geocode API key in ``twitter_credentials.py``.

``google_geocode_api_key = "GOOGLE_GEOCODE_API_KEY_HERE"``


The code to fetch country from the user's location is commented in ``tweet_collection.py`` because it is a paid service.

