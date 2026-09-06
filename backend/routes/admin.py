from flask import Blueprint, jsonify
from database.db import query_db
from services.decision_engine import evaluate_instruction_reliability

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/analytics', methods=['GET'])
def get_analytics():
    total = query_db("SELECT COUNT(*) as count FROM DeliveryOutcomes", one=True)['count']
    success = query_db("SELECT COUNT(*) as count FROM DeliveryOutcomes WHERE outcome = 'SUCCESS'", one=True)['count']
    failures = query_db("SELECT COUNT(*) as count FROM DeliveryOutcomes WHERE outcome = 'FAILURE'", one=True)['count']

    instruction_reuse = query_db(
        "SELECT COUNT(*) as count FROM InstructionUsageLogs WHERE was_reused = 1", one=True
    )['count']
    customer_confirmations = query_db(
        "SELECT COUNT(*) as count FROM CustomerConfirmations WHERE is_correct = 1", one=True
    )['count']
    customer_updates = query_db(
        "SELECT COUNT(*) as count FROM CustomerConfirmations WHERE is_correct = 0", one=True
    )['count']

    repeat_failure_locations = query_db("""
        SELECT COUNT(*) as count FROM (
            SELECT location_id FROM DeliveryOutcomes WHERE outcome = 'FAILURE'
            GROUP BY location_id HAVING COUNT(*) > 1
        )
    """, one=True)['count']

    # Low-confidence active instructions (rule-based, computed live)
    active_instructions = query_db("SELECT id FROM AccessInstructions WHERE active_status = 1")
    low_confidence_count = sum(
        1 for inst in active_instructions
        if evaluate_instruction_reliability(inst['id'])['level'] == 'LOW'
    )

    return jsonify({
        "total_deliveries": total,
        "successful_deliveries": success,
        "failed_deliveries": failures,
        "instruction_reuse_count": instruction_reuse,
        "customer_confirmation_count": customer_confirmations,
        "customer_update_count": customer_updates,
        "repeat_failure_location_count": repeat_failure_locations,
        "low_confidence_instruction_count": low_confidence_count
    }), 200


@admin_bp.route('/repeat-failures', methods=['GET'])
def get_repeat_failures():
    query = """
        SELECT l.id as location_id, l.basic_address, l.landmark, COUNT(do.id) as total_failures
        FROM Locations l
        JOIN DeliveryOutcomes do ON l.id = do.location_id
        WHERE do.outcome = 'FAILURE'
        GROUP BY l.id
        HAVING total_failures > 1
    """
    failures = query_db(query)

    results = []
    for f in failures:
        location_id = f['location_id']

        reasons_db = query_db("""
            SELECT fr.reason_text FROM DeliveryOutcomes do
            JOIN FailureReasons fr ON do.failure_reason_id = fr.id
            WHERE do.location_id = ? AND do.outcome = 'FAILURE'
        """, (location_id,))

        attempts = query_db(
            "SELECT COUNT(*) as c FROM DeliveryOutcomes WHERE location_id = ?",
            (location_id,), one=True
        )['c']

        instruction = query_db(
            "SELECT * FROM AccessInstructions WHERE location_id = ? AND active_status = 1",
            (location_id,), one=True
        )

        confidence = None
        latest_content = None
        was_reused = False
        if instruction:
            latest_content = instruction['current_content']
            confidence = evaluate_instruction_reliability(instruction['id'])['level']
            reused_row = query_db(
                "SELECT COUNT(*) as c FROM InstructionUsageLogs WHERE instruction_id = ? AND was_reused = 1",
                (instruction['id'],), one=True
            )
            was_reused = reused_row['c'] > 0

        results.append({
            "location_id": location_id,
            "address": f['basic_address'],
            "landmark": f['landmark'],
            "attempts": attempts,
            "total_failures": f['total_failures'],
            "reasons": list(set(r['reason_text'] for r in reasons_db)),
            "latest_instructions": latest_content,
            "instruction_confidence": confidence,
            "instructions_reused": was_reused
        })

    return jsonify(results), 200
