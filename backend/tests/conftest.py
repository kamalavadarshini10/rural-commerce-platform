import subprocess
import sys
import os
import pytest

EXPERIMENTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'experiments')


@pytest.fixture(scope="session", autouse=True)
def regenerate_demo_database():
    """
    Regenerates the synthetic demo database once per test session, so tests
    run against a known, reproducible dataset (random.seed(42) in
    generate_dataset.py) regardless of what manual testing/demoing has
    changed in the DB beforehand.
    """
    subprocess.run(
        [sys.executable, "generate_dataset.py"],
        cwd=EXPERIMENTS_DIR,
        check=True,
        capture_output=True
    )
    yield
