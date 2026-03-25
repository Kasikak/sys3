@items_bp.route('/get-items', methods=['GET'])
def get_items():
    items = Item.query.all()
    return jsonify([{
        'ItemName': item.ItemName,
        'Quantity': item.Quantity,
        'Price':    item.Price,
        'Stock':    item.Stock
    } for item in items]), 200