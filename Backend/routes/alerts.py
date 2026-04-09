from flask import Blueprint, request, jsonify, session
from services.alert_service import AlertService
from models import Item
from routes.pages import login_required

alerts_bp = Blueprint('alerts', __name__)


@alerts_bp.route('/api/alerts')
@login_required
def get_alerts():
    if session.get('role') not in ['owner', 'manager']:
        return jsonify({'error': 'Forbidden'}), 403
    resolved = request.args.get('resolved', 'false').lower() == 'true'
    alerts   = AlertService.get_all(resolved)
    result   = []
    for a in alerts:
        item = Item.query.filter_by(ItemName=a.ItemName).first()
        result.append({
            'id':         a.alertID,
            'alert_type': a.alertType,
            'message':    a.message,
            'created_at': a.createdAt.isoformat(),
            'products':   {'name': a.ItemName, 'stock': item.Stock} if item else {'name': a.ItemName, 'stock': 0}
        })
    return jsonify(result)


@alerts_bp.route('/api/alerts/<int:alert_id>/resolve', methods=['PUT'])
@login_required
def resolve_alert(alert_id):
    _, error = AlertService.resolve(alert_id)
    if error:
        return jsonify({'success': False, 'error': error}), 404
    return jsonify({'success': True})
