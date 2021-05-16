from os import path

base_dir = path.abspath(path.dirname(__file__))


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'super-secret-key'
    JWT_ERROR_MESSAGE_KEY = 'message'
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    UPLOADED_IMAGES_DEST = 'static/images'
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 10 * 60


class DevelopmentConfig(Config):
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://maxim:canada@localhost:5434/smilecook'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(base_dir, 'data_dev.sqlite')


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
