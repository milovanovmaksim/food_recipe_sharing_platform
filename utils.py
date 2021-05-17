import uuid
from itsdangerous import URLSafeTimedSerializer
from os import stat, remove

from flask import current_app, request
from flask_uploads import extension

from PIL import Image

from extensions import image_set, cache


def generate_token(email, salt=None):
    serializer = URLSafeTimedSerializer(current_app.config.get('SECRET_KEY'))
    return serializer.dumps(email, salt=salt)


def verify_token(token, max_age=(30 * 60), salt=None):
    serializer = URLSafeTimedSerializer(current_app.config.get('SECRET_KEY'))
    try:
        email = serializer.loads(token, max_age=max_age, salt=salt)
        return email
    except:
        return False


def save_image(image, folder):
    filename = f"{uuid.uuid4()}.{extension(image.filename)}"
    image_set.save(image, folder=folder, name=filename)
    filename = compress_image(filename=filename, folder=folder)
    return filename


def compress_image(filename, folder):
    file_path = image_set.path(filename=filename, folder=folder)
    image = Image.open(file_path)
    if image.mode != "RGB":
        image = image.convert("RGB")
    if max(image.width, image.height) > 1600:
        maxsize = (1600, 1600)
        image.thumbnail(maxsize, Image.ANTIALIAS)
    compressed_filename = f'{uuid.uuid4()}.jpg'
    compressed_file_path = image_set.path(filename=compressed_filename, folder=folder)
    image.save(compressed_file_path, optimize=True, quality=75)
    original_size = stat(file_path).st_size
    compressed_size = stat(compressed_file_path).st_size
    percentage = round((original_size - compressed_size) / original_size * 100)
    print(f"The file size is reduced by {percentage} %, from {original_size} to {compressed_size}")
    remove(file_path)
    return compressed_filename


def clear_cache(key_prefix):
    keys = [key for key in cache.cache._cache.keys() if key.startswith(key_prefix)]
    cache.delete_many(*keys)
