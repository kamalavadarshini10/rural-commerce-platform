from flask import Blueprint, request, jsonify
from database.db import query_db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Simple demo authentication (plaintext password comparison).
    NOT secure - this is a college prototype, not a production system.
    See README.md for demo credentials.
    """
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    user = query_db("SELECT * FROM Users WHERE username = ?", (username,), one=True)

    if user:
        if user['password_hash'] != password:
            return jsonify({"error": "Invalid credentials"}), 401

        customer_id = None
        if user['role'] == 'customer':
            customer = query_db("SELECT id FROM Customers WHERE user_id = ?", (user['id'],), one=True)
            if customer:
                customer_id = customer['id']

        return jsonify({
            "id": user['id'],
            "username": user['username'],
            "role": user['role'],
            "customer_id": customer_id
        }), 200

    # Fallback for demo convenience: allow logging in as a seeded customer by name
    # (no password required in this legacy path, kept for backward compatibility).
    customer = query_db("SELECT * FROM Customers WHERE name = ?", (username,), one=True)
    if customer:
        return jsonify({
            "id": 999,
            "username": username,
            "role": "customer",
            "customer_id": customer['id']
        }), 200

    return jsonify({"error": "Invalid credentials"}), 401
