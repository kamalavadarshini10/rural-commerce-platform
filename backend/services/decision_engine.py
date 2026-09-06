from database.db import query_db
from datetime import datetime

RECENCY_WINDOW_DAYS = 30


def _parse_ts(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def _days_ago(ts):
    dt = _parse_ts(ts)
    if not dt:
        return None
    return (datetime.now() - dt).days


def evaluate_instruction_reliability(instruction_id):
    """
    Explainable, rule-based reliability evaluation.

    Rules (checked in this order):
      1. LOW/VERIFY  - latest version is associated with a previous FAILED delivery.
                        (Never recommend instructions blindly after a failure.)
      2. HIGH        - customer confirmed the instructions within the last
                        RECENCY_WINDOW_DAYS days.
      3. HIGH        - instructions were used on a SUCCESSFUL delivery within
                        the last RECENCY_WINDOW_DAYS days.
      4. MEDIUM      - instructions were successful at some point, but that
                        success is old and/or the instructions were never
                        confirmed by the customer.
      5. LOW/VERIFY  - unconfirmed / insufficient information (default).

    Returns a dict: { "level": "HIGH" | "MEDIUM" | "LOW", "reason": "<text>" }
    """
    if not instruction_id:
        return {"level": "LOW", "reason": "No captured access instructions for this location yet."}

    versions = query_db(
        "SELECT * FROM InstructionVersions WHERE instruction_id = ? ORDER BY id DESC",
        (instruction_id,)
    )

    if not versions:
        return {"level": "LOW", "reason": "No captured access instructions for this location yet."}

    latest = versions[0]

    # Rule 1: never blindly trust instructions tied to a previous failure.
    if latest['failed_delivery_assoc']:
        return {
            "level": "LOW",
            "reason": "These instructions were associated with a previous failed delivery. Verify with the customer before relying on them."
        }

    # Rule 2: recently customer-confirmed
    if latest['customer_confirmation_status'] == 'CONFIRMED':
        age = _days_ago(latest['updated_at']) if latest['updated_at'] else _days_ago(latest['created_at'])
        if age is None or age <= RECENCY_WINDOW_DAYS:
            when = f"{age} day(s) ago" if age is not None else "recently"
            return {
                "level": "HIGH",
                "reason": f"Customer confirmed these instructions {when} and no failures have occurred since."
            }
        else:
            return {
                "level": "MEDIUM",
                "reason": f"Customer confirmed these instructions {age} days ago, but the confirmation is old. Consider verifying."
            }

    # Rule 3: recently used on a successful delivery
    if latest['successful_delivery_assoc']:
        age = _days_ago(latest['updated_at']) if latest['updated_at'] else _days_ago(latest['created_at'])
        if age is None or age <= RECENCY_WINDOW_DAYS:
            when = f"{age} day(s) ago" if age is not None else "recently"
            return {
                "level": "HIGH",
                "reason": f"Successfully used on a delivery {when}."
            }
        # Rule 4: old success, not confirmed
        return {
            "level": "MEDIUM",
            "reason": f"Previously successful ({age} days ago) but not recently confirmed by the customer."
        }

    # Rule 4b: explicit stored score from an unconfirmed capture, not yet tied to any outcome
    if latest['reliability_score'] == 'MEDIUM':
        return {
            "level": "MEDIUM",
            "reason": "Instructions were captured but have not yet been confirmed or used on a completed delivery."
        }

    # Rule 5: default - unconfirmed / insufficient info
    return {
        "level": "LOW",
        "reason": "Instructions are unconfirmed and have no successful delivery history. Verify before use."
    }


def get_location_failure_summary(location_id):
    """
    Returns attempt/failure counts and reasons for a location, used for
    repeat-failure warnings shown to the agent and in the admin dashboard.
    """
    attempts = query_db(
        "SELECT COUNT(*) as c FROM DeliveryOutcomes WHERE location_id = ?",
        (location_id,), one=True
    )['c']

    failures = query_db(
        "SELECT COUNT(*) as c FROM DeliveryOutcomes WHERE location_id = ? AND outcome = 'FAILURE'",
        (location_id,), one=True
    )['c']

    reasons_rows = query_db("""
        SELECT fr.reason_text, COUNT(*) as cnt
        FROM DeliveryOutcomes do
        JOIN FailureReasons fr ON do.failure_reason_id = fr.id
        WHERE do.location_id = ? AND do.outcome = 'FAILURE'
        GROUP BY fr.reason_text
        ORDER BY cnt DESC
    """, (location_id,))

    return {
        "attempts": attempts,
        "failures": failures,
        "reasons": [r['reason_text'] for r in reasons_rows],
        "is_repeat_failure": failures > 1
    }
