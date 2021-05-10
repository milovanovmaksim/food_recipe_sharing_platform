from marshmallow import Schema, fields
from werkzeug.security import generate_password_hash
from flask import url_for


class UserSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Int(dump_only=True)  # Fields to skip during deserialization (read-only fields)
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.Method(required=True, deserialize='load_password')
    created_at = fields.DateTime(dump_only=True)
    update_at = fields.DateTime(dump_only=True)
    avatar_url = fields.Method(serialize='dump_avatar_url')

    @staticmethod
    def load_password(value):
        return generate_password_hash(value)

    @staticmethod
    def dump_avatar_url(user):
        if user.avatar_image:
            return url_for('static', filename=f"images/avatars/{user.avatar_image}", _external=True)
        else:
            return url_for('static', filename='images/assets/default-avatar.jpeg', _external=True)

