class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://maxim:canada@localhost:5434/smilecook'


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
