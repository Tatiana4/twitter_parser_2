from datetime import datetime
import tweepy


# авторизация в апи твиттера
def auth(consumer_key, consumer_secret, access_token, access_token_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    global api
    api = tweepy.API(auth)
    return api

tweets = []
users_info = []


# получение информации о пользователях
def get_user_info(username):
    u = {}
    user = api.get_user(username)._json
    user_created_at = datetime.strptime((user.get('created_at')), '%a %b %d %X %z %Y')
    u['user'] = user.get('screen_name')
    u['name'] = user.get('name')
    u['location'] = user.get('location')
    u['friends'] = user.get('friends_count')
    u['followers'] = user.get('followers_count')
    u['creation_date'] = user_created_at.strftime('%Y-%m-%d')
    u['description'] = user.get('description')
    return users_info.append(u)


# выборка твитов
def get_tweets_of_user(*args):
    # все твиты пользователей
    if len(args) == 1:
        username_list = args[0]

        for username in username_list:
            for tweet in tweepy.Cursor(api.user_timeline, username).items():
                t = {}
                created_at = datetime.strptime((tweet._json.get('created_at')), '%a %b %d %X %z %Y')
                t['name'] = username
                t['creation_date'] = created_at.strftime('%Y-%m-%d')
                t['creation_time'] = created_at.strftime('%X')
                t['text'] = tweet._json.get('text')
                tweets.append(t)

            get_user_info(username)

    # заданное количество твитов
    else:
        username_list = args[0]
        count = args[1]

        for username in username_list:
            for tweet in tweepy.Cursor(api.user_timeline, username).items(count):
                t = {}
                created_at = datetime.strptime((tweet._json.get('created_at')), '%a %b %d %X %z %Y')
                t['name'] = username
                t['creation_date'] = created_at.strftime('%Y-%m-%d')
                t['creation_time'] = created_at.strftime('%X')
                t['text'] = tweet._json.get('text')
                tweets.append(t)

            get_user_info(username)
