from django.db import models


class Tweets(models.Model):
    class Meta():
        db_table = 'Tweets'
    tweet_date = models.DateField()
    tweet_username = models.CharField(max_length=50)
    tweet_text = models.CharField(max_length=200)
    session_id = models.CharField(max_length=200)
    query = models.CharField(max_length=200)


class Users(models.Model):
    class Meta():
        db_table = 'Users'
    creation_date = models.DateField()
    username = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=50, blank=True)
    friends = models.IntegerField()
    followers = models.IntegerField()
    description = models.CharField(max_length=200, blank=True)
    session_id = models.CharField(max_length=200)
    query = models.CharField(max_length=200)
