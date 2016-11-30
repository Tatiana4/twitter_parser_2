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
def get_user_info(tweet):
    u = {}
    user_created_at = datetime.strptime((tweet._json.get('user').get('created_at')), '%a %b %d %X %z %Y')
    u['user'] = tweet._json.get('user').get('screen_name')
    u['name'] = tweet._json.get('user').get('name')
    u['location'] = tweet._json.get('user').get('location')
    u['friends'] = tweet._json.get('user').get('friends_count')
    u['followers'] = tweet._json.get('user').get('followers_count')
    u['creation_date'] = user_created_at.strftime('%Y-%m-%d')
    u['description'] = tweet._json.get('user').get('description')
    users_info.append(u)


# выборка твитов по ключевым словам
def get_tweets_by_query(*args):
    # если дата не введена
    if len(args) == 3:
        query = args[0]
        count = args[1]
        result = args[2]

        for tweet in tweepy.Cursor(api.search, q=query, result_type=result).items(count):
            t = {}
            created_at = datetime.strptime((tweet._json.get('created_at')), '%a %b %d %X %z %Y')
            t['name'] = tweet._json.get('user').get('screen_name')
            t['creation_date'] = created_at.strftime('%Y-%m-%d')
            t['creation_time'] = created_at.strftime('%X')
            t['text'] = tweet._json.get('text')
            tweets.append(t)

            get_user_info(tweet)

    # если дата введена
    else:
        query = args[0]
        count = args[1]
        result = args[2]
        until = args[3]

        for tweet in tweepy.Cursor(api.search, q=query, result_type=result, until=until).items(count):
            t = {}
            created_at = datetime.strptime((tweet._json.get('created_at')), '%a %b %d %X %z %Y')
            t['name'] = tweet._json.get('user').get('screen_name')
            t['creation_date'] = created_at.strftime('%Y-%m-%d')
            t['creation_time'] = created_at.strftime('%X')
            t['text'] = tweet._json.get('text')
            tweets.append(t)

            get_user_info(tweet)
