from flask import Flask, send_from_directory
from flask_cors import CORS
from models import db
import os

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+pymysql://u207617_SGAHLQ1zsV:xYOGfUGgTD.Y%40X84lZZNGZzR"
    "@db-ash-03.apollopanel.com:3306/s207617_Management"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

from routes.items import items_bp
app.register_blueprint(items_bp)

@app.route("/")
def home():
    return send_from_directory("frontend", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("frontend", path)

if __name__ == "__main__":
    app.run(debug=True)