from http import HTTPStatus
from os import path, remove

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from webargs import fields
from webargs.flaskparser import use_kwargs

from models.recipe import Recipe
from schemas.recipe import RecipeSchema, RecipePaginationSchema
from extensions import image_set, cache
from utils import save_image, clear_cache

recipe_schema = RecipeSchema()
recipe_cover_schema = RecipeSchema(only=('cover_url',))
recipe_pagination_schema = RecipePaginationSchema()


class RecipeListResource(Resource):

    @use_kwargs({'q': fields.Str(missing=''),
                 'page': fields.Int(missing=1),
                 'per_page': fields.Int(missing=20),
                 'sort': fields.Str(missing='created_at'),
                 'order': fields.Str(missing='desc')}, location="query")
    @cache.cached(timeout=60, query_string=True)
    def get(self, q, page, per_page, sort, order):
        print('Querying database....')
        if sort not in ['created_at', 'cook_time', 'num_of_servings']:
            sort = 'created_at'
        if order not in ['asc', 'desc']:
            order = 'desc'
        paginated_recipes = Recipe.get_all_published(q, page, per_page, sort, order)
        return recipe_pagination_schema.dump(paginated_recipes), HTTPStatus.OK

    @jwt_required()
    def post(self):
        json_data = request.get_json()
        current_user = get_jwt_identity()
        try:
            data = recipe_schema.load(data=json_data)
        except ValidationError as errors:
            return {'message': 'Validation errors', 'errors': errors.messages}, HTTPStatus.BAD_REQUEST
        recipe = Recipe(**data)
        recipe.user_id = current_user
        recipe.save()
        return recipe_schema.dump(recipe), HTTPStatus.CREATED


class RecipeResource(Resource):

    @jwt_required(optional=True)
    def get(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if not recipe:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if not recipe.is_publish and recipe.user_id != current_user:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        return recipe_schema.dump(recipe), HTTPStatus.OK

    @jwt_required()
    def delete(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if not recipe:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        recipe.delete()

        clear_cache('/recipes')
        return {}, HTTPStatus.NO_CONTENT

    @jwt_required()
    def patch(self, recipe_id):
        json_data = request.get_json()
        try:
            data = recipe_schema.load(data=json_data, partial=('name',))
        except ValidationError as errors:
            return {'message': 'Validation errors', 'errors': errors.messages}, HTTPStatus.BAD_REQUEST
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if not recipe:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.name = data.get('name') or recipe.name
        recipe.description = data.get('description') or recipe.description
        recipe.num_of_servings = data.get('num_of_servings') or recipe.num_of_servings
        recipe.cook_time = data.get('cook_time') or recipe.cook_time
        recipe.directions = data.get('directions') or recipe.directions
        recipe.ingredients = data.get('ingredients') or recipe.ingredients
        recipe.save()
        clear_cache('/recipes')
        return recipe_schema.dump(recipe), HTTPStatus.OK


class RecipePublishResource(Resource):

    @jwt_required()
    def put(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if not recipe:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        recipe.is_publish = True
        recipe.save()
        clear_cache('/recipes')
        return {}, HTTPStatus.NO_CONTENT

    @jwt_required()
    def delete(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if not recipe:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        recipe.is_publish = False
        recipe.save()
        clear_cache('/recipes')
        return {}, HTTPStatus.NO_CONTENT


class RecipeCoverUploadResource(Resource):
    @jwt_required()
    def put(self, recipe_id):
        file = request.files.get('cover')
        if not file:
            return {"message": 'Not a valid image'}, HTTPStatus.BAD_REQUEST
        if not image_set.file_allowed(file, file.filename):
            return {'message': 'File type not allowed'}, HTTPStatus.BAD_REQUEST
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if not recipe:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        if recipe.cover_image:
            cover_path = image_set.path(folder='recipes', filename=recipe.cover_image)
            if path.exists(cover_path):
                remove(cover_path)
        file_name = save_image(file, 'recipes')
        recipe.cover_image = file_name
        recipe.save()
        clear_cache('/recipes')
        return recipe_cover_schema.dump(recipe), HTTPStatus.OK
