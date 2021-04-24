from marshmallow import Schema, fields
from werkzeug.security import generate_password_hash


class UserSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Int(dump_only=True)  # Fields to skip during deserialization (read-only fields)
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.Method(required=True, deserialize='load_password')
    created_at = fields.DateTime(dump_only=True)
    update_at = fields.DateTime(dump_only=True)

    def load_password(self, value):
        return generate_password_hash(value)
