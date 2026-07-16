from flask import Flask, jsonify
from flask_cors import CORS

from db import init_db
from routes import transactions_bp, ai_bp, upload_bp

app = Flask(__name__)
CORS(app)

# Initialize the database on startup
init_db()

# Register blueprints
app.register_blueprint(transactions_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(ai_bp)


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "MoneyMentor API is running"})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
