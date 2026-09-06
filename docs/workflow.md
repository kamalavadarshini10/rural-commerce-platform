# Workflow

This document walks through each role's journey through RuralRoute and how
the pieces connect end-to-end.

## Agent Workflow

1. Agent logs in (`agent@example.com` / `agent123`).
2. Dashboard lists their PENDING deliveries, each showing customer, address,
   landmark, and a GPS-availability warning where relevant.
3. Agent opens a delivery. The app fetches:
   - The location's active access instructions (if any) via
     `GET /api/deliveries/<id>/instructions`.
   - A **confidence badge** (HIGH / MEDIUM / LOW) computed by the rule-based
     decision engine, plus a **plain-English reason** for that score.
   - A **repeat-failure warning banner** if this location has more than one
     recorded failure, regardless of the current instruction's confidence.
4. If GPS is unavailable for the location, the UI clearly labels this and
   falls back to manual landmark-based navigation.
5. Agent may tap **"Verify Instructions On-Site"** before using them — this
   is logged against the delivery outcome without requiring any typing.
6. Agent marks the outcome:
   - **SUCCESS** — optionally adds/updates the access instructions in one
     short text field (this creates a new, unconfirmed instruction version).
   - **FAILURE** — picks a reason from a dropdown (no free typing required)
     and may add a short optional note.
7. If the device is offline, the outcome is queued in `localStorage`
   (`SYNC PENDING` badge shown) instead of posted immediately. When
   connectivity returns, the queue is flushed via `POST /api/sync`, which
   replays each queued outcome through the exact same backend logic as the
   online path.

## Customer Workflow

1. Customer logs in (`customer@example.com` / `customer123`).
2. Portal shows their upcoming delivery's current saved access instructions.
3. Customer taps:
   - **Confirm** — instructions are marked `CONFIRMED`, and the decision
     engine immediately upgrades them to HIGH confidence for the next
     delivery.
   - **Update** — customer types corrected instructions. The system
     deactivates the old instruction, creates a brand-new
     `AccessInstructions` + `InstructionVersions` row, and preserves the old
     version in history rather than overwriting it.

## Admin Workflow

1. Admin logs in (`admin@example.com` / `admin123`).
2. Dashboard shows aggregate stats: total deliveries, success rate,
   repeat-failure location count, instruction reuse count, customer
   confirmations/updates, and low-confidence instruction count.
3. A bar chart compares successful vs failed deliveries.
4. A **repeat-failure table** lists every location with more than one
   recorded failure, along with attempt count, failure reasons, the latest
   captured instructions, their current confidence level, and whether those
   instructions have ever been reused on a delivery.

## How the Decision Engine Fits In

Every time instructions are fetched (`GET /api/deliveries/<id>/instructions`
or `GET /api/locations/<id>/instructions`), the backend calls
`evaluate_instruction_reliability()`, a small set of ordered if/else rules
(see `docs/architecture.md`) that never require guessing at intent from raw
text — every rule is grounded in delivery outcomes and customer confirmation
timestamps already sitting in the database.

## Offline / Sync Flow

```
Agent device (offline) --outcome--> localStorage syncQueue
        |
        | (connectivity restored)
        v
POST /api/sync  [{ type: delivery_outcome, delivery_id, payload }, ...]
        |
        v
apply_delivery_outcome() -- same function used by the online route --
        |
        v
DeliveryOutcomes / InstructionVersions / InstructionUsageLogs updated
```
