#!/usr/bin/env python3
import os
from time import sleep

import pandas as pd
import tweepy as tw


# creating variables for credentials
consumer_key = '37gwjesvZbRmoJQVBxP9nvrwq'
consumer_secret = '8dKpWgrW2wU47oYWl6ZBhvzqIWorbBGaUczSwBiua9hqXofQzP'
access_token = '186349231-5XXE6gokfKCz5k6lYMKummQTBQ8BtBfKyb8hSkQN'
access_token_secret = 'uL3XVUqhdwFyXW4QYby3btIVFwVlMfXYAugcgmIG69RQJ'
# Creating an OAuthHandler instance
auth = tw.OAuthHandler(consumer_key, consumer_secret)
# Setting the app access token
auth.set_access_token(access_token, access_token_secret)
# Creating an API object
api = tw.API(auth, wait_on_rate_limit=True)
me = api.me()


# Like a tweet
def like_tweet():
    tweets = api.home_timeline(count=5)
    tweet = tweets[0]
    print(f"Liking tweet {tweet.id} of {tweet.author.name}")
    api.create_favorite(tweet.id)
    if tweet.in_reply_to_status_id is not None or tweet.user.id == me.id:
        # This tweet is a reply or I'm its author so, ignore it
        return
    if not tweet.favorited:
        # Mark it as Liked, since we have not done it yet
        try:
            tweet.favorite()
        except Exception as e:
            print("Error on fav", e.args)


def get_tweets():
    for tweet in tw.Cursor(api.home_timeline).items(100):
        print(f"{tweet.user.name} said: {tweet.text}")


# Follow followers
def follow_followers():
    print("Retrieving and following followers")
    for follower in tw.Cursor(api.followers).items():
        if not follower.following:
            print(f"Following {follower.name}")
            follower.follow()


# Follow followers
def unfollow():
    print("Unfollow process starts")
    followers_list = [follower for follower in tw.Cursor(api.followers_ids).items()]
    for friend in tw.Cursor(api.friends).items():
        if input("Do you want to cancle the unfollow process: Y/N?") == 'y' or 'Y':
            break
        elif friend not in followers_list:
            "Unfollow {0}?".format(api.get_user(friend).screen_name)
            if input("Y/N?") == 'y' or 'Y':
                api.destroy_friendship(friend)


# Check tweets where you are mentioned and reply to it
def check_mentions(keywords, since_id):
    print("Retrieving mentions")
    new_since_id = since_id
    for tweet in tw.Cursor(api.mentions_timeline, since_id=since_id).items():
        new_since_id = max(tweet.id, new_since_id)
        if tweet.in_reply_to_status_id is not None:
            continue
        if any(keyword in tweet.text.lower() for keyword in keywords):
            print(f"Answering to {tweet.user.name}")
            if not tweet.user.following:
                tweet.user.follow()
            api.update_status(
                status="Please reach us via DM",
                in_reply_to_status_id=tweet.id,
            )
    return new_since_id


# Send direct message to a tweet
def send_direct_message(tweet, message):
    api.send_direct_message(recipient_id=tweet.user.id, text=message)


# Welcome message
def welcome_message():
    wm_text = 'Hi! Thanks for following.'
    new_followers = api.followers_ids()
    with open('TwitterFollowers.csv', 'r+') as follower_file:
        old_followers = follower_file.read()
    print("Followers count:", len(old_followers))
    # If new_follower is not in old follower, send him welcome message and save him
    for follower in new_followers:
        if follower not in old_followers:
            api.send_direct_message(recipient_id=follower, text=wm_text)
            # Save the followers to csv
            save_followers(follower=follower)


# Save the followers to csv
def save_followers(follower):
    follower = follower
    # Save the followers to csv
    df = pd.DataFrame({"Follower": follower})
    # if file does not exist write header
    if not os.path.isfile('TwitterFollowers.csv'):
        df.to_csv('TwitterFollowers.csv', index=None)
    else:  # else if exists so append without writing the header
        df.to_csv('TwitterFollowers.csv', mode='a', header=False, index=None)


if __name__ == '__main__':
    since_ids = [1]
    is_started = False
    with open('TwitterKeywords.txt', 'r+') as keyword_file:
        keywords = keyword_file.read()
        keyword_list = keywords.split(',')
    while True:
        if not is_started:
            followers = tw.Cursor(api.followers).items()
            save_followers(follower=followers)
        like_tweet()
        follow_followers()
        unfollow()
        welcome_message()
        check_mentions(keywords=keyword_list, since_id=since_ids[-1])

