"""
evaluate.py - Runs both baseline.py and prototype.py against the same
synthetic database and prints a side-by-side comparison.

IMPORTANT: All numbers below come from the small synthetic dataset created
by generate_dataset.py. These are "Synthetic prototype evaluation" results
only - they demonstrate that the prototype's architecture and metrics
pipeline work end-to-end. They are NOT real-world measurements and must
never be presented as such.

Run: python evaluate.py
"""
from baseline import run_baseline
from prototype import run_prototype

COMMON_KEYS = [
    ("total_attempts", "Total Delivery Attempts"),
    ("success_count", "Successful Deliveries"),
    ("failure_count", "Failed Deliveries"),
    ("success_rate", "Success Rate"),
    ("failure_rate", "Failure Rate"),
    ("first_attempt_success_rate", "First-Attempt Success Rate"),
    ("repeat_failure_locations", "Repeat-Failure Locations"),
    ("repeat_failure_rate", "Repeat-Failure Rate (of locations w/ any failure)"),
    ("instruction_reuse_rate", "Instruction Reuse Rate"),
    ("customer_confirmation_rate", "Customer Confirmation Rate"),
    ("agent_input_effort", "Agent Input Effort"),
]


def main():
    baseline = run_baseline()
    prototype = run_prototype()

    print("=" * 70)
    print("RuralRoute Synthetic Evaluation: Baseline vs Prototype")
    print("=" * 70)
    print("NOTE: This is a SYNTHETIC PROTOTYPE EVALUATION using a small,")
    print("reproducible demo dataset. It demonstrates the evaluation pipeline")
    print("and the prototype's architecture - it does NOT prove real-world")
    print("causal improvement, and no real-world data was used or fabricated.")
    print("-" * 70)

    header = f"{'Metric':45} {'Baseline':>12} {'Prototype':>12}"
    print(header)
    print("-" * 70)
    for key, label in COMMON_KEYS:
        b_val = baseline.get(key, "-")
        p_val = prototype.get(key, "-")
        print(f"{label:45} {str(b_val):>12} {str(p_val):>12}")

    print("-" * 70)
    print("Prototype-only metrics (no equivalent in baseline by design):")
    print(f"  Instructions Shown to Agent: {prototype['instructions_shown_count']}")
    print(f"  Instruction Reuse Count: {prototype['instruction_reuse_count']}")
    print(f"  Successful Deliveries After Instruction Reuse: {prototype['successful_deliveries_after_reuse']}")
    print(f"  Customer Confirmations Logged: {prototype['customer_confirmation_count']}")
    print(f"  Offline Sync Success Rate: {prototype['offline_sync_success_rate']}")
    print("=" * 70)


if __name__ == '__main__':
    main()
