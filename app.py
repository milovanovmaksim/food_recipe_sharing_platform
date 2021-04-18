import os

from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

from models.user import User
from models.recipe import Recipe
from config import config
from extensions import db
from resources.recipe import RecipeListResource, RecipeResource, RecipePublishResource


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    register_extensions(app)
    register_resource(app)
    return app


def register_extensions(app):
    db.init_app(app)
    migrate = Migrate(app, db)


def register_resource(app):
    api = Api(app)
    api.add_resource(RecipeListResource, '/recipes')
    api.add_resource(RecipeResource, '/recipes/<int:recipe_id>')
    api.add_resource(RecipePublishResource, '/recipes/<int:recipe_id>/publish')


def make_shell_context():
    return dict(app=app, db=db, User=User, Recipe=Recipe)


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':

    manager.run()
