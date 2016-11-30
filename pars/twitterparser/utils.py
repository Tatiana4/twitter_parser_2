import os
from datetime import datetime
import zipfile
import pandas
from djqscsv import write_csv
from .models import Tweets, Users


def add_to_db(tweets, users, session_id, query):
    # пишем в БД выборку твиттов
    for t in tweets:
        tweet = Tweets()
        tweet.tweet_text = t['text']
        tweet.tweet_date = t['creation_date']
        tweet.tweet_username = t['name']
        tweet.session_id = session_id
        tweet.query = query
        tweet.save()

    # пишем в БД инфу о юзерах
    for u in users:
        user = Users()
        user.username = u['user']
        user.name = u['name']
        user.location = u['location']
        user.friends = u['friends']
        user.followers = u['followers']
        user.description = u['description']
        user.creation_date = u['creation_date']
        user.session_id = session_id
        user.query = query
        user.save()


def make_file(session_id, query):
    # делаем выборку из БД и сохраняем в csv
    users_set = Users.objects.filter(query=query,
                                     session_id=session_id).values('creation_date', 'username', 'name',
                                                                   'location', 'friends', 'followers',
                                                                   'description')
    with open('users.csv', 'ab') as csv_file:
        write_csv(users_set, csv_file)

    tweets_set = Tweets.objects.filter(query=query,
                                       session_id=session_id).values('tweet_date', 'tweet_username',
                                                                     'tweet_text')
    with open('tweets.csv', 'ab') as csv_file:
        write_csv(tweets_set, csv_file)

    name = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    tweets_df = pandas.read_csv('tweets.csv')
    user_info_df = pandas.read_csv('users.csv')
    with pandas.ExcelWriter(name + '.xlsx') as writer:
        tweets_df.to_excel(writer, sheet_name='tweets')
        user_info_df.to_excel(writer, sheet_name='user_info')
    with zipfile.ZipFile(name + '.zip', 'w') as zip:
        zip.write(name + '.xlsx')
    os.remove(name + '.xlsx')
    os.remove('tweets.csv')
    os.remove('users.csv')
