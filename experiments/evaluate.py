"""
evaluate.py

Compares the standard baseline with the RuralRoute
synthetic evaluation using the same scenarios.
"""

from baseline import run_baseline
from prototype import run_prototype


def calculate_percentage(value):
    return round(value * 100, 1)


def main():

    baseline = run_baseline()
    ruralroute = run_prototype()

    print()
    print("=" * 60)
    print("           RURALROUTE EVALUATION")
    print("=" * 60)

    print()

    print(f"{'Metric':<30} {'Baseline':>12} {'RuralRoute':>12}")
    print("-" * 60)

    print(
        f"{'Total scenarios':<30}"
        f"{baseline['total_attempts']:>12}"
        f"{ruralroute['total_attempts']:>12}"
    )

    print(
        f"{'Successful deliveries':<30}"
        f"{baseline['success_count']:>12}"
        f"{ruralroute['success_count']:>12}"
    )

    print(
        f"{'Failed deliveries':<30}"
        f"{baseline['failure_count']:>12}"
        f"{ruralroute['failure_count']:>12}"
    )

    print(
        f"{'Success rate':<30}"
        f"{calculate_percentage(baseline['success_rate']):>11}%"
        f"{calculate_percentage(ruralroute['success_rate']):>11}%"
    )

    print(
        f"{'Failure rate':<30}"
        f"{calculate_percentage(baseline['failure_rate']):>11}%"
        f"{calculate_percentage(ruralroute['failure_rate']):>11}%"
    )

    print(
        f"{'Repeat-failure locations':<30}"
        f"{baseline['repeat_failure_locations']:>12}"
        f"{ruralroute['repeat_failure_locations']:>12}"
    )

    print(
        f"{'Instruction reuse rate':<30}"
        f"{calculate_percentage(baseline.get('instruction_reuse_rate', 0)):>11}%"
        f"{calculate_percentage(ruralroute.get('instruction_reuse_rate', 0)):>11}%"
    )

    print(
        f"{'Customer confirmation rate':<30}"
        f"{calculate_percentage(baseline.get('customer_confirmation_rate', 0)):>11}%"
        f"{calculate_percentage(ruralroute.get('customer_confirmation_rate', 0)):>11}%"
    )

    print(
        f"{'Offline recovery rate':<30}"
        f"{calculate_percentage(baseline.get('offline_recovery_rate', 0)):>11}%"
        f"{calculate_percentage(ruralroute.get('offline_recovery_rate', 0)):>11}%"
    )

    print("-" * 60)

    baseline_failures = baseline["failure_count"]
    ruralroute_failures = ruralroute["failure_count"]

    if baseline_failures > 0:

        failure_reduction = (
            (baseline_failures - ruralroute_failures)
            / baseline_failures
        ) * 100

    else:
        failure_reduction = 0

    print()
    print("Failure reduction:")
    print(f"{failure_reduction:.1f}%")

    print()
    print("=" * 60)
    print("Evaluation completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()