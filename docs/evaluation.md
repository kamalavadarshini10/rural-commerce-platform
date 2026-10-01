# Evaluation

## Purpose

This document explains how RuralRoute's baseline-vs-prototype evaluation
works, what it measures, and what the results do and do not prove.

The evaluation uses a deterministic set of 20 synthetic delivery scenarios.
The scenarios are designed to represent common rural-delivery conditions such
as GPS availability, missing landmarks, access instructions, previous delivery
failures, customer confirmation, and offline operation.

These results are synthetic prototype evaluation results. They demonstrate
that the evaluation pipeline, decision logic, and metrics are implemented
end-to-end. They are not real-world measurements and must not be presented as
evidence of real-world impact.

## Running the Evaluation

From the project root:

```bash
python experiments/evaluate.py

The evaluation runs the baseline and RuralRoute simulations using the same
20 deterministic scenarios and prints a side-by-side comparison.

The individual simulations can also be run independently:

python experiments/baseline.py
python experiments/prototype.py
Evaluation Scenarios

The evaluation contains 20 deterministic synthetic delivery scenarios.

Each scenario can include factors such as:

GPS availability
Landmark availability
Access-instruction availability
Instruction confidence
Previous delivery failures
Customer confirmation
Offline operation
Delivery difficulty

Using the same scenarios for both modes makes the comparison controlled and
reproducible.

What "Baseline" Means

The baseline represents a simple GPS-only delivery approach.

Its decision logic is intentionally limited:

If GPS is available, the delivery succeeds.
If GPS is unavailable, the delivery fails.
It does not use captured access instructions.
It does not use customer confirmation.
It does not perform instruction-confidence evaluation.
It does not recover deliveries through offline instructions.

This provides a simple reference point against which the RuralRoute decision
logic can be evaluated.

What "RuralRoute" Means

RuralRoute uses additional information and decision logic that is not
available in the GPS-only baseline.

The prototype can consider:

GPS availability
landmarks
captured access instructions
instruction confidence
previous delivery failures
customer confirmation
offline operation
repeat-failure warnings

The decision engine can select actions such as:

USE_GPS
USE_LANDMARK_AND_INSTRUCTION
USE_CONFIRMED_INSTRUCTION
VERIFY_CUSTOMER
REQUEST_VERIFICATION

A previous repeat failure causes the system to require customer verification
rather than blindly recommending the same access instructions.

Evaluation Results

The current deterministic 20-scenario evaluation produced the following
results:

Metric	Baseline	RuralRoute
Total scenarios	20	20
Successful deliveries	8	14
Failed deliveries	12	6
Success rate	40.0%	70.0%
Failure rate	60.0%	30.0%
Repeat-failure locations	2	2
Instruction reuse rate	0%	30.0%
Customer confirmation rate	0%	45.0%
Offline recovery rate	0%	100.0%
Failure Reduction

The failure reduction is calculated as:

Failure reduction
= (Baseline failures - RuralRoute failures)
  / Baseline failures × 100

= (12 - 6) / 12 × 100

= 50%

Therefore, in this synthetic 20-scenario evaluation, RuralRoute produced
6 failures compared with 12 failures for the baseline, corresponding to a
50% reduction in total delivery failures.

Important Interpretation of Repeat Failures

The evaluation produced:

Baseline repeat-failure locations   = 2
RuralRoute repeat-failure locations = 2

Therefore, this experiment does not demonstrate a reduction in the number
of repeat-failure locations.

Instead, repeat-failure handling is demonstrated through the decision engine
and automated tests. When a location has repeated failures, the system
detects the condition and can require customer verification before relying on
previous instructions.

The repeat-failure metric should therefore not be interpreted as evidence
that RuralRoute eliminates repeat failures.

Additional Metrics
Instruction Reuse

The RuralRoute prototype achieved a 30.0% instruction reuse rate in the
20-scenario evaluation.

The baseline has no instruction-reuse mechanism, so its corresponding value
is 0%.

Customer Confirmation

RuralRoute recorded a 45.0% customer confirmation rate in the evaluation.

The baseline does not use customer confirmation, so its corresponding value
is 0%.

Offline Recovery

RuralRoute achieved a 100.0% offline recovery rate in the synthetic
evaluation.

The baseline does not provide an equivalent instruction-based offline
recovery mechanism, so its corresponding value is 0%.

Offline Synchronization and Conflict Resolution

RuralRoute supports store-and-forward operation through the offline sync
endpoint.

When an offline delivery outcome is created, the client records the
sync_version of the delivery.

When the device reconnects:

The client sends the offline outcome and its stored version.
The server reads the current delivery version.
If the versions match, the update is accepted.
The delivery version is incremented after the update.
If the client version is older than the server version, the update is
rejected as a conflict.
The conflict is returned to the client instead of silently overwriting the
newer server state.

This prevents a stale offline update from overwriting a newer delivery
outcome.

Automated Testing

The project contains automated tests for the API, decision engine,
repeat-failure logic, confidence/reliability rules, and offline
synchronization.

The complete test suite currently reports:

39 passed

The decision-engine tests cover cases including:

missing instructions
recent successful instructions
customer-confirmed instructions
older successful instructions
previous delivery failures
low-confidence verification requirements
repeat-failure detection
repeat-failure summaries

The offline synchronization tests also verify that an older offline version
is detected as a conflict after a newer online update has changed the server
version.

Metrics Computed
Metric	Description
Success rate	Successful deliveries divided by total scenarios
Failure rate	Failed deliveries divided by total scenarios
Failure reduction	Reduction in baseline failures compared with RuralRoute
Repeat-failure locations	Locations with more than one delivery failure
Instruction reuse rate	Scenarios where captured instructions were successfully reused
Customer confirmation rate	Scenarios using customer-confirmed instructions
Offline recovery rate	Offline scenarios successfully recovered by RuralRoute
Decision action	Rule-based action selected for each scenario
Limitations
The evaluation uses only 20 synthetic scenarios.
The scenarios are deterministic and are not real delivery records.
The evaluation does not represent a statistically significant real-world
deployment.
Synthetic scenarios cannot establish real-world delivery improvement.
The baseline is a simplified GPS-only reference implementation rather than
a complete commercial delivery system.
Repeat-failure locations remained at 2 in both modes in this evaluation.
Agent input effort is not measured through a formal user study.
A larger real-world dataset and field trial would be required to measure
actual operational impact.
Conclusion

The current prototype evaluation demonstrates that RuralRoute can be
compared against a defined GPS-only baseline using the same deterministic
scenario set.

In the 20-scenario synthetic evaluation:

RuralRoute completed 14 deliveries compared with 8 for the baseline.
RuralRoute recorded 6 failures compared with 12 for the baseline.
The calculated reduction in total failures was 50%.
Instruction reuse was 30%.
Customer confirmation was 45%.
Offline recovery was 100%.
Repeat-failure locations remained at 2 for both modes.

The results demonstrate the implemented evaluation pipeline and prototype
decision logic. They should not be interpreted as measured real-world
performance.