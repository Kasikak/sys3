from flask import Blueprint, render_template, redirect, session
from models import Item, Sale, User
from datetime import datetime, timezone

pages_bp = Blueprint('pages', __name__)


def get_ctx():
    return {
        'full_name': session.get('full_name', ''),
        'role':      session.get('role', '')
    }


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated


@pages_bp.route('/')
def index():
    return redirect('/home' if 'user_id' in session else '/login')


@pages_bp.route('/home')
@login_required
def home():
    return render_template('home.html', **get_ctx())


@pages_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', **get_ctx())


@pages_bp.route('/inventory')
@login_required
def inventory():
    return render_template('inventory.html', **get_ctx())


@pages_bp.route('/sales')
@login_required
def sales():
    return render_template('sales.html', **get_ctx())


@pages_bp.route('/reports')
@login_required
def reports():
    if session.get('role') not in ['owner', 'manager']:
        return redirect('/home')
    return render_template('reports.html', **get_ctx())


@pages_bp.route('/alerts')
@login_required
def alerts():
    if session.get('role') not in ['owner', 'manager']:
        return redirect('/home')
    return render_template('alerts.html', **get_ctx())


@pages_bp.route('/users')
@login_required
def users():
    if session.get('role') not in ['owner', 'manager']:
        return redirect('/dashboard')
    return render_template('users.html', **get_ctx())


@pages_bp.route('/promotions')
@login_required
def promotions():
    if session.get('role') not in ['owner', 'manager']:
        return redirect('/home')
    return render_template('promotions.html', **get_ctx())


@pages_bp.route('/api/dashboard')
@login_required
def api_dashboard():
    from flask import jsonify
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_sales = Sale.query.filter(Sale.date >= today_start).all()
    items       = Item.query.all()
    low_stock   = [i for i in items if 0 < i.Stock <= i.reorderThreshold]
    out_stock   = [i for i in items if i.Stock == 0]

    alert_items = out_stock + low_stock
    recent_alerts = []
    for i in alert_items[:5]:
        if i.Stock == 0:
            recent_alerts.append({'message': f'"{i.ItemName}" is out of stock', 'alert_type': 'out_of_stock'})
        else:
            recent_alerts.append({'message': f'"{i.ItemName}" is low on stock ({i.Stock} remaining)', 'alert_type': 'low_stock'})

    recent_logins = User.query.filter(User.last_login != None).order_by(User.last_login.desc()).limit(8).all()

    return jsonify({
        'total_products':     len(items),
        'revenue_today':      round(sum(s.total for s in today_sales), 2),
        'sales_count_today':  len(today_sales),
        'low_stock_count':    len(low_stock),
        'out_of_stock_count': len(out_stock),
        'low_stock_items':    [{'name': i.ItemName, 'stock': i.Stock} for i in (out_stock + low_stock)[:8]],
        'recent_alerts':      recent_alerts,
        'recent_logins':      [{'full_name': u.full_name, 'role': u.role.roleName.lower(), 'last_login': u.last_login.isoformat()} for u in recent_logins]
    })
