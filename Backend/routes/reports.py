from flask import Blueprint, request, jsonify, session
from services.report_service import ReportService
from routes.pages import login_required

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/api/reports')
@login_required
def get_report():
    if session.get('role') not in ['owner', 'manager']:
        return jsonify({'error': 'Forbidden'}), 403
    start = request.args.get('start_date')
    end   = request.args.get('end_date')

    if not start or not end:
        return jsonify({'error': 'start_date and end_date are required'}), 400

    data, error = ReportService.generate(start, end, session.get('user_id'))
    if error:
        return jsonify({'error': error}), 400

    return jsonify(data)
