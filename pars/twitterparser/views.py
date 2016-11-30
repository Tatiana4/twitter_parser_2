import os
import mimetypes
from datetime import timedelta, date
import glob2
import tweepy
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.template.context_processors import csrf
from .forms import ApiForm, SearchByUser, SearchByQuery
from .utils import *
from . import parser_by_query, parser_by_list


def begin(request):
    if request.POST:
        key_form = ApiForm(request.POST)
        if key_form.is_valid():
            keys = key_form.cleaned_data
            # сохраняем ключи в сессии
            request.session['apikey'] = keys['apikey']
            request.session['apisecret'] = keys['apisecret']
            request.session['token'] = keys['token']
            request.session['tokensecret'] = keys['tokensecret']
            # устанавливаем время жизни сессии 1 час
            request.session.set_expiry(60 * 60)
            return redirect('search/')

    else:
        key_form = ApiForm()

    return render(request, 'begin.html', {'key_form': key_form})


def search(request):
    args = {}
    args.update(csrf(request))
    errors = []

    if request.POST:
        # вытаскиваем ключи из сессии
        consumer_key = request.session.get('apikey')
        consumer_secret = request.session.get('apisecret')
        access_token = request.session.get('token')
        access_token_secret = request.session.get('tokensecret')

        session_id = request.session.session_key

        user_form = SearchByUser(request.POST)
        query_form = SearchByQuery(request.POST)

        # проверяем, заполнены ли поля формы поиска по пользователю
        if user_form.is_valid() and user_form.has_changed():
            params = user_form.cleaned_data
            usernames = params['usernames'].split(', ')
            count = params['count']

            # запретим пользователю вводить список более 5 юзернеймов
            if len(usernames) <= 5:
                if count is None:
                    # если количество не задано, парсим все твитты
                    try:
                        # авторизуем пользователя в апи твиттера и выполняем выборку
                        parser_by_list.auth(consumer_key, consumer_secret,
                                            access_token, access_token_secret)
                        parser_by_list.get_tweets_of_user(usernames)

                        # пишем выборку в БД, формируем файл
                        tweets = parser_by_list.tweets
                        users = parser_by_list.users_info

                        add_to_db(tweets, users, session_id, usernames)

                        parser_by_list.tweets = []
                        parser_by_list.users_info = []

                        make_file(session_id, usernames)

                    except tweepy.TweepError as e:
                        # на тот случай, если при вводе имени допущена ошибка
                        if int((str(e).split('= '))[-1]) == 404:
                            errors.append('Пользователь не найден')
                else:
                    try:
                        # авторизуем пользователя в апи твиттера и выполняем выборку
                        parser_by_list.auth(consumer_key, consumer_secret,
                                            access_token, access_token_secret)
                        parser_by_list.get_tweets_of_user(usernames, count)

                        # пишем выборку в БД, формируем файл
                        tweets = parser_by_list.tweets
                        users = parser_by_list.users_info

                        add_to_db(tweets, users, session_id, usernames)

                        parser_by_list.tweets = []
                        parser_by_list.users_info = []

                        make_file(session_id, usernames)

                    except tweepy.TweepError as e:
                        # на тот случай, если при вводе имени допущена ошибка
                        if int((str(e).split('= '))[-1]) == 404:
                            errors.append('Пользователь не найден')

            else:
                errors.append('Слишком большой список пользователей. Оставьте 5 или меньше.')

            if not errors:
                return redirect('/result/')
            else:
                return render(request, 'search.html',
                              {'user_form': user_form, 'query_form': query_form, 'errors': errors})

        # если поиск по пользователю пуст, проверяем поля формы поиска по ключевым словам
        elif query_form.is_valid() and query_form.has_changed():
            params = query_form.cleaned_data
            query = params['query']
            count1 = params['count1']
            result_type = params['result_type']
            until = params['date']

            # если дата введена
            if until is not None:
                # проверяем введенную дату
                now = date.today()
                delta = now - until
                min_delta = timedelta(days=7)

                if delta < min_delta:
                    # авторизуем пользователя в апи твиттера и выполняем выборку
                    parser_by_query.auth(consumer_key, consumer_secret,
                                         access_token, access_token_secret)
                    parser_by_query.get_tweets_by_query(query, count1, result_type, until)

                    tweets = parser_by_query.tweets
                    users = parser_by_query.users_info

                    add_to_db(tweets, users, session_id, query)

                    parser_by_query.tweets = []
                    parser_by_query.users_info = []

                    make_file(session_id, query)

                else:
                    errors.append('Введенная дата старше 1 недели')

            # если дата не введена
            else:
                # авторизуем пользователя в апи твиттера и выполняем выборку
                parser_by_query.auth(consumer_key, consumer_secret,
                                     access_token, access_token_secret)
                parser_by_query.get_tweets_by_query(query, count1, result_type)

                tweets = parser_by_query.tweets
                users = parser_by_query.users_info

                add_to_db(tweets, users, session_id, query)

                parser_by_query.tweets = []
                parser_by_query.users_info = []

                make_file(session_id, query)

            if not errors:
                return redirect('/result/')
            else:
                return render(request, 'search.html',
                              {'user_form': user_form, 'query_form': query_form, 'errors': errors})

    else:
        user_form = SearchByUser(request.POST)
        query_form = SearchByQuery(request.POST)

    return render(request, 'search.html', {'user_form': user_form, 'query_form': query_form})


def result(request):
    return render(request, 'result.html')


def download(request):
    # находим сформированный файл, отдаем его на скачивание и удаляем
    fname = glob2.glob('*.zip')[0]
    f = open(fname, 'rb')
    response = HttpResponse(f.read())
    f.close()
    file_type = mimetypes.guess_type(fname)
    if file_type is None:
        file_type = 'application/octet-stream'
    response['Content-Type'] = file_type
    response['Content-Length'] = str(os.stat(fname).st_size)
    response['Content-Disposition'] = "attachment; filename=output.zip"
    os.remove(fname)
    return response


def how_to(request):
    return render(request, 'how_to.html')
