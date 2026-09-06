import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app

# Deterministic delivery IDs produced by experiments/generate_dataset.py (random.seed(42)):
#   6  -> location 1 (no instructions yet)
#   7  -> location 2 (HIGH confidence, recently successful, reusable)
#   8  -> location 3 (no instructions, has 1 prior failure)
#   9  -> location 4 (LOW confidence - tied to a previous FAILURE; repeat-failure location)
#   10 -> location 5 (HIGH confidence - customer confirmed)
#   11 -> location 6 (LOW confidence - old, unconfirmed)
#   12 -> location 7 (MEDIUM confidence - old success, never confirmed)


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# 1. Login ---------------------------------------------------------------

def test_login_success_agent(client):
    rv = client.post('/api/auth/login', json={'username': 'agent@example.com', 'password': 'agent123'})
    assert rv.status_code == 200
    body = rv.get_json()
    assert body['role'] == 'agent'


def test_login_success_admin(client):
    rv = client.post('/api/auth/login', json={'username': 'admin@example.com', 'password': 'admin123'})
    assert rv.status_code == 200
    assert rv.get_json()['role'] == 'admin'


def test_login_success_customer(client):
    rv = client.post('/api/auth/login', json={'username': 'customer@example.com', 'password': 'customer123'})
    assert rv.status_code == 200
    body = rv.get_json()
    assert body['role'] == 'customer'
    assert body['customer_id'] is not None


def test_login_wrong_password_rejected(client):
    rv = client.post('/api/auth/login', json={'username': 'agent@example.com', 'password': 'wrong'})
    assert rv.status_code == 401


def test_login_unknown_user_rejected(client):
    rv = client.post('/api/auth/login', json={'username': 'nobody@example.com', 'password': 'x'})
    assert rv.status_code == 401


# 2. Delivery retrieval ----------------------------------------------------

def test_get_deliveries_for_agent(client):
    rv = client.get('/api/deliveries?agent_id=1')
    assert rv.status_code == 200
    data = rv.get_json()
    assert isinstance(data, list)
    assert len(data) == 7  # 7 pending demo deliveries


def test_get_single_delivery(client):
    rv = client.get('/api/deliveries/7')
    assert rv.status_code == 200
    body = rv.get_json()
    assert body['location_id'] == 2
    assert 'failure_summary' in body


def test_get_delivery_not_found(client):
    rv = client.get('/api/deliveries/99999')
    assert rv.status_code == 404


# 3. Instruction retrieval --------------------------------------------------

def test_get_delivery_instructions(client):
    rv = client.get('/api/deliveries/7/instructions')
    assert rv.status_code == 200
    body = rv.get_json()
    assert body['has_instructions'] is True
    assert 'confidence' in body
    assert 'reason' in body


def test_get_location_instructions_route(client):
    """GET /api/locations/<id>/instructions per spec."""
    rv = client.get('/api/locations/2/instructions')
    assert rv.status_code == 200
    body = rv.get_json()
    assert body['has_instructions'] is True
    assert body['confidence'] == 'HIGH'


def test_no_instructions_for_new_location(client):
    rv = client.get('/api/deliveries/6/instructions')  # location 1, no captured instructions
    assert rv.status_code == 200
    body = rv.get_json()
    assert body['has_instructions'] is False


# 4. HIGH confidence ---------------------------------------------------------

def test_high_confidence_recent_success(client):
    rv = client.get('/api/deliveries/7/instructions')  # location 2
    body = rv.get_json()
    assert body['confidence'] == 'HIGH'
    assert 'success' in body['reason'].lower()


def test_high_confidence_customer_confirmed(client):
    rv = client.get('/api/deliveries/10/instructions')  # location 5
    body = rv.get_json()
    assert body['confidence'] == 'HIGH'
    assert 'confirmed' in body['reason'].lower()


# 5. MEDIUM confidence --------------------------------------------------------

def test_medium_confidence_old_unconfirmed_success(client):
    rv = client.get('/api/deliveries/12/instructions')  # location 7
    body = rv.get_json()
    assert body['confidence'] == 'MEDIUM'
    assert 'not recently confirmed' in body['reason'].lower()


# 6. LOW confidence -----------------------------------------------------------

def test_low_confidence_previous_failure(client):
    rv = client.get('/api/deliveries/9/instructions')  # location 4, tied to a failure
    body = rv.get_json()
    assert body['confidence'] == 'LOW'
    assert 'failed delivery' in body['reason'].lower()


def test_low_confidence_never_recommends_after_failure(client):
    """Explicit rule: never blindly recommend instructions after a failure."""
    rv = client.get('/api/locations/4/instructions')
    body = rv.get_json()
    assert body['confidence'] == 'LOW'


