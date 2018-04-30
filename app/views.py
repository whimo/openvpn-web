'''
App views
'''

from app import app
from flask import render_template, redirect, url_for, request, make_response, send_from_directory, flash
from functools import wraps
import os.path
from subprocess import Popen


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


@app.route('/clients/<str:name>/download', methods=['GET'])
@auth_required
def download_client(name):
    return send_from_directory(app.config['CLIENTS_DIR'], '{}.ovpn'.format(name))


@app.route('/clients/<str:name>/delete', methods=['GET'])
@auth_required
def delete_client(name):
    if not os.path.exists(os.path.join(app.config['CLIENTS_DIR'], '{}.ovpn').format(name)):
        return '<h2>Client not found</h2>', 404

    input_file = open(app.config['CLIENT_DELETE_INPUT_FILE'])
    client_del = Popen([app.config['CLIENT_DELETE'], name], stdin=input_file)
    client_del.wait()

    if 'error 23' not in ''.join(client_del.stdout.readlines()):
        flash('Something went wrong, probably the client has already been revoked')

    return redirect(url_for('new_client'))


@app.route('/clients/<str:name>', methods=['GET'])
@auth_required
def get_client(name):
    if not os.path.exists(os.path.join(app.config['CLIENTS_DIR'], '{}.ovpn').format(name)):
        return '<h2>Client not found</h2>', 404

    return render_template('client.html', name=name)


@app.route('/new_client', methods=['GET', 'POST'])
@auth_required
def new_client():
    if request.method == 'POST':
        name = request.form.to_dict()['client_name']

        input_file = open(app.config['CLIENT_SETUP_INPUT_FILE'])
        client_gen = Popen([app.config['CLIENT_SETUP'], name], stdin=input_file)
        client_gen.wait()

        if 'Data Base Updated' not in ''.join(client_gen.stdout.readlines()):
            flash('Something went wrong, please try another client name')

        else:
            return redirect(url_for('get_client', name=name))

    return render_template('new_client.html')
