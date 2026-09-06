# Evaluation

## Purpose

This document explains how RuralRoute's baseline-vs-prototype evaluation
works, what it measures, and — importantly — what it does **not** prove.

All results referenced here are **synthetic prototype evaluation** results
computed from the small, deterministic demo dataset created by
`experiments/generate_dataset.py` (`random.seed(42)`). They demonstrate that
the evaluation pipeline and metrics are implemented correctly end-to-end.
They are **not** real-world measurements, were not fabricated to look
favorable, and must not be quoted as evidence of real-world impact.

## Running the Evaluation

```bash
cd experiments
python generate_dataset.py   # (re)generate the deterministic demo database
python evaluate.py           # runs baseline.py + prototype.py and prints a comparison
```

You can also run either mode independently:

```bash
python baseline.py
python prototype.py
```

## What "Baseline" Means

`baseline.py` computes delivery statistics from the **same** database but
deliberately ignores everything related to instruction capture, reuse, or
confidence scoring — as if the system only ever recorded a bare
address/location and an outcome. This is not a separate, weaker system that
was actually run; it's the same historical outcome data re-summarized
without the instruction-awareness layer, so the two summaries are directly
comparable and reproducible from one dataset.

## What "Prototype" Means

`prototype.py` computes the same core delivery statistics, plus the metrics
that only exist because the prototype has an instruction-reuse system:
instruction reuse count/rate, successful deliveries after reuse, customer
confirmation count/rate, and an offline-sync success rate.

## Metrics Computed

| Metric | Computed as |
|--------|-------------|
| First-attempt success rate | successes where `attempt_number = 1` ÷ all attempts where `attempt_number = 1` |
| Failure rate | failed outcomes ÷ total outcomes |
| Repeat-failure rate | locations with >1 failure ÷ locations with ≥1 failure |
| Instruction reuse rate | `InstructionUsageLogs.was_reused = 1` rows ÷ total outcomes |
| Customer confirmation rate | confirmations marked correct ÷ total confirmations logged |
| Successful deliveries after reuse | reused instructions where the outcome was `SUCCESS` |
| Agent interaction/input effort | qualitative: baseline requires free-typed notes every attempt; prototype uses dropdowns, pre-filled instructions, and a one-tap verify action |
| Offline synchronization success | outcomes recorded ÷ deliveries created (all outcomes that reach the DB — online or replayed via `/api/sync` — count as synced) |

## Interpreting the Small Sample

Because the demo dataset intentionally has only a handful of historical
deliveries (by design — "do not generate a huge dataset"), individual rate
metrics (e.g. "75%") should be read as illustrations of the *calculation*,
not as statistically meaningful outcomes. A real deployment would need a much
larger, real-world dataset before these numbers meant anything on their own.

## Known Limitations of This Evaluation

- Baseline and prototype are computed from the *same* historical data, not
  from two independently-run delivery campaigns — a true A/B comparison
  would require running each mode over separate delivery batches.
- Sample size is very small (single digits per scenario), by design for a
  demonstrable college prototype.
- "Agent input effort" is reported qualitatively, not measured via a user
  study.
