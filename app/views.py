'''
App views
'''

from app import app
from flask import render_template, redirect, url_for, request, make_response
from functools import wraps


def check_auth(username, password):
    '''
    Check if a user is authenticated
    '''
    return username == app.config['USERNAME'] and password == app.config['PASSWORD']


def auth():
    '''
    Request client authentication
    '''
    response = make_response('<h1>Authentication required</h1>', 401)
    response.headers['WWW-Authenticate'] = 'Basic realm="Login Required"'
    return response


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return auth()
        return f(*args, **kwargs)
    return decorated
