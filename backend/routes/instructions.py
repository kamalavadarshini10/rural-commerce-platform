from flask import Blueprint, request, jsonify
from database.db import query_db, insert_db, update_db
from datetime import datetime

instructions_bp = Blueprint('instructions', __name__)


@instructions_bp.route('', methods=['POST'])
def capture_instruction():
    """
    POST /api/instructions
    Lets an agent (or admin) capture a brand-new access instruction for a
    location directly, outside of the outcome-recording flow. Creates a new
    AccessInstructions row (deactivating any previous one) plus its first
    InstructionVersion.
    """
    data = request.json or {}
    location_id = data.get('location_id')
    content = data.get('content')
    source = data.get('source', 'agent')

    if not location_id or not content:
        return jsonify({"error": "location_id and content are required"}), 400

    timestamp = datetime.now().isoformat()

    update_db("UPDATE AccessInstructions SET active_status = 0 WHERE location_id = ?", (location_id,))

    new_inst_id = insert_db("""
        INSERT INTO AccessInstructions (location_id, current_content, confidence_score, active_status)
        VALUES (?, ?, 'MEDIUM', 1)
    """, (location_id, content))

    insert_db("""
        INSERT INTO InstructionVersions
        (instruction_id, content, source, created_at, updated_at, customer_confirmation_status,
         successful_delivery_assoc, failed_delivery_assoc, reliability_score)
        VALUES (?, ?, ?, ?, ?, 'PENDING', 0, 0, 'MEDIUM')
    """, (new_inst_id, content, source, timestamp, timestamp))

    return jsonify({"success": True, "instruction_id": new_inst_id}), 201


@instructions_bp.route('/customer/<int:customer_id>', methods=['GET'])
def get_customer_instructions(customer_id):
    delivery = query_db(
        "SELECT location_id FROM Deliveries WHERE customer_id = ? AND status = 'PENDING' LIMIT 1",
        (customer_id,), one=True
    )
    if not delivery:
        delivery = query_db(
            "SELECT location_id FROM Deliveries WHERE customer_id = ? ORDER BY id DESC LIMIT 1",
            (customer_id,), one=True
        )
        if not delivery:
            return jsonify({"error": "No location found"}), 404

    location_id = delivery['location_id']
    instruction = query_db(
        "SELECT * FROM AccessInstructions WHERE location_id = ? AND active_status = 1",
        (location_id,), one=True
    )

    if not instruction:
        return jsonify({"has_instructions": False, "location_id": location_id}), 200

    return jsonify({
        "has_instructions": True,
        "instruction_id": instruction['id'],
        "location_id": location_id,
        "content": instruction['current_content']
    }), 200


def confirm_instruction_logic(instruction_id, data):
    """Shared logic used by both /api/instructions/<id>/confirm and /api/customer-confirmations."""
    is_correct = data.get('is_correct')
    updated_content = data.get('updated_content', '')
    timestamp = datetime.now().isoformat()

    insert_db("""
        INSERT INTO CustomerConfirmations (instruction_id, is_correct, updated_content, timestamp)
        VALUES (?, ?, ?, ?)
    """, (instruction_id, is_correct, updated_content, timestamp))

    if is_correct:
        latest_ver = query_db(
            "SELECT id FROM InstructionVersions WHERE instruction_id = ? ORDER BY id DESC LIMIT 1",
            (instruction_id,), one=True
        )
        if latest_ver:
            update_db("""
                UPDATE InstructionVersions
                SET customer_confirmation_status = 'CONFIRMED', reliability_score = 'HIGH', updated_at = ?
                WHERE id = ?
            """, (timestamp, latest_ver['id']))
        update_db("UPDATE AccessInstructions SET confidence_score = 'HIGH' WHERE id = ?", (instruction_id,))
        return {"success": True, "new_instruction_id": instruction_id}

    # Customer says instructions are wrong -> deactivate old, create a new version if content supplied.
    inst = query_db("SELECT location_id FROM AccessInstructions WHERE id = ?", (instruction_id,), one=True)
    update_db("UPDATE AccessInstructions SET active_status = 0 WHERE id = ?", (instruction_id,))

    new_inst_id = instruction_id
    if updated_content and inst:
        new_inst_id = insert_db("""
            INSERT INTO AccessInstructions (location_id, current_content, confidence_score, active_status)
            VALUES (?, ?, 'HIGH', 1)
        """, (inst['location_id'], updated_content))
        insert_db("""
            INSERT INTO InstructionVersions
            (instruction_id, content, source, created_at, updated_at, customer_confirmation_status,
             successful_delivery_assoc, failed_delivery_assoc, reliability_score)
            VALUES (?, ?, 'customer', ?, ?, 'CONFIRMED', 0, 0, 'HIGH')
        """, (new_inst_id, updated_content, timestamp, timestamp))

    return {"success": True, "new_instruction_id": new_inst_id}


@instructions_bp.route('/<int:instruction_id>/confirm', methods=['POST'])
def confirm_instruction(instruction_id):
    data = request.json or {}
    result = confirm_instruction_logic(instruction_id, data)
    return jsonify(result), 200
