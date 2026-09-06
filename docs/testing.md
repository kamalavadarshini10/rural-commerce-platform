# Testing

## Running the Tests

```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v
```

A `conftest.py` fixture automatically regenerates the deterministic demo
database (`experiments/generate_dataset.py`, which uses `random.seed(42)`)
once at the start of the test session, so tests always run against a known
dataset regardless of what manual demoing has changed in the DB file.

**Note:** running the tests mutates `backend/database/ruralroute.db` (some
tests record real outcomes and confirmations). Re-run
`python experiments/generate_dataset.py` afterward if you want a pristine
database for a live demo.

## Coverage

`backend/tests/test_api.py` contains 28 tests covering all of the following
required areas:

| # | Area | Representative test(s) |
|---|------|------------------------|
| 1 | Login | `test_login_success_agent/admin/customer`, `test_login_wrong_password_rejected`, `test_login_unknown_user_rejected` |
| 2 | Delivery retrieval | `test_get_deliveries_for_agent`, `test_get_single_delivery`, `test_get_delivery_not_found` |
| 3 | Instruction retrieval | `test_get_delivery_instructions`, `test_get_location_instructions_route`, `test_no_instructions_for_new_location` |
| 4 | HIGH confidence | `test_high_confidence_recent_success`, `test_high_confidence_customer_confirmed` |
| 5 | MEDIUM confidence | `test_medium_confidence_old_unconfirmed_success` |
| 6 | LOW confidence | `test_low_confidence_previous_failure`, `test_low_confidence_never_recommends_after_failure`, `test_low_confidence_outdated_unconfirmed` |
| 7 | Successful delivery | `test_record_successful_delivery` |
| 8 | Failed delivery | `test_record_failed_delivery` |
| 9 | Repeat failure | `test_repeat_failure_detected`, `test_repeat_failure_summary_on_instruction_endpoint` |
| 10 | Customer confirmation | `test_customer_confirm_instructions_correct` |
| 11 | Customer update / versioning | `test_customer_update_creates_new_version` |
| 12 | Offline synchronization | `test_offline_sync_replays_queued_outcomes`, `test_offline_sync_reports_failure_for_bad_delivery_id` |

Plus smoke tests for `/api/health`, `/api/admin/analytics`, and instruction
capture (`POST /api/instructions`).

## Manual / Frontend Testing

The frontend has no automated test suite (out of scope for this prototype).
It was verified manually via `npm run build` (production build succeeds with
no errors) and by exercising the full demo flow described in `README.md`
against the running Flask backend.

## What Is Deliberately Not Tested

- Real network failure/reconnection (the offline mode is demoed via a
  manual "Simulate Offline" toggle in the UI, not real network interruption).
- Concurrent-write race conditions (SQLite + Flask dev server, single-agent
  demo dataset — not a concern at this scale).
- Security/auth hardening — see README "Known limitations".