def test_low_confidence_outdated_unconfirmed(client):
    rv = client.get('/api/deliveries/11/instructions')  # location 6
    body = rv.get_json()
    assert body['confidence'] == 'LOW'


# 7. Successful delivery -------------------------------------------------------

def test_record_successful_delivery(client):
    rv = client.post('/api/deliveries/6/outcome', json={
        'outcome': 'SUCCESS',
        'note': 'Delivered without issue',
        'instructions_available': False
    })
    assert rv.status_code == 200
    assert rv.get_json()['success'] is True

    d = client.get('/api/deliveries/6').get_json()
    assert d['status'] == 'COMPLETED'


# 8. Failed delivery ------------------------------------------------------------

def test_record_failed_delivery(client):
    rv = client.post('/api/deliveries/8/outcome', json={
        'outcome': 'FAILURE',
        'reason_id': 1,
        'note': 'Gate was locked'
    })
    assert rv.status_code == 200

    d = client.get('/api/deliveries/8').get_json()
    assert d['status'] == 'FAILED'


# 9. Repeat failure ---------------------------------------------------------------

def test_repeat_failure_detected(client):
    rv = client.get('/api/admin/repeat-failures')
    assert rv.status_code == 200
    results = rv.get_json()
    location_ids = [r['location_id'] for r in results]
    assert 4 in location_ids  # location 4 has 2 recorded historical failures
    loc4 = next(r for r in results if r['location_id'] == 4)
    assert loc4['total_failures'] >= 2
    assert 'reasons' in loc4
    assert 'instruction_confidence' in loc4


def test_repeat_failure_summary_on_instruction_endpoint(client):
    rv = client.get('/api/deliveries/9/instructions')
    body = rv.get_json()
    assert body['failure_summary']['is_repeat_failure'] is True


# 10. Customer confirmation ----------------------------------------------------------

def test_customer_confirm_instructions_correct(client):
    # location 2's active instruction id is 1 in the fresh dataset
    inst = client.get('/api/locations/2/instructions').get_json()
    instruction_id = inst['instruction_id']

    rv = client.post('/api/customer-confirmations', json={
        'instruction_id': instruction_id,
        'is_correct': True
    })
    assert rv.status_code == 200
    assert rv.get_json()['success'] is True

    updated = client.get('/api/locations/2/instructions').get_json()
    assert updated['confidence'] == 'HIGH'
    assert 'confirmed' in updated['reason'].lower()


# 11. Customer update / instruction versioning ----------------------------------------

def test_customer_update_creates_new_version(client):
    inst = client.get('/api/locations/6/instructions').get_json()
    old_instruction_id = inst['instruction_id']

    rv = client.post('/api/customer-confirmations', json={
        'instruction_id': old_instruction_id,
        'is_correct': False,
        'updated_content': 'The mill was demolished - now look for the blue water tank instead'
    })
    assert rv.status_code == 200
    new_instruction_id = rv.get_json()['new_instruction_id']
    assert new_instruction_id != old_instruction_id

    updated = client.get('/api/locations/6/instructions').get_json()
    assert updated['instruction_id'] == new_instruction_id
    assert 'water tank' in updated['content'].lower()
    assert updated['confidence'] == 'HIGH'

    # Old version history is preserved, not deleted
    versions = updated['version_history']
    assert len(versions) >= 1


# 12. Offline synchronization -----------------------------------------------------------

def test_offline_sync_replays_queued_outcomes(client):
    payload = [
        {
            "type": "delivery_outcome",
            "delivery_id": 6,
            "payload": {"outcome": "SUCCESS", "note": "Synced after reconnecting"}
        }
    ]
    rv = client.post('/api/sync', json=payload)
    assert rv.status_code == 200
    body = rv.get_json()
    assert body['success'] is True
    assert body['synced_count'] == 1

    d = client.get('/api/deliveries/6').get_json()
    assert d['status'] == 'COMPLETED'


def test_offline_sync_reports_failure_for_bad_delivery_id(client):
    payload = [
        {"type": "delivery_outcome", "delivery_id": 999999, "payload": {"outcome": "SUCCESS"}}
    ]
    rv = client.post('/api/sync', json=payload)
    assert rv.status_code == 200
    body = rv.get_json()
    assert body['success'] is False
    assert len(body['failed']) == 1


# Misc / smoke -----------------------------------------------------------------------------

def test_health(client):
    rv = client.get('/api/health')
    assert rv.status_code == 200


def test_admin_analytics(client):
    rv = client.get('/api/admin/analytics')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'total_deliveries' in data
    assert 'repeat_failure_location_count' in data


def test_capture_new_instruction(client):
    rv = client.post('/api/instructions', json={
        'location_id': 1,
        'content': 'Behind the banyan tree, red mailbox',
        'source': 'agent'
    })
    assert rv.status_code == 201
    assert 'instruction_id' in rv.get_json()
