from ma import ma
from models.user import UserModel


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_only = ("password",)
        dump_only = ("id", "is_active")
        load_instance = True
