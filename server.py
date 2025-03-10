from waitress import serve
from api.wsgi import application
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

if __name__ == '__main__':
    print('Starting Waitress server on http://127.0.0.1:8088...')
    serve(application, host='127.0.0.1', port=8088) 