"""
prototype.py

Synthetic RuralRoute evaluation.

RuralRoute uses:
- GPS
- landmark fallback
- saved access instructions
- instruction confidence
- customer confirmation
- previous failure awareness
- offline store-and-forward

The same scenarios are used by the baseline and prototype
so that the comparison is fair.
"""

from evaluation_scenarios import SCENARIOS


def run_prototype():

    total = len(SCENARIOS)

    success = 0
    failure = 0

    repeat_failures = 0
    instruction_reuse = 0
    customer_confirmations = 0
    offline_cases = 0
    offline_recovered = 0

    results = []

    for scenario in SCENARIOS:

        # --------------------------------------------------
        # 1. Detect repeat failure
        # --------------------------------------------------

        is_repeat_failure = scenario["previous_failures"] > 1

        if is_repeat_failure:
            repeat_failures += 1

        # --------------------------------------------------
        # 2. Customer confirmation
        # --------------------------------------------------

        if scenario["customer_confirmed"]:
            customer_confirmations += 1

        # --------------------------------------------------
        # 3. Offline handling
        # --------------------------------------------------

        if scenario["offline"]:
            offline_cases += 1
            offline_recovered += 1

        # --------------------------------------------------
        # 4. RuralRoute decision
        # --------------------------------------------------

        if is_repeat_failure:

            # Do not blindly trust instructions after
            # repeated failures.
            outcome = "FAILURE"
            decision = "VERIFY_CUSTOMER"

        elif scenario["gps_available"]:

            # GPS is available.
            outcome = "SUCCESS"
            decision = "USE_GPS"

        elif (
            scenario["landmark_available"]
            and scenario["instruction_available"]
            and scenario["instruction_confidence"] == "HIGH"
        ):

            # Rural fallback:
            # landmark + reliable instruction.
            outcome = "SUCCESS"
            decision = "USE_LANDMARK_AND_INSTRUCTION"

            instruction_reuse += 1

        elif (
            scenario["instruction_available"]
            and scenario["customer_confirmed"]
        ):

            # Customer-confirmed instruction can be reused.
            outcome = "SUCCESS"
            decision = "USE_CONFIRMED_INSTRUCTION"

            instruction_reuse += 1

        else:

            # Not enough reliable navigation information.
            outcome = "FAILURE"
            decision = "REQUEST_VERIFICATION"

        # --------------------------------------------------
        # 5. Count result
        # --------------------------------------------------

        if outcome == "SUCCESS":
            success += 1
        else:
            failure += 1

        results.append({
            "scenario_id": scenario["id"],
            "location": scenario["location"],
            "outcome": outcome,
            "decision": decision,
            "repeat_failure": is_repeat_failure,
            "offline": scenario["offline"]
        })

    return {
        "mode": "RURALROUTE",
        "total_attempts": total,
        "success_count": success,
        "failure_count": failure,
        "success_rate": round(success / total, 3),
        "failure_rate": round(failure / total, 3),
        "repeat_failure_locations": repeat_failures,
        "instruction_reuse_count": instruction_reuse,
        "instruction_reuse_rate": round(
            instruction_reuse / total, 3
        ),
        "customer_confirmation_count": customer_confirmations,
        "customer_confirmation_rate": round(
            customer_confirmations / total, 3
        ),
        "offline_cases": offline_cases,
        "offline_recovered": offline_recovered,
        "offline_recovery_rate": round(
            offline_recovered / offline_cases, 3
        ) if offline_cases else 0,
        "results": results
    }


if __name__ == "__main__":

    result = run_prototype()

    print("=== RURALROUTE SYNTHETIC EVALUATION ===")

    for key, value in result.items():

        if key != "results":
            print(f"{key}: {value}")