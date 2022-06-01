from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_mail import Mail
from flask_principal import Principal, Permission, RoleNeed
from flask_principal import identity_changed, Identity, AnonymousIdentity,\
        identity_loaded, UserNeed, RoleNeed


import logging, os
from logging.handlers import SMTPHandler, RotatingFileHandler
from elasticsearch import Elasticsearch

# create flask extension instances, not attached to any application
db = SQLAlchemy()
login=LoginManager()
login.login_view = 'auth.login'
bootstrap = Bootstrap()
moment = Moment()
mail = Mail()
principals = Principal()
admin_permission = Permission(RoleNeed('Admin'))


def initialize_extensions(app):
    '''
    bind the flask extensions to the current application
    '''
    db.init_app(app)
    login.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    principals.init_app(app)


def register_blueprints(app):
    '''
    register the flask blueprints
    '''
    # errors
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    # authentication
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    # main
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)


def user_info_provider_setup(app):
    '''
    set up magical user information provider to handle permissions
    '''
    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        # Set the identity user object
        identity.user = current_user

        # Add the UserNeed to the identity
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        # Assuming the User model has a list of roles, update the
        # identity with the roles that the user provides
        if hasattr(current_user, 'roles'):
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.role_name))


def create_app(config_class=Config):
    '''
    APPLICATION FACTORY FUNCTION
    '''

    app = Flask(__name__)
    app.config.from_object(config_class)
    initialize_extensions(app)
    register_blueprints(app)
    user_info_provider_setup(app)

    # add elasticsearch attribute to app instance
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
            if app.config['ELASTICSEARCH_URL'] else None

    if not app.debug:
        
        # set up email notifications for errors
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=app.config['EMAIL_HANDLE'],
                toaddrs=app.config['ADMINS'], subject=str(app.config['APPLICATION_NAME']+' error'),
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # set up logging to disk
        if not os.path.exists('logs'):
            os.mkdir('logs')
            file_handler = RotatingFileHandler(str('logs/'+app.config['APPLICATION_NAME']+'.log'), 
                    maxBytes=10240,
                    backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

            app.logger.setLevel(logging.INFO)
            app.logger.info(str(app.config['APPLICATION_NAME']+' startup'))

    return app

from app import models
