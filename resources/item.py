from typing import Tuple

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, fresh_jwt_required

from libs.strings import gettext
from models.item import ItemModel
from schemas.item import ItemSchema

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


class Item(Resource):
    @classmethod
    def get(cls, name: str) -> Tuple:
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.schema_dump(item), 200
        return {"message": gettext("item_not_found")}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name: str) -> Tuple:
        if ItemModel.find_by_name(name):
            return (
                {"message": gettext("item_name_exists").format(name)},
                400,
            )
        item_json = request.get_json()  # price id, store id
        item_json["name"] = name
        item = item_schema.load(item_json)
        try:
            item.save_to_db()
        except:
            return {"message": gettext("item_error_inserting")}, 500

        return item.json(), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str) -> Tuple:
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": gettext("item_deleted")}, 200
        return {"message": gettext("item_not_found")}, 404

    @classmethod
    def put(cls, name: str) -> Tuple:
        item_json = request.get_json()
        item = ItemModel.find_by_name(name)

        if item:
            item.price = item_json["price"]
        else:
            item_json["name"] = name
            item = item_schema.load(item_json)

        item.save_to_db()
        return item_schema.dump(item), 200


class ItemList(Resource):
    @classmethod
    def get(cls) -> Tuple:
        """
        Here we get the JWT identity, and then if the user is logged in (we were able to get an identity)
        we return the entire item list.
        Otherwise we just return the item names.
        This could be done with e.g. see orders that have been placed, but not see details about the orders
        unless the user has logged in.
        """
        return {"items": item_list_schema.dump(ItemModel.find_all())}, 200
