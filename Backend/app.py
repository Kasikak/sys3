from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import db
import os

app = Flask(
    __name__,
    static_folder="frontend",
    static_url_path=""
)

CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+pymysql://u207617_SGAHLQ1zsV:xYOGfUGgTD.Y%40X84lZZNGZzR"
    "@db-ash-03.apollopanel.com:3306/s207617_Management"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from routes.items import items_bp
app.register_blueprint(items_bp)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")

@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)

if __name__ == "__main__":
    app.run(debug=True)
