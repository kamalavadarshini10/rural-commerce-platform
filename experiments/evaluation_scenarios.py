"""
evaluation_scenarios.py

Deterministic synthetic scenarios used to compare:

1. Standard GPS/static-address baseline
2. RuralRoute decision system

These are synthetic evaluation scenarios, not real-world measurements.
The same scenarios are given to both systems so that their outcomes
can be compared fairly.
"""


SCENARIOS = [
    {
        "id": 1,
        "location": "LOC-01",
        "gps_available": True,
        "landmark_available": False,
        "instruction_available": False,
        "instruction_confidence": "LOW",
        "previous_failures": 0,
        "customer_confirmed": False,
        "offline": False,
        "difficulty": "normal"
    },

    {
        "id": 2,
        "location": "LOC-02",
        "gps_available": True,
        "landmark_available": True,
        "instruction_available": True,
        "instruction_confidence": "HIGH",
        "previous_failures": 0,
        "customer_confirmed": True,
        "offline": False,
        "difficulty": "normal"
    },

    {
        "id": 3,
        "location": "LOC-03",
        "gps_available": False,
        "landmark_available": True,
        "instruction_available": True,
        "instruction_confidence": "HIGH",
        "previous_failures": 0,
        "customer_confirmed": True,
        "offline": False,
        "difficulty": "gps_unavailable"
    },

    {
        "id": 4,
        "location": "LOC-04",
        "gps_available": False,
        "landmark_available": True,
        "instruction_available": True,
        "instruction_confidence": "HIGH",
        "previous_failures": 0,
        "customer_confirmed": False,
        "offline": False,
        "difficulty": "gps_unavailable"
    },

    {
        "id": 5,
        "location": "LOC-05",
        "gps_available": False,
        "landmark_available": False,
        "instruction_available": True,
        "instruction_confidence": "MEDIUM",
        "previous_failures": 0,
        "customer_confirmed": False,
        "offline": False,
        "difficulty": "gps_unavailable"
    },

    {
        "id": 6,
        "location": "LOC-06",
        "gps_available": True,
        "landmark_available": True,
        "instruction_available": True,
        "instruction_confidence": "HIGH",
        "previous_failures": 1,
        "customer_confirmed": True,
        "offline": False,
        "difficulty": "previous_failure"
    },

    {
        "id": 7,
        "location": "LOC-07",
        "gps_available": False,
        "landmark_available": True,
        "instruction_available": True,
        "instruction_confidence": "LOW",
        "previous_failures": 2,
        "customer_confirmed": False,
        "offline": False,
        "difficulty": "repeat_failure"
    },

    {
        "id": 8,
        "location": "LOC-08",
        "gps_available": True,
        "landmark_available": True,
        "instruction_available": False,
        "instruction_confidence": "LOW",
        "previous_failures": 0,
        "customer_confirmed": False,
        "offline": True,
        "difficulty": "offline"
    },

    {
        "id": 9,
        "location": "LOC-09",
        "gps_available": False,
        "landmark_available": True,
        "instruction_available": True,
        "instruction_confidence": "HIGH",
        "previous_failures": 1,
        "customer_confirmed": True,
        "offline": True,
        "difficulty": "offline_previous_failure"
    },

    {
        "id": 10,
        "location": "LOC-10",
        "gps_available": True,
        "landmark_available": False,
        "instruction_available": True,
        "instruction_confidence": "MEDIUM",
        "previous_failures": 0,
        "customer_confirmed": False,
        "offline": False,
        "difficulty": "medium"
    },

    {
        "id": 11,
        "location": "LOC-11",
        "gps_available": False,
        "landmark_available": True,
        "instruction_available": True,
        "instruction_confidence": "HIGH",
        "previous_failures": 0,
        "customer_confirmed": True,
        "offline": False,
        "difficulty": "gps_unavailable"
    },

    {
        "id": 12,
        "location": "LOC-12",
        "gps_available": False,
        "landmark_available": False,
        "instruction_available": False,
        "instruction_confidence": "LOW",
        "previous_failures": 0,
        "customer_confirmed": False,
        "offline": False,
        "difficulty": "no_navigation_data"
    },

    {
        "id": 13,
        "location": "LOC-13",
        "gps_available": True,
        "landmark_available": True,
        "instruction_available": True,
        "instruction_confidence": "HIGH",
        "previous_failures": 0,
        "customer_confirmed": True,
        "offline": True,
        "difficulty": "offline"
    },

    {
        "id": 14,
        "location": "LOC-14",
        "gps_available": False,
        "landmark_available": True,
        "instruction_available": True,
        "instruction_confidence": "MEDIUM",
        "previous_failures": 1,
        "customer_confirmed": False,
        "offline": False,
        "difficulty": "previous_failure"
    },

    {
        "id": 15,
        "location": "LOC-15",
        "gps_available": True,
        "landmark_available": True,
        "instruction_available": True,
        "instruction_confidence": "HIGH",
        "previous_failures": 0,
        "customer_confirmed": True,
        "offline": False,
        "difficulty": "normal"
    },

    {
        "id": 16,
        "location": "LOC-16",
        "gps_available": False,
        "landmark_available": True,
        "instruction_available": True,
        "instruction_confidence": "HIGH",
        "previous_failures": 0,
        "customer_confirmed": True,
        "offline": True,
        "difficulty": "offline"
    },

    {
        "id": 17,
        "location": "LOC-17",
        "gps_available": False,
        "landmark_available": True,
        "instruction_available": False,
        "instruction_confidence": "LOW",
        "previous_failures": 1,
        "customer_confirmed": False,
        "offline": False,
        "difficulty": "limited_information"
    },

    {
        "id": 18,
        "location": "LOC-18",
        "gps_available": True,
        "landmark_available": True,
        "instruction_available": True,
        "instruction_confidence": "MEDIUM",
        "previous_failures": 0,
        "customer_confirmed": False,
        "offline": False,
        "difficulty": "medium"
    },

    {
        "id": 19,
        "location": "LOC-19",
        "gps_available": False,
        "landmark_available": True,
        "instruction_available": True,
        "instruction_confidence": "HIGH",
        "previous_failures": 0,
        "customer_confirmed": True,
        "offline": False,
        "difficulty": "gps_unavailable"
    },

    {
        "id": 20,
        "location": "LOC-20",
        "gps_available": False,
        "landmark_available": True,
        "instruction_available": True,
        "instruction_confidence": "LOW",
        "previous_failures": 2,
        "customer_confirmed": False,
        "offline": True,
        "difficulty": "repeat_failure"
    }
]