from flask import Blueprint, request, jsonify
from services.delivery_service import apply_delivery_outcome

sync_bp = Blueprint('sync', __name__)


@sync_bp.route('', methods=['POST'])
def sync_data():
    """
    POST /api/sync
    Receives a list of actions performed while the agent's device was
    offline, and replays them against the real backend logic (the same
    function used by the online outcome route), so behaviour is identical
    whether an outcome is recorded online or synced later.

    Expected body: [ { "type": "delivery_outcome", "delivery_id": <id>, "payload": {...} }, ... ]
    """
    payloads = request.json or []
    synced = []
    failed = []

    for item in payloads:
        if item.get('type') == 'delivery_outcome':
            delivery_id = item.get('delivery_id')
            payload = item.get('payload', {})
            result, status = apply_delivery_outcome(delivery_id, payload)
            if status == 200:
                synced.append(delivery_id)
            else:
                failed.append({"delivery_id": delivery_id, "error": result.get("error")})

    return jsonify({
        "success": len(failed) == 0,
        "synced_count": len(synced),
        "synced_ids": synced,
        "failed": failed
    }), 200
