from http import HTTPStatus

from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError
from webargs import fields
from webargs.flaskparser import use_kwargs


from models.user import User
from schemas.user import UserSchema
from schemas.recipe import RecipeSchema

from models.recipe import Recipe

user_schema = UserSchema()
user_public_schema = UserSchema(exclude=('email',))

recipe_list_schema = RecipeSchema(many=True)


class UserListResource(Resource):
    def post(self):
        json_data = request.get_json()
        try:
            data = user_schema.load(data=json_data)
        except ValidationError as errors:
            return {'message': 'Validation errors', 'errors': errors.messages}, HTTPStatus.BAD_REQUEST

        if User.get_by_username(data.get('username')):
            return {'message': 'username already used'}, HTTPStatus.BAD_REQUEST
        if User.get_by_email(data.get('email')):
            return {'message': 'email already used'}, HTTPStatus.BAD_REQUEST
        user = User(**data)
        user.save()
        return user_schema.dump(user), HTTPStatus.CREATED


class UserResource(Resource):
    """
    Могут быть случаи, когда вы хотите использовать один и тот же маршрут
    независимо от того, присутствует ли JWT в запросе или нет.
     В этих ситуациях вы можете использовать jwt_required () с необязательным аргументом = True.
    """

    @jwt_required(optional=True)
    def get(self, username):
        user = User.get_by_username(username=username)
        if not user:
            return {'message': 'user not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()
        if current_user == user.id:
            data = user_schema.dump(user)
        else:
            data = user_public_schema.dump(user)
        return data, HTTPStatus.OK


class MeResource(Resource):

    @jwt_required()
    def get(self):
        user = User.get_by_id(id=get_jwt_identity())
        return user_schema.dump(user), HTTPStatus.OK


class UserRecipeListResource(Resource):
    @jwt_required(optional=True)
    @use_kwargs({'visibility': fields.Str(missing='public')}, location="query")
    def get(self, username, visibility):
        user = User.get_by_username(username=username)
        if not user:
            return {'message', 'User not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()

        if current_user != user.id:
            visibility = 'public'
        recipes = Recipe.get_all_by_user(user_id=user.id, visibility=visibility)
        return recipe_list_schema.dump(recipes), HTTPStatus.OK

