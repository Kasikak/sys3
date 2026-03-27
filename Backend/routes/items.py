from flask import Blueprint, request, jsonify
from models import db, Item

items_bp = Blueprint('items', __name__)


@items_bp.route('/add-item', methods=['POST'])
def add_item():
    data = request.get_json()

    item_name = data.get('ItemName')
    quantity  = data.get('Quantity')
    price     = data.get('Price')
    stock     = data.get('Stock')
    category  = data.get('Category', 'Uncategorized')

    if not all([item_name, quantity is not None, price is not None, stock is not None]):
        return jsonify({'error': 'All fields are required'}), 400

    new_item = Item(ItemName=item_name, Quantity=quantity, Price=price, Stock=stock, Category=category)
    db.session.add(new_item)
    db.session.commit()

    return jsonify({'message': f'"{item_name}" added successfully'}), 201


@items_bp.route('/remove-item', methods=['DELETE'])
def remove_item():
    data = request.get_json()
    item_name = data.get('ItemName')

    item = Item.query.filter_by(ItemName=item_name).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({'message': f'"{item_name}" deleted successfully'}), 200


@items_bp.route('/update-item', methods=['PUT'])
def update_item():
    data = request.get_json()
    item_name = data.get('ItemName')

    item = Item.query.filter_by(ItemName=item_name).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    if data.get('Quantity') is not None:
        item.Quantity = data['Quantity']
    if data.get('Price') is not None:
        item.Price = data['Price']
    if data.get('Stock') is not None:
        item.Stock = data['Stock']
    if data.get('Category') is not None:
        item.Category = data['Category']

    db.session.commit()

    return jsonify({'message': f'"{item_name}" updated successfully'}), 200

@items_bp.route('/get-items', methods=['GET'])
def get_items():
    items = Item.query.all()
    return jsonify([{
        'ItemName': item.ItemName,
        'Quantity': item.Quantity,
        'Price':    item.Price,
        'Stock':    item.Stock,
        'Category': item.Category
    } for item in items]), 200