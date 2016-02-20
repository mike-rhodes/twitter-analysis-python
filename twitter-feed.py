# -*- coding: utf-8 -*-
'''
Created on Oct 17, 2014
Updated on Feb 20, 2016

@author: mrhodes
'''

# Import libraries
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from pymongo import MongoClient
import datetime
import time
import json
import re
import traceback
import tweepy

# Twitter keys
c_key = ''
c_secret = ''
a_token = ''
a_secret = ''

# The keyword we want to pull tweets for
keyword_list = ['mcdonalds', 'chipotle','walmart', 'wendys', 'kfc', 'gas', 'shopping']
twitter_keyword = ','.join(keyword_list)

# Store the tweet in the db (True) or just do a dry run (False)
store_tweet = True
# Should retweets be inluded? Usually no since really popular people tend to be tetweeted a ton.
incl_retweets = False
# Sleep time
sleep_time = 1

# Punctuation to be removed from tweet data
#punc_to_remove = [",", ";", "'", "-", "?", "!", "&", "\"", "(", ")", "@", "#", "|", "\n", "~", "_", ":", "..."]
punc_to_remove = ['\n', '.', '$', '|', '/', '~']

# Set up MongoDB
client = MongoClient()
db = client.tweetdb
collection = db.tweetdata

class listener(StreamListener):
    
    def on_data(self, data):
        
        try:
            # Get tweets and other info using JSON library
            json_data = json.loads(data)
            
            # Save individual tweet data to variables
            the_user_id = json_data["user"]["id"]
            the_username = json_data["user"]["screen_name"].encode("utf-8")
            the_location = json_data["user"]["location"]
            the_user_desc = json_data["user"]["description"]
            the_num_followers = json_data["user"]["followers_count"]
            the_num_retweets = json_data["retweet_count"]
            num_statuses = json_data["user"]["statuses_count"]
            the_tweet = json_data["text"].encode("utf-8")
            num_friends = json_data["user"]["friends_count"]
            user_lang = json_data["user"]["lang"]
            
            #Hashtags - if tweet contains hashtags, then store each one in a list
            if len(json_data["entities"]["hashtags"]) > 0:
                hashtag_list = []
                for i in range(len(json_data["entities"]["hashtags"])):
                    hashtag_list.append(json_data["entities"]["hashtags"][i]["text"])
            else:
                hashtag_list = None
            
            # URLs - Lists of URLs included in the tweet
            if len(json_data["entities"]["urls"]) > 0:
                
                url_list = []
                for i in range(len(json_data["entities"]["urls"])):
                    url_list.append(json_data["entities"]["urls"][i]["url"])
            else:
                url_list = None
                    
            # User mentions - Lists of the other users called out in a tweet
            if len(json_data["entities"]["user_mentions"]) > 0:
                
                mention_list = []
                for i in range(len(json_data["entities"]["user_mentions"])):
                    mention_list.append(json_data["entities"]["user_mentions"][i]["screen_name"])
            else:
                mention_list = None
            # Handle possible missing information for location and user desc. 
            # NOTE: If None is what they have put as their location or description, it will throw an error 
            if (the_location == "" or the_location == None):
                the_location = None
            else:
                the_location = the_location.encode("utf-8")
                the_location = unicode(the_location, errors = 'ignore')
                the_location = re.sub(r' \w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', the_location)
                
            if (the_user_desc == "" or the_user_desc == None):
                the_user_desc = None
            else:
                the_user_desc = the_user_desc.encode("utf-8")
                the_user_desc = unicode(the_user_desc, errors = 'ignore')
                the_user_desc = re.sub(r' \w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', the_user_desc)
            
            # Ignore symbols that can cause errors
            the_username = unicode(the_username, errors = 'ignore')
            the_tweet = unicode(the_tweet, errors = 'ignore')
            
            # Remove links (discarding them for now - don't want to deal with them yet, though they could yield some interesting insights)
            the_username = re.sub(r' \w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', the_username)
            the_tweet = re.sub(r' \w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', the_tweet)
            
            # Remove punctuation
            for i in punc_to_remove:
                the_tweet = the_tweet.replace(i, "")
                if the_location != None:
                    the_location = the_location.replace(i, "")
                if the_user_desc != None:
                    the_user_desc = the_user_desc.replace(i, "")
                    
            # Remove ugly spaces, line breaks/make lower case
            the_tweet = re.sub(r'\s+', ' ', the_tweet)
            the_tweet = the_tweet.lower()
            the_username = re.sub(r'\s+', ' ', the_username)
            the_username = the_username.lower()
            if the_location != None:
                the_location = re.sub(r'\s+', ' ', the_location)
                the_location = the_location.lower()
            if the_user_desc != None:
                the_user_desc = re.sub(r'\s+', ' ', the_user_desc)
                the_user_desc = the_user_desc.lower()

            # Find which keywords matched
            keyword_matches = [x for i, x in enumerate(keyword_list) if x in the_tweet]
            keyword_matches_str = '|'.join(keyword_matches)
            
            # Pring the results on the console
            print "Keyword:", keyword_matches_str
            print "Tweet:", the_tweet
            print "User ID:", the_user_id
            print "Username:", the_username
            print "Location:", the_location
            print "User Description:", the_user_desc
            print "URLs:", url_list
            print "Hashtags:", hashtag_list
            print "Mentions:", mention_list
            
            # Compile the tweet info into a prepared statement
            tweet_info = {"time": datetime.datetime.utcnow(),
                "user_id": the_user_id,
                "username": the_username,
                "user_desc": None if the_user_desc == None else the_user_desc,
                "location": None if the_location == None else the_location,
                "nfollowers": the_num_followers,
                "nretweets": the_num_retweets,
                "tweet": the_tweet,
                "keyword": keyword_matches,
                "user_lang": user_lang,
                "nstatuses": num_statuses,
                "nfriends": num_friends,
                "hashtags": None if hashtag_list == None else hashtag_list,
                "urls": None if url_list == None else url_list,
                "user_mentions": None if mention_list == None else mention_list}
            
            print tweet_info

            # Do we want to include retweets?
            if incl_retweets == True:
                if store_tweet == True:
                    # Insert data into database
                    collection.insert(tweet_info)
                print "-" * 40
                print "\n"
                # Take a quick break so we don't hammer the server
                time.sleep(sleep_time)
            
            # If we dont want to include RTs, then check to see if it is. If it is, then skip it
            else:
                # Is the tweet a RT?
                if the_tweet[:2] == "rt":
                    print "NOTE: Tweet skipped because it was a retweet"
                    print "-" * 40
                    print "\n"
                # If not, store it in the db
                else:
                    if store_tweet == True:
                        # Insert data into database
                        collection.insert(tweet_info)
                    print "-" * 40
                    print "\n"
                    # Take a quick break
                    time.sleep(sleep_time)
            
        except BaseException, e:
            print "Whoops! There was an error!:", str(e)
            print traceback.format_exc()
            print "-" * 40
            print "\n"
        return True
    
    def on_error(self, status):
        print status
        print "-" * 40
        print "\n"
       
# Connect to Twitter
auth = OAuthHandler(c_key, c_secret)
auth.set_access_token(a_token, a_secret)
# auth.set_request_token(a_token, a_secret)

# Stream Tweets
twitterStream = Stream(auth, listener())
twitterStream.filter(track=[twitter_keyword])

'''
# Rate limit info
api = tweepy.API(auth)

rateLimit = api.rate_limit_status()

print json.dumps(rateLimit, indent=4, sort_keys=True)
'''

