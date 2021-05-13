import os

from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from flask_uploads import configure_uploads, patch_request_class

from models.user import User
from models.recipe import Recipe

from config import config
from extensions import db, jwt, image_set

from resources.user import UserListResource, UserResource, MeResource,\
    UserRecipeListResource, UserActivateResource, UserAvatarUploadResource
from resources.recipe import RecipeListResource, RecipeResource, RecipePublishResource
from resources.token import TokenResource, RefreshResource, black_list, RevokeResource


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    register_extensions(app)
    register_resource(app)
    return app


def register_extensions(app):
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt.init_app(app)
    configure_uploads(app, image_set)
    patch_request_class(app, 10 * 1024 * 1024)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return jti in black_list


def register_resource(app):
    api = Api(app)
    api.add_resource(UserListResource, '/users')
    api.add_resource(UserResource, '/users/<string:username>')
    api.add_resource(UserRecipeListResource, '/users/<string:username>/recipes')
    api.add_resource(UserActivateResource, '/users/active/<string:token>')
    api.add_resource(UserAvatarUploadResource, '/users/avatar')

    api.add_resource(MeResource, '/me')

    api.add_resource(RecipeListResource, '/recipes')
    api.add_resource(RecipeResource, '/recipes/<int:recipe_id>')
    api.add_resource(RecipePublishResource, '/recipes/<int:recipe_id>/publish')

    api.add_resource(TokenResource, '/token')
    api.add_resource(RefreshResource, '/refresh')
    api.add_resource(RevokeResource, '/revoke')


def make_shell_context():
    return dict(app=app, db=db, User=User, Recipe=Recipe)


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
