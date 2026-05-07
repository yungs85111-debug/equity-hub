"""EQUITY HUB Flask backend."""
from flask import Flask, jsonify
from flask_cors import CORS

from backend.config import FRONTEND_ORIGIN
from backend.routes.health    import health_bp
from backend.routes.sectors   import sectors_bp
from backend.routes.sector    import sector_bp
from backend.routes.company   import company_bp
from backend.routes.indicator import indicator_bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, origins=[FRONTEND_ORIGIN, "http://localhost:5173", "http://127.0.0.1:5173"])

    app.register_blueprint(health_bp)
    app.register_blueprint(sectors_bp)
    app.register_blueprint(sector_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(indicator_bp)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
