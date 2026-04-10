from flask import Blueprint, request, jsonify, session
from routes.pages import login_required
from services.promotion_service import PromotionService

promotions_bp = Blueprint('promotions', __name__)


def manager_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') not in ['owner', 'manager']:
            return jsonify({'error': 'Unauthorized'}), 403
        return f(*args, **kwargs)
    return decorated


@promotions_bp.route('/api/promotions', methods=['GET'])
@login_required
@manager_required
def get_promotions():
    items, error = PromotionService.get_all()
    if error:
        return jsonify({'error': error}), 500
    return jsonify(items)


@promotions_bp.route('/api/promotions/<path:item_name>', methods=['POST'])
@login_required
@manager_required
def set_promotion(item_name):
    data = request.get_json() or {}

    promotion_name   = data.get('promotion_name', '').strip()
    reason           = data.get('reason', '').strip()
    threshold_qty    = data.get('threshold_qty')
    discount_percent = data.get('discount_percent')

    try:
        threshold_qty    = int(threshold_qty)
        discount_percent = float(discount_percent)
    except (TypeError, ValueError):
        return jsonify({'error': 'threshold_qty must be an integer and discount_percent a number'}), 400

    result, error = PromotionService.set_promotion(
        item_name, promotion_name, reason, threshold_qty, discount_percent
    )
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'success': True, 'promotion': result})


@promotions_bp.route('/api/promotions/<path:item_name>', methods=['DELETE'])
@login_required
@manager_required
def remove_promotion(item_name):
    success, error = PromotionService.remove_promotion(item_name)
    if not success:
        return jsonify({'error': error}), 404
    return jsonify({'success': True})
