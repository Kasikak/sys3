from flask import Blueprint, request, jsonify, session, redirect, render_template
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET'])
def login_page():
    if 'user_id' in session:
        return redirect('/home')
    return render_template('login.html')


@auth_bp.route('/login', methods=['POST'])
def login():
    data     = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    user, error = AuthService.login(username, password)
    if error:
        return jsonify({'success': False, 'error': error}), 401

    from models import db
    from datetime import datetime, timezone
    user.last_login = datetime.now(timezone.utc)
    db.session.commit()

    session['user_id']   = user.userID
    session['full_name'] = user.full_name
    session['role']      = user.role.roleName.lower()
    return jsonify({'success': True})


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
