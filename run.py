'''
Run WSGI application
'''

from app import app as application
import config

if __name__ == '__main__':
    application.run(host=config.host, port=config.port, debug=config.debug)
