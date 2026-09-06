# Phase 2: Synthetic Dataset and Database Schema

## Overview
This document outlines the SQLite database schema and the synthetic dataset generated for the **RuralRoute** prototype. The dataset provides realistic rural delivery scenarios, including difficult and failed cases, to effectively test both the Baseline and Prototype evaluation modes under equivalent controlled conditions.

## Database Schema
The database (`ruralroute.db`) consists of the following 11 tables:

1. **Users**: Stores application users (Delivery Agents, Admins).
2. **Customers**: Stores customer details linked to deliveries.
3. **Locations**: Stores delivery destinations with expanded fields (`basic_address`, `landmark`, `gps_available`, `network_available`, `sensor_available`, `road_condition`, `vehicle_accessibility`, `notes`) to accurately model rural and difficult terrain.
4. **AccessInstructions**: Stores the active set of access instructions and its calculated `confidence_score` for a location.
5. **InstructionVersions**: Tracks the history, origin (`source`), and confirmation status of each instruction to prevent blind overwriting and provide an audit trail.
6. **CustomerConfirmations**: Logs instances where a customer reviews an instruction to CONFIRM or UPDATE it.
7. **Deliveries**: Tracks the actual delivery jobs assigned to agents.
8. **FailureReasons**: A static lookup table of common failure reasons (e.g., "Locked gate", "Road inaccessible") to minimize frontline worker typing.
9. **DeliveryOutcomes**: Records the result of a delivery attempt. Expanded to track whether instructions were shown, reused, or found incorrect.
10. **InstructionUsageLogs**: Explicitly records how instructions were interacted with during a delivery to calculate the "Instruction reuse rate".
11. **SyncQueue**: Stores offline payload events that need synchronization with the backend once network connectivity is restored.

## Synthetic Dataset Design
The dataset is generated deterministically (using `random.seed(42)`) to ensure reproducibility during academic evaluation. 

### Seeded Scenarios
The database is pre-populated with 7 distinct location profiles that model the required test scenarios:

1. **New Location**: No previous history, good road, GPS/Network available. *(Tests baseline data capture)*.
2. **Previous Successful Delivery**: Has historical success and high-confidence instructions. *(Tests instruction reuse)*.
3. **Previous Failed Delivery**: Has historical failure (Road inaccessible), no saved instructions. *(Tests decision logic handling of failures)*.
4. **Repeat Failures**: Multiple past failures (Locked gate, Customer unavailable) for the same location. *(Tests repeat-failure detection and reporting)*.
5. **Customer-Confirmed Instructions**: High confidence instructions recently verified by the customer. *(Tests highest reliability tier)*.
6. **Outdated Instructions**: Old instructions (1 year old) where the landmark has changed, flagged as LOW confidence. *(Tests decision logic warning "VERIFY")*.
7. **Poor Access / Fallback**: Estate bungalow with a frequently locked gate; missing sensor and network availability. *(Tests offline/fallback workflows)*.

### Validation Data
- **7** Locations created.
- **7** Pending deliveries ready for the Agent to process in the Demo.
- **3** Historical failed deliveries (to trigger repeat failure and low confidence logic).
- **3** Access Instructions captured (combining high and low confidence).

## Reproducibility
To regenerate the dataset from scratch, run the following command from the `experiments/` directory:
```bash
python generate_dataset.py
```
This script automatically drops the existing `ruralroute.db` and recreates the tables and seed data, ensuring a clean slate for Baseline vs. Prototype testing.
