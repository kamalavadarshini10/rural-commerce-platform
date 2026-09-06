from flask import Blueprint, request, jsonify
from routes.instructions import confirm_instruction_logic

confirmations_bp = Blueprint('confirmations', __name__)


@confirmations_bp.route('/customer-confirmations', methods=['POST'])
def customer_confirmation():
    """
    POST /api/customer-confirmations
    Body: { "instruction_id": <id>, "is_correct": true|false, "updated_content": "..." }
    """
    data = request.json or {}
    instruction_id = data.get('instruction_id')
    if not instruction_id:
        return jsonify({"error": "instruction_id is required"}), 400
    result = confirm_instruction_logic(instruction_id, data)
    return jsonify(result), 200
