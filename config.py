from os import path

base_dir = path.abspath(path.dirname(__file__))

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'super-secret-key'
    JWT_ERROR_MESSAGE_KEY = 'message'



class DevelopmentConfig(Config):
    DEBUG = True
    #SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://maxim:canada@localhost:5434/smilecook'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(base_dir, 'data_dev.sqlite')


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
