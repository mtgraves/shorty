import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    # -------------------------------------------------------------------------
    # configs to change
    # -------------------------------------------------------------------------
    APPLICATION_NAME = 'Shorty'
    EMAIL_HANDLE = ''
    ACCOUNTS_NEED_APPROVAL = False

    # -------------------------------------------------------------------------
    # configs that usually will not change
    # -------------------------------------------------------------------------
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'not-gonna-guess-my-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # LDAP/AD stuff
    LDAP_DN_END = ''
    LDAP_SERVER_URL = ''
    LDAP_PORT = 389
    LDAP_BASE = ''

    # email stuff
    MAIL_SERVER = ''
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = []

    # elasticsearch - for full text search stuff
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL') or 'http://localhost:9200'

