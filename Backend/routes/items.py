from flask import Blueprint, request, jsonify, session
from services.item_service import ItemService
from routes.pages import login_required

items_bp = Blueprint('items', __name__)


@items_bp.route('/api/get-items')
@login_required
def get_items():
    search   = request.args.get('search', '')
    category = request.args.get('category', '')
    items    = ItemService.get_all(search, category)
    return jsonify([{
        'id':                i.ItemName,
        'name':              i.ItemName,
        'price':             i.Price,
        'stock':             i.Stock,
        'reorder_threshold': i.reorderThreshold,
        'categories':        {'name': i.Category} if i.Category else None
    } for i in items])


@items_bp.route('/api/add-item', methods=['POST'])
@login_required
def add_item():
    if session.get('role') not in ['owner', 'manager']:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'success': False, 'error': 'Item name is required'}), 400
    try:
        price             = float(data.get('price', 0))
        stock             = int(data.get('stock', 0))
        reorder_threshold = int(data.get('reorder_threshold', 10))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid price, stock, or threshold'}), 400
    if price < 0 or stock < 0 or reorder_threshold < 0:
        return jsonify({'success': False, 'error': 'Values cannot be negative'}), 400
    _, error = ItemService.add(name, price, stock, data.get('category', 'Uncategorized'), reorder_threshold)
    if error:
        return jsonify({'success': False, 'error': error}), 400
    return jsonify({'success': True}), 201


@items_bp.route('/api/update-item/<item_id>', methods=['PUT'])
@login_required
def update_item(item_id):
    if session.get('role') not in ['owner', 'manager']:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    data = request.get_json() or {}
    try:
        price             = float(data.get('price', 0))
        stock             = int(data.get('stock', 0))
        reorder_threshold = int(data.get('reorder_threshold', 10))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid price, stock, or threshold'}), 400
    if price < 0 or stock < 0 or reorder_threshold < 0:
        return jsonify({'success': False, 'error': 'Values cannot be negative'}), 400
    _, error = ItemService.update(item_id, price, stock, data.get('category', ''), reorder_threshold)
    if error:
        return jsonify({'success': False, 'error': error}), 404
    return jsonify({'success': True})


@items_bp.route('/api/remove-item/<item_id>', methods=['DELETE'])
@login_required
def remove_item(item_id):
    if session.get('role') not in ['owner', 'manager']:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    _, error = ItemService.delete(item_id)
    if error:
        return jsonify({'success': False, 'error': error}), 404
    return jsonify({'success': True})
