import pytest
import sys
import os

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..')
    )
)

from app import create_app

from services.decision_engine import (
    evaluate_instruction_reliability,
    get_location_failure_summary
)


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


# 1. No instruction -------------------------------------------------------

def test_no_instruction_is_low(app):

    with app.app_context():
        result = evaluate_instruction_reliability(None)

    assert result['level'] == 'LOW'


# 2. High confidence recent success --------------------------------------

def test_high_confidence_recent_success(app):

    with app.app_context():
        result = evaluate_instruction_reliability(1)

    assert result['level'] == 'HIGH'


# 3. Customer confirmed instruction --------------------------------------

def test_high_confidence_customer_confirmed(app):

    with app.app_context():
        result = evaluate_instruction_reliability(3)

    assert result['level'] == 'HIGH'


# 4. Medium confidence old success ---------------------------------------

def test_medium_confidence_old_unconfirmed_success(app):

    with app.app_context():
        result = evaluate_instruction_reliability(5)

    assert result['level'] == 'MEDIUM'


# 5. Low confidence after previous failure -------------------------------

def test_low_confidence_previous_failure(app):

    with app.app_context():
        result = evaluate_instruction_reliability(4)

    assert result['level'] == 'LOW'


# 6. Low confidence should not recommend after failure -------------------

def test_low_confidence_never_recommends_after_failure(app):

    with app.app_context():
        result = evaluate_instruction_reliability(4)

    assert result['level'] == 'LOW'
    assert 'verify' in result['reason'].lower()


# 7. Outdated unconfirmed instruction ------------------------------------

def test_low_confidence_unconfirmed_instruction(app):

    with app.app_context():
        result = evaluate_instruction_reliability(7)

    assert result['level'] == 'MEDIUM'


# 8. Repeat failure detection --------------------------------------------

def test_repeat_failure_detected(app):

    with app.app_context():
        result = get_location_failure_summary(4)

    assert result['is_repeat_failure'] is True
    assert result['failures'] > 1


# 9. Repeat failure summary ----------------------------------------------

def test_repeat_failure_summary_contains_reasons(app):

    with app.app_context():
        result = get_location_failure_summary(4)

    assert result['attempts'] > 0
    assert result['failures'] > 1
    assert len(result['reasons']) > 0
# 10. Invalid instruction ID ---------------------------------------------

def test_invalid_instruction_is_low(app):

    with app.app_context():
        result = evaluate_instruction_reliability(99999)

    assert result['level'] == 'LOW'


# 11. Missing location has no failures -----------------------------------

def test_location_without_failures_is_not_repeat_failure(app):

    with app.app_context():
        result = get_location_failure_summary(1)

    assert result['is_repeat_failure'] is False


# 12. Failure summary returns expected fields ----------------------------

def test_failure_summary_structure(app):

    with app.app_context():
        result = get_location_failure_summary(4)

    assert 'attempts' in result
    assert 'failures' in result
    assert 'reasons' in result
    assert 'is_repeat_failure' in result