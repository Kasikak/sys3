from flask import Blueprint, request, jsonify, session
from services.user_service import UserService
from routes.pages import login_required

users_bp = Blueprint('users', __name__)


@users_bp.route('/api/users/public')
def get_users_public():
    """Returns just name + username — no auth needed, used for login dropdown."""
    users = UserService.get_all()
    return jsonify([{'username': u.username, 'full_name': u.full_name} for u in users])


@users_bp.route('/api/users', methods=['POST'])
@login_required
def create_user():
    if session.get('role') != 'owner':
        return jsonify({'success': False, 'error': 'Only owners can add users'}), 403
    data = request.get_json() or {}
    _, error = UserService.create(
        full_name=data.get('full_name', '').strip(),
        username=data.get('username', '').strip(),
        pin=data.get('pin', ''),
        role_name=data.get('role', 'cashier')
    )
    if error:
        return jsonify({'success': False, 'error': error}), 400
    return jsonify({'success': True}), 201


@users_bp.route('/api/users')
@login_required
def get_users():
    if session.get('role') not in ['owner', 'manager']:
        return jsonify({'error': 'Forbidden'}), 403
    users = UserService.get_all()
    return jsonify([{
        'id':         str(u.userID),
        'full_name':  u.full_name,
        'username':   u.username,
        'role':       u.role.roleName.lower(),
        'created_at': u.created_at.isoformat() if u.created_at else ''
    } for u in users])


@users_bp.route('/api/users/<user_id>/role', methods=['PUT'])
@login_required
def update_role(user_id):
    if session.get('role') != 'owner':
        return jsonify({'success': False, 'error': 'Only owners can change roles'}), 403
    role_name = request.get_json().get('role', '')
    _, error  = UserService.update_role(user_id, role_name)
    if error:
        return jsonify({'success': False, 'error': error}), 400
    return jsonify({'success': True})
