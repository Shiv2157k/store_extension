from typing import Tuple

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, fresh_jwt_required

from models.item import ItemModel

BLANK_ERROR = "{} cannot be blank."
NAME_ALREADY_EXISTS = "An item with name {} already exists."
ERROR_INSERTING = "An error occurred while inserting the item."
ITEM_DELETED = "Item deleted."
ITEM_NOT_FOUND = "Item not found."


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price", type=float, required=True, help=BLANK_ERROR.format("price")
    )
    parser.add_argument(
        "store_id", type=int, required=True, help=BLANK_ERROR.format("store_id")
    )

    @classmethod
    def get(cls, name: str) -> Tuple:
        item = ItemModel.find_by_name(name)
        if item:
            return item.json(), 200
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name: str) -> Tuple:
        if ItemModel.find_by_name(name):
            return (
                {"message": NAME_ALREADY_EXISTS.format(name)},
                400,
            )
        data = Item.parser.parse_args()
        item = ItemModel(name, **data)
        try:
            item.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 500

        return item.json(), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str) -> Tuple:
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": ITEM_DELETED}, 200
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    def put(cls, name: str) -> Tuple:
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item:
            item.price = data["price"]
        else:
            item = ItemModel(name, **data)

        item.save_to_db()

        return item.json(), 200


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
        return {"items": [item.json() for item in ItemList.find_all()]}, 200
