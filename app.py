from flask import Flask, jsonify

from routes.single import single_bp
from routes.batch import batch_bp


def create_app():
    """Application factory to create and configure the Flask app.

    Why an app factory? It keeps construction explicit and testable; here we
    keep things simple but still encapsulate creation.
    """
    app = Flask(__name__)

    # Register API blueprints under `/api` prefix to group endpoints.
    app.register_blueprint(single_bp, url_prefix="/api")
    app.register_blueprint(batch_bp, url_prefix="/api")

    @app.route("/", methods=["GET"])
    def health():
        # A lightweight health check for deployment or orchestration systems.
        return jsonify({"status": "ok", "message": "Flask AI API running"})

    return app


if __name__ == "__main__":
    # For local development only: run the server in debug mode.
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
