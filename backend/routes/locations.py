from flask import Blueprint, jsonify
from database.db import query_db
from services.decision_engine import evaluate_instruction_reliability, get_location_failure_summary

locations_bp = Blueprint('locations', __name__)


@locations_bp.route('/<int:location_id>/instructions', methods=['GET'])
def get_location_instructions(location_id):
    location = query_db("SELECT * FROM Locations WHERE id = ?", (location_id,), one=True)
    if not location:
        return jsonify({"error": "Location not found"}), 404

    instruction = query_db(
        "SELECT * FROM AccessInstructions WHERE location_id = ? AND active_status = 1",
        (location_id,), one=True
    )
    failure_summary = get_location_failure_summary(location_id)

    if not instruction:
        return jsonify({
            "location": location,
            "has_instructions": False,
            "failure_summary": failure_summary
        }), 200

    reliability = evaluate_instruction_reliability(instruction['id'])

    versions = query_db(
        "SELECT * FROM InstructionVersions WHERE instruction_id = ? ORDER BY id DESC",
        (instruction['id'],)
    )

    return jsonify({
        "location": location,
        "has_instructions": True,
        "instruction_id": instruction['id'],
        "content": instruction['current_content'],
        "confidence": reliability['level'],
        "reason": reliability['reason'],
        "failure_summary": failure_summary,
        "version_history": versions
    }), 200
