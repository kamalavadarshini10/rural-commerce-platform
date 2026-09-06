# Problem Analysis

## The Problem

Rural delivery locations frequently lack a standard, unambiguous street address.
Delivery agents often locate a destination through informal cues — a landmark,
a description of the gate colour, a neighbour's directions — gathered on the
spot from the customer or by trial and error. When the delivery is complete
(or fails), that knowledge is normally lost: it lives in the agent's memory or
a scrap of paper, not in any system. The next agent sent to the same address
has to rediscover it from scratch, and repeat-failure locations keep failing
for the same preventable reasons (locked gates, outdated landmarks, wrong
turns) because nobody captured what actually worked or didn't last time.

## Why This Matters

- **Wasted trips**: A failed delivery attempt costs fuel, time, and customer
  trust, and in rural areas the round trip is often long.
- **Repeat failures**: Without a way to flag "this address has failed before
  and here's why", the same mistake repeats indefinitely.
- **Knowledge loss**: Access instructions an agent painstakingly worked out
  are not written down anywhere reusable.
- **Low agent bandwidth**: Rural delivery agents are busy and often working
  with unreliable connectivity; any system that demands heavy data entry or
  constant connectivity will be ignored in practice.

## Design Goals

1. Capture access instructions with minimal agent effort.
2. Make the instructions reusable and visibly explain *why* they should (or
   should not) be trusted on a given delivery.
3. Give the customer a lightweight way to confirm or correct their
   instructions, since they know their own home best.
4. Detect and surface repeat-failure locations to admins so patterns don't
   go unnoticed.
5. Never blindly recommend instructions that previously led to a failure —
   trust must be *earned* and re-verified, not assumed.
6. Work acceptably when the agent's device loses network or GPS, which is
   common in rural areas.
7. Keep the underlying logic simple, explainable, and rule-based rather than
   a black-box model, since trust in the "why" matters as much as the "what"
   for a delivery agent deciding whether to believe a recommendation.

## Non-Goals

This is a college prototype, not a production logistics platform. It does
not integrate real GPS/mapping hardware, does not use machine learning, does
not handle authentication/security beyond a simple demo login, and uses a
deliberately small, hand-designed synthetic dataset rather than
production-scale data.
