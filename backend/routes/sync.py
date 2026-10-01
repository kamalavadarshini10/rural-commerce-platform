from flask import Blueprint, request, jsonify
from database.db import query_db
from services.delivery_service import apply_delivery_outcome

sync_bp = Blueprint('sync', __name__)


@sync_bp.route('', methods=['POST'])
def sync_data():
    """
    POST /api/sync

    Receives actions performed while the device was offline.

    Conflict resolution:
    - Client sends the sync_version it had when the action was created.
    - Server compares it with the current delivery version.
    - If versions match, the update is applied.
    - If versions differ, the update is rejected as a conflict.
    """

    payloads = request.json or []

    synced = []
    failed = []
    conflicts = []

    for item in payloads:

        if item.get('type') != 'delivery_outcome':
            continue

        delivery_id = item.get('delivery_id')
        payload = item.get('payload', {})

        client_version = item.get('sync_version')

        delivery = query_db(
            "SELECT sync_version FROM Deliveries WHERE id = ?",
            (delivery_id,),
            one=True
        )

        if not delivery:
            failed.append({
                "delivery_id": delivery_id,
                "error": "Delivery not found"
            })
            continue

        server_version = delivery['sync_version']

        # Conflict check
        if client_version is not None and client_version != server_version:
            conflicts.append({
                "delivery_id": delivery_id,
                "client_version": client_version,
                "server_version": server_version,
                "reason": "Offline update is based on an older version"
            })
            continue

        # Apply the offline outcome
        result, status = apply_delivery_outcome(
            delivery_id,
            payload
        )

        if status == 200:

            # Increase version after successful synchronization
            # query_db(
            #     "SELECT sync_version FROM Deliveries WHERE id = ?",
            #     (delivery_id,),
            #     one=True
            # )

            # from database.db import update_db

            # update_db(
            #     "UPDATE Deliveries SET sync_version = sync_version + 1 WHERE id = ?",
            #     (delivery_id,)
            # )

            synced.append(delivery_id)

        else:
            failed.append({
                "delivery_id": delivery_id,
                "error": result.get("error")
            })

    return jsonify({
        "success": len(failed) == 0 and len(conflicts) == 0,
        "synced_count": len(synced),
        "synced_ids": synced,
        "failed": failed,
        "conflicts": conflicts,
        "conflict_count": len(conflicts)
    }), 200