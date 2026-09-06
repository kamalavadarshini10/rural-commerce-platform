from database.db import query_db, insert_db, update_db
from datetime import datetime


def apply_delivery_outcome(delivery_id, data):
    """
    Applies a delivery outcome (SUCCESS/FAILURE) to the database.
    Shared by the direct API route (routes/deliveries.py) and the offline
    sync route (routes/sync.py) so both online and offline flows use the
    exact same logic.

    Returns (result_dict, http_status_code)
    """
    outcome = data.get('outcome')  # 'SUCCESS' or 'FAILURE'
    reason_id = data.get('reason_id')
    note = data.get('note', '')
    instruction_id = data.get('instruction_id')
    instructions_verified = data.get('instructions_verified', False)

    instructions_available = data.get('instructions_available', False)
    instructions_shown = data.get('instructions_shown', False)
    instructions_reused = data.get('instructions_reused', False)
    instructions_incorrect = data.get('instructions_incorrect', False)

    delivery = query_db("SELECT location_id, attempt_number FROM Deliveries WHERE id = ?", (delivery_id,), one=True)
    if not delivery:
        return {"error": "Delivery not found"}, 404

    location_id = delivery['location_id']
    attempt_number = delivery['attempt_number']
    timestamp = datetime.now().isoformat()

    update_db("UPDATE Deliveries SET status = ? WHERE id = ?",
              ('COMPLETED' if outcome == 'SUCCESS' else 'FAILED', delivery_id))

    insert_db("""
        INSERT INTO DeliveryOutcomes
        (delivery_id, location_id, attempt_number, outcome, failure_reason_id, optional_note, timestamp,
         instructions_available, instructions_shown, instructions_reused, instructions_incorrect)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (delivery_id, location_id, attempt_number, outcome, reason_id, note, timestamp,
          instructions_available, instructions_shown, instructions_reused, instructions_incorrect))

    if instruction_id:
        insert_db("""
            INSERT INTO InstructionUsageLogs
            (delivery_id, instruction_id, was_displayed, was_reused, was_verified, assoc_with_success, assoc_with_fail)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (delivery_id, instruction_id, instructions_shown, instructions_reused, instructions_verified,
              outcome == 'SUCCESS', outcome == 'FAILURE'))

        latest_ver = query_db(
            "SELECT id FROM InstructionVersions WHERE instruction_id = ? ORDER BY id DESC LIMIT 1",
            (instruction_id,), one=True
        )
        if latest_ver:
            if outcome == 'SUCCESS':
                update_db(
                    "UPDATE InstructionVersions SET successful_delivery_assoc = 1, updated_at = ? WHERE id = ?",
                    (timestamp, latest_ver['id'])
                )
            else:
                update_db(
                    "UPDATE InstructionVersions SET failed_delivery_assoc = 1, updated_at = ? WHERE id = ?",
                    (timestamp, latest_ver['id'])
                )

    new_instruction_content = data.get('new_instruction')
    if new_instruction_content:
        update_db("UPDATE AccessInstructions SET active_status = 0 WHERE location_id = ?", (location_id,))
        new_inst_id = insert_db("""
            INSERT INTO AccessInstructions (location_id, current_content, confidence_score, active_status)
            VALUES (?, ?, 'MEDIUM', 1)
        """, (location_id, new_instruction_content))
        insert_db("""
            INSERT INTO InstructionVersions
            (instruction_id, content, source, created_at, updated_at, customer_confirmation_status,
             successful_delivery_assoc, failed_delivery_assoc, reliability_score)
            VALUES (?, ?, 'agent', ?, ?, 'PENDING', ?, ?, 'MEDIUM')
        """, (new_inst_id, new_instruction_content, timestamp, timestamp,
              outcome == 'SUCCESS', outcome == 'FAILURE'))

    return {"success": True}, 200
