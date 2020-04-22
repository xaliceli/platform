"""
init_app.py
Defines the db and Flask app
"""
import os
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import config

local_db_uri = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=config['dbuser'],
    dbpass=config['dbpass'],
    dbhost=config['local_dbhost'],
    dbname=config['dbname']
)

live_db_uri = (
    'postgres+pg8000://{user}:{password}@/{database}'
    '?unix_sock=/cloudsql/{connection_name}/.s.PGSQL.5432').format(
    user=config['dbuser'],
    password=config['dbpass'],
    database=config['dbname'],
    host=config['dbhost'],
    connection_name=config['dbconnection'])

if os.environ.get('GAE_INSTANCE'):
    SQLALCHEMY_DATABASE_URI = live_db_uri
else:
    SQLALCHEMY_DATABASE_URI = local_db_uri

app = Flask(__name__)

app.config.update(
    SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY=config['secret_key'],
    GOOGLE_OAUTH_CLIENT_ID=config['google_oauth_client_id'],
    GOOGLE_OAUTH_CLIENT_SECRET=config['google_oauth_client_secret'],
    GITHUB_OAUTH_CLIENT_ID=config['github_oauth_client_id'],
    GITHUB_OAUTH_CLIENT_SECRET=config['github_oauth_client_secret'],
    GOOGLE_APPLICATION_CREDENTIALS='nlp-key.json'
)

db = SQLAlchemy(app)
migrate = Migrate(app, db)