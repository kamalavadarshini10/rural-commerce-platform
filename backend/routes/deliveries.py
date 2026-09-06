from flask import Blueprint, request, jsonify
from database.db import query_db
from services.decision_engine import evaluate_instruction_reliability, get_location_failure_summary
from services.delivery_service import apply_delivery_outcome

deliveries_bp = Blueprint('deliveries', __name__)


@deliveries_bp.route('', methods=['GET'])
@deliveries_bp.route('/', methods=['GET'])
def get_deliveries():
    agent_id = request.args.get('agent_id')

    query = """
        SELECT d.id, d.status, d.attempt_number, l.basic_address, l.landmark,
               l.gps_available, l.network_available, l.id as location_id,
               c.name as customer_name, c.phone
        FROM Deliveries d
        JOIN Locations l ON d.location_id = l.id
        JOIN Customers c ON d.customer_id = c.id
        WHERE d.agent_id = ? AND d.status = 'PENDING'
    """
    deliveries = query_db(query, (agent_id,))
    return jsonify(deliveries), 200


@deliveries_bp.route('/<int:delivery_id>', methods=['GET'])
def get_delivery(delivery_id):
    query = """
        SELECT d.id, d.status, d.attempt_number, l.id as location_id, l.basic_address, l.landmark,
               l.gps_available, l.network_available, l.sensor_available, l.road_condition,
               l.vehicle_accessibility, c.name as customer_name, c.phone
        FROM Deliveries d
        JOIN Locations l ON d.location_id = l.id
        JOIN Customers c ON d.customer_id = c.id
        WHERE d.id = ?
    """
    delivery = query_db(query, (delivery_id,), one=True)
    if not delivery:
        return jsonify({"error": "Not found"}), 404
    delivery['failure_summary'] = get_location_failure_summary(delivery['location_id'])
    return jsonify(delivery), 200


@deliveries_bp.route('/<int:delivery_id>/instructions', methods=['GET'])
def get_delivery_instructions(delivery_id):
    delivery = query_db("SELECT location_id FROM Deliveries WHERE id = ?", (delivery_id,), one=True)
    if not delivery:
        return jsonify({"error": "Not found"}), 404

    location_id = delivery['location_id']
    instruction = query_db(
        "SELECT * FROM AccessInstructions WHERE location_id = ? AND active_status = 1",
        (location_id,), one=True
    )
    failure_summary = get_location_failure_summary(location_id)

    if not instruction:
        return jsonify({
            "has_instructions": False,
            "failure_summary": failure_summary
        }), 200

    reliability = evaluate_instruction_reliability(instruction['id'])

    return jsonify({
        "has_instructions": True,
        "instruction_id": instruction['id'],
        "content": instruction['current_content'],
        "confidence": reliability['level'],
        "reason": reliability['reason'],
        "failure_summary": failure_summary
    }), 200


@deliveries_bp.route('/<int:delivery_id>/outcome', methods=['POST'])
def record_outcome(delivery_id):
    data = request.json or {}
    result, status = apply_delivery_outcome(delivery_id, data)
    return jsonify(result), status


@deliveries_bp.route('/failure-reasons', methods=['GET'])
def get_failure_reasons():
    reasons = query_db("SELECT * FROM FailureReasons")
    return jsonify(reasons), 200
