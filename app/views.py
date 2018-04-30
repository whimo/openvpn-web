'''
App views
'''

from app import app
from flask import render_template, redirect, url_for, request, make_response, send_from_directory
from functools import wraps
import os.path
import subprocess


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


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return auth()
        return f(*args, **kwargs)
    return decorated


@app.route('/clients/<str:name>/download')
@auth_required
def download_client(name):
    return send_from_directory(app.config['CLIENTS_DIR'], '{}.ovpn'.format(name))


@app.route('/clients/<str:name>', methods=['GET'])
@auth_required
def get_client(name):
    if not os.path.exists(os.path.join(app.config['CLIENTS_DIR'], '{}.ovpn').format(name)):
        return '<h2>Client not found</h2>', 404

    return render_template('client.html', name=name)
