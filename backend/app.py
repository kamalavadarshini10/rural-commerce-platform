from flask import Flask, jsonify
from flask_cors import CORS
from database.db import close_db
from routes.auth import auth_bp
from routes.deliveries import deliveries_bp
from routes.instructions import instructions_bp
from routes.admin import admin_bp
from routes.sync import sync_bp
from routes.locations import locations_bp
from routes.confirmations import confirmations_bp
import os

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    app.teardown_appcontext(close_db)
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(deliveries_bp, url_prefix='/api/deliveries')
    app.register_blueprint(instructions_bp, url_prefix='/api/instructions')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(sync_bp, url_prefix='/api/sync')
    app.register_blueprint(locations_bp, url_prefix='/api/locations')
    app.register_blueprint(confirmations_bp, url_prefix='/api')
    
    @app.route('/api/health')
    def health():
        return jsonify({"status": "ok"})
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
