from flask import Flask
from flask_cors import CORS
from models import db
import os

app = Flask(__name__, template_folder='frontend', static_folder='frontend', static_url_path='/static')
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'carols-ims-secret-key-2024')

app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+pymysql://u207617_SGAHLQ1zsV:xYOGfUGgTD.Y%40X84lZZNGZzR"
    "@db-ash-03.apollopanel.com:3306/s207617_Management"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Register blueprints (Boundary layer)
from routes.auth       import auth_bp
from routes.pages      import pages_bp
from routes.items      import items_bp
from routes.sales      import sales_bp
from routes.alerts     import alerts_bp
from routes.reports    import reports_bp
from routes.users      import users_bp
from routes.promotions import promotions_bp

app.register_blueprint(auth_bp)
app.register_blueprint(pages_bp)
app.register_blueprint(items_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(users_bp)
app.register_blueprint(promotions_bp)

if __name__ == '__main__':
    app.run(debug=True)
