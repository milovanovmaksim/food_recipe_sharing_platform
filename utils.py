import uuid
from itsdangerous import URLSafeTimedSerializer

from flask import current_app
from flask_uploads import extension

from extensions import image_set


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
    return filename

