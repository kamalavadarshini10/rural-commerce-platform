"""
baseline.py

Standard baseline:
- Uses GPS/static location information only.
- Does not reuse access instructions.
- Does not use landmark fallback.
- Does not use confidence scoring.
- Does not use previous-failure intelligence.

This is a SYNTHETIC simulation for comparison only.
"""

from evaluation_scenarios import SCENARIOS


def run_baseline():
    total = len(SCENARIOS)

    success = 0
    failure = 0
    repeat_failures = 0

    results = []

    for scenario in SCENARIOS:

        # Baseline depends mainly on GPS.
        if scenario["gps_available"]:
            outcome = "SUCCESS"
        else:
            outcome = "FAILURE"

        if outcome == "SUCCESS":
            success += 1
        else:
            failure += 1

        if scenario["previous_failures"] > 1 and outcome == "FAILURE":
            repeat_failures += 1

        results.append({
            "scenario_id": scenario["id"],
            "location": scenario["location"],
            "outcome": outcome
        })

    return {
        "mode": "BASELINE",
        "total_attempts": total,
        "success_count": success,
        "failure_count": failure,
        "success_rate": round(success / total, 3),
        "failure_rate": round(failure / total, 3),
        "repeat_failure_locations": repeat_failures,
        "results": results
    }


if __name__ == "__main__":
    result = run_baseline()

    print("=== BASELINE SYNTHETIC EVALUATION ===")

    for key, value in result.items():
        if key != "results":
            print(f"{key}: {value}")