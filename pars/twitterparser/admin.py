from django.contrib import admin
from .models import Tweets
from .models import Users


admin.site.register(Tweets)
admin.site.register(Users)
