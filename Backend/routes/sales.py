from flask import Blueprint, request, jsonify, session
from services.sale_service import SaleService
from routes.pages import login_required

sales_bp = Blueprint('sales', __name__)


@sales_bp.route('/api/sales', methods=['GET'])
@login_required
def get_sales():
    limit = int(request.args.get('limit', 50))
    sales = SaleService.get_all(limit)
    return jsonify([{
        'sale_id':        str(s.transactionID),
        'created_at':     s.date.isoformat(),
        'total':          s.total,
        'payment_method': s.payment_method,
        'profiles':       {'full_name': s.cashier.full_name} if s.cashier else None,
        'sale_items':     [{'quantity': si.quantity} for si in s.saleItems]
    } for s in sales])


@sales_bp.route('/api/sales', methods=['POST'])
@login_required
def record_sale():
    data       = request.get_json()
    items_data = data.get('items', [])
    payment    = data.get('payment_method', 'cash')

    if not items_data:
        return jsonify({'success': False, 'error': 'At least one item is required'}), 400

    sale, error = SaleService.record(items_data, payment, session.get('user_id'))
    if error:
        return jsonify({'success': False, 'error': error}), 400

    return jsonify({'success': True, 'sale_id': str(sale.transactionID), 'total': sale.total}), 201
