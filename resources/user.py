import os
from http import HTTPStatus
from os import environ

from flask import request, url_for, render_template
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError
from webargs import fields
from webargs.flaskparser import use_kwargs

from models.user import User
from schemas.user import UserSchema
from schemas.recipe import RecipeSchema

from models.recipe import Recipe

from utils import generate_token, verify_token, save_image
from mailgun import MailGunApi

from extensions import image_set


user_schema = UserSchema()
user_public_schema = UserSchema(exclude=('email',))
user_avatar_schema = UserSchema(only=('avatar_url', ))

recipe_list_schema = RecipeSchema(many=True)

mailgun = MailGunApi(domain=environ.get('MAILGUN_DOMAIN'),
                     api_key=environ.get('MAILGUN_API_KEY'))


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

        self._send_link_by_email(user=user)
        return user_schema.dump(user), HTTPStatus.CREATED

    @staticmethod
    def _send_link_by_email(user):
        token = generate_token(user.email, salt='activate')
        subject = 'Please confirm your registration.'
        link = url_for('useractivateresource', token=token, _external=True)
        html=render_template('mail/confirm' + '.html', link=link, username=user.username)
        text = render_template('mail/confirm' + '.txt', link=link, username=user.username)
        mailgun.send_email(to=user.email,
                           subject=subject,
                           text=text,
                           html=html
                           )




class UserResource(Resource):
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


class UserActivateResource(Resource):
    def get(self, token):
        email = verify_token(token, salt='activate')
        if not email:
            return {'message': 'Invalid token or token expired'}, HTTPStatus.BAD_REQUEST
        user = User.get_by_email(email=email)
        if not user:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND
        if user.is_active:
            return {'message': 'The user account is already activated'}, HTTPStatus.BAD_REQUEST
        user.is_active = True
        user.save()
        return {}, HTTPStatus.NO_CONTENT


class UserAvatarUploadResource(Resource):
    @jwt_required()
    def put(self):
        file = request.files.get("avatar")
        if not file:
            return {'message': 'Not a valid image'}, HTTPStatus.BAD_REQUEST
        if not image_set.file_allowed(file, file.filename):
            return {'message': 'File type not allowed'}, HTTPStatus.BAD_REQUEST
        user = User.get_by_id(id=get_jwt_identity())
        if user.avatar_image:
            avatar_path = image_set.path(folder='avatars', filename=user.avatar_image)
            if os.path.exists(avatar_path):
                os.remove(avatar_path)
        filename = save_image(image=file, folder='avatars')
        user.avatar_image = filename
        user.save()
        return user_avatar_schema.dump(user), HTTPStatus.OK

