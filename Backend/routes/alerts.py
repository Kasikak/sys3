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

    # Sync: create missing alerts for any items that are currently low/out
    for item in Item.query.all():
        AlertService.create_if_needed(item)

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
    success, error = AlertService.resolve(alert_id)
    if not success:
        status = 404 if error == 'Alert not found' else 400
        return jsonify({'success': False, 'error': error}), status
    return jsonify({'success': True})
