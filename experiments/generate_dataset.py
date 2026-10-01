import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = '../backend/database/ruralroute.db'

def setup_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create Tables
    cursor.executescript("""
        CREATE TABLE Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        );

        CREATE TABLE Customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES Users(id)
        );

        CREATE TABLE Locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lat REAL,
            lng REAL,
            basic_address TEXT,
            landmark TEXT,
            gps_available BOOLEAN,
            network_available BOOLEAN,
            sensor_available BOOLEAN,
            road_condition TEXT,
            vehicle_accessibility TEXT,
            notes TEXT
        );

        CREATE TABLE AccessInstructions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER,
            current_content TEXT,
            confidence_score TEXT,
            active_status BOOLEAN,
            FOREIGN KEY(location_id) REFERENCES Locations(id)
        );

        CREATE TABLE InstructionVersions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instruction_id INTEGER,
            content TEXT,
            source TEXT,
            created_at DATETIME,
            updated_at DATETIME,
            customer_confirmation_status TEXT,
            successful_delivery_assoc BOOLEAN,
            failed_delivery_assoc BOOLEAN,
            reliability_score TEXT,
            FOREIGN KEY(instruction_id) REFERENCES AccessInstructions(id)
        );

        CREATE TABLE CustomerConfirmations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instruction_id INTEGER,
            is_correct BOOLEAN,
            updated_content TEXT,
            timestamp DATETIME,
            FOREIGN KEY(instruction_id) REFERENCES AccessInstructions(id)
        );

        CREATE TABLE Deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER,
            customer_id INTEGER,
            agent_id INTEGER,
            status TEXT,
            attempt_number INTEGER,
            sync_version INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY(location_id) REFERENCES Locations(id),
            FOREIGN KEY(customer_id) REFERENCES Customers(id),
            FOREIGN KEY(agent_id) REFERENCES Users(id)
        );

        CREATE TABLE FailureReasons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reason_text TEXT
        );

        CREATE TABLE DeliveryOutcomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            delivery_id INTEGER,
            location_id INTEGER,
            attempt_number INTEGER,
            outcome TEXT,
            failure_reason_id INTEGER,
            optional_note TEXT,
            timestamp DATETIME,
            instructions_available BOOLEAN,
            instructions_shown BOOLEAN,
            instructions_reused BOOLEAN,
            instructions_incorrect BOOLEAN,
            FOREIGN KEY(delivery_id) REFERENCES Deliveries(id),
            FOREIGN KEY(location_id) REFERENCES Locations(id),
            FOREIGN KEY(failure_reason_id) REFERENCES FailureReasons(id)
        );

        CREATE TABLE InstructionUsageLogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            delivery_id INTEGER,
            instruction_id INTEGER,
            was_displayed BOOLEAN,
            was_reused BOOLEAN,
            was_verified BOOLEAN,
            was_updated BOOLEAN,
            assoc_with_success BOOLEAN,
            assoc_with_fail BOOLEAN,
            FOREIGN KEY(delivery_id) REFERENCES Deliveries(id),
            FOREIGN KEY(instruction_id) REFERENCES AccessInstructions(id)
        );

        CREATE TABLE SyncQueue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT,
            action TEXT,
            payload TEXT,
            status TEXT
        );
    """)
    
    # Insert Static Reference Data
    reasons = [
        "Locked gate",
        "Road inaccessible",
        "Customer unavailable",
        "Incorrect access instructions",
        "Outdated instructions",
        "Changed landmark",
        "GPS unavailable",
        "Network unavailable",
        "Insufficient access information"
    ]
    cursor.executemany("INSERT INTO FailureReasons (reason_text) VALUES (?)", [(r,) for r in reasons])
    
    conn.commit()
    return conn

def generate_data(conn):
    random.seed(42) # Reproducible
    cursor = conn.cursor()
    
    # Create Users
    # NOTE: password_hash stores a PLAINTEXT demo password (not a real hash).
    # This is a college prototype - see README.md "Known limitations".
    cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES ('agent1', 'agent123', 'agent')")
    agent_id = cursor.lastrowid

    cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES ('admin1', 'admin123', 'admin')")

    # Primary demo accounts requested for the assignment (email-style usernames)
    cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES ('agent@example.com', 'agent123', 'agent')")
    cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES ('admin@example.com', 'admin123', 'admin')")
    cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES ('customer@example.com', 'customer123', 'customer')")
    customer_user_id = cursor.lastrowid

    customers_data = [
        ('Ravi Kumar', '555-0001'),
        ('Anita Sharma', '555-0002'),
        ('Vikram Singh', '555-0003'),
        ('Priya Patel', '555-0004'),
        ('Rahul Verma', '555-0005')
    ]

    cursor.executemany("INSERT INTO Customers (name, phone) VALUES (?, ?)", customers_data)

    # Link the demo customer login to the first seeded customer (Ravi Kumar)
    cursor.execute("UPDATE Customers SET user_id = ? WHERE name = 'Ravi Kumar'", (customer_user_id,))
    
    # Define locations matching requested scenarios
    locations_data = [
        # 1. New location (no history)
        (12.91, 77.51, 'House 4, near field', 'Big Banyan Tree', True, True, True, 'Good', 'Van', 'First delivery'),
        # 2. Previous successful delivery
        (12.92, 77.52, 'Red roof house', 'Village Temple', True, True, True, 'Dirt road', 'Bike only', ''),
        # 3. Previous failed delivery
        (12.93, 77.53, 'Farmhouse at end of path', 'Water tower', True, False, False, 'Poor', 'Bike only', 'Network spots are bad'),
        # 4. Repeat failures
        (12.94, 77.54, 'White house, blue gate', 'Post office', False, True, False, 'Good', 'Van', 'GPS jumps around'),
        # 5. Customer-confirmed instructions
        (12.95, 77.55, 'Green house', 'Primary School', True, True, True, 'Good', 'Van', ''),
        # 6. Outdated instructions (Landmark changed)
        (12.96, 77.56, 'Brick house', 'Old mill (demolished)', True, True, True, 'Fair', 'Van', ''),
        # 7. Locked gate / poor access
        (12.97, 77.57, 'Estate bungalow', 'Estate Gate', True, True, False, 'Private road', 'Van', 'Gate often locked')
    ]
    
    for idx, loc in enumerate(locations_data, 1):
        cursor.execute("""
            INSERT INTO Locations 
            (lat, lng, basic_address, landmark, gps_available, network_available, sensor_available, road_condition, vehicle_accessibility, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, loc)
        
    # Generate histories based on scenario
    
    now = datetime.now()
    
    # Location 2: Previous successful - this is the "reusable, HIGH confidence" demo example
    cursor.execute("INSERT INTO AccessInstructions (location_id, current_content, confidence_score, active_status) VALUES (2, 'Take dirt road right of temple, 3rd house', 'HIGH', 1)")
    inst_id = cursor.lastrowid
    inst_created = (now - timedelta(days=12)).isoformat()
    inst_updated = (now - timedelta(days=10)).isoformat()
    cursor.execute("""
        INSERT INTO InstructionVersions
        (instruction_id, content, source, created_at, updated_at, customer_confirmation_status,
         successful_delivery_assoc, failed_delivery_assoc, reliability_score)
        VALUES (?, 'Take dirt road right of temple, 3rd house', 'agent', ?, ?, 'PENDING', 1, 0, 'HIGH')
    """, (inst_id, inst_created, inst_updated))
    cursor.execute("INSERT INTO Deliveries (location_id, customer_id, agent_id, status, attempt_number) VALUES (2, 2, ?, 'COMPLETED', 1)", (agent_id,))
    del_id = cursor.lastrowid
    cursor.execute("INSERT INTO DeliveryOutcomes (delivery_id, location_id, attempt_number, outcome, optional_note, timestamp, instructions_available) VALUES (?, 2, 1, 'SUCCESS', 'Easy to find', ?, 1)", (del_id, inst_updated))
    cursor.execute("""
        INSERT INTO InstructionUsageLogs (delivery_id, instruction_id, was_displayed, was_reused, was_verified, assoc_with_success, assoc_with_fail)
        VALUES (?, ?, 1, 1, 0, 1, 0)
    """, (del_id, inst_id))
    
    # Location 3: Previous failed delivery
    cursor.execute("INSERT INTO Deliveries (location_id, customer_id, agent_id, status, attempt_number) VALUES (3, 3, ?, 'FAILED', 1)", (agent_id,))
    del_id = cursor.lastrowid
    # Reason 2 = Road inaccessible
    cursor.execute("INSERT INTO DeliveryOutcomes (delivery_id, location_id, attempt_number, outcome, failure_reason_id, optional_note, timestamp, instructions_available) VALUES (?, 3, 1, 'FAILURE', 2, 'Path flooded', ?, 0)", (del_id, (now - timedelta(days=2)).isoformat()))
    
    # Location 4: Repeat failures - also the "instructions tied to a previous failure" LOW/VERIFY demo example
    cursor.execute("INSERT INTO AccessInstructions (location_id, current_content, confidence_score, active_status) VALUES (4, 'White house behind the post office, blue gate', 'LOW', 1)")
    loc4_inst_id = cursor.lastrowid
    loc4_ts = (now - timedelta(days=4)).isoformat()
    cursor.execute("""
        INSERT INTO InstructionVersions
        (instruction_id, content, source, created_at, updated_at, customer_confirmation_status,
         successful_delivery_assoc, failed_delivery_assoc, reliability_score)
        VALUES (?, 'White house behind the post office, blue gate', 'agent', ?, ?, 'PENDING', 0, 1, 'LOW')
    """, (loc4_inst_id, loc4_ts, loc4_ts))

    for attempt in [1, 2]:
        cursor.execute("INSERT INTO Deliveries (location_id, customer_id, agent_id, status, attempt_number) VALUES (4, 4, ?, 'FAILED', ?)", (agent_id, attempt))
        del_id = cursor.lastrowid
        # Reason 3 = Customer unavailable, Reason 1 = Locked gate
        cursor.execute("INSERT INTO DeliveryOutcomes (delivery_id, location_id, attempt_number, outcome, failure_reason_id, optional_note, timestamp, instructions_available) VALUES (?, 4, ?, 'FAILURE', ?, 'No one home', ?, 1)", (del_id, attempt, 1 if attempt==1 else 3, (now - timedelta(days=5-attempt)).isoformat()))
        cursor.execute("""
            INSERT INTO InstructionUsageLogs (delivery_id, instruction_id, was_displayed, was_reused, was_verified, assoc_with_success, assoc_with_fail)
            VALUES (?, ?, 1, 1, 0, 0, 1)
        """, (del_id, loc4_inst_id))
        
    # Location 5: Customer-confirmed
    cursor.execute("INSERT INTO AccessInstructions (location_id, current_content, confidence_score, active_status) VALUES (5, 'House next to school with green gate', 'HIGH', 1)")
    inst_id = cursor.lastrowid
    cursor.execute("INSERT INTO InstructionVersions (instruction_id, content, source, created_at, updated_at, customer_confirmation_status, reliability_score) VALUES (?, 'House next to school with green gate', 'customer', ?, ?, 'CONFIRMED', 'HIGH')", (inst_id, (now - timedelta(days=20)).isoformat(), (now - timedelta(days=5)).isoformat()))
    
    # Location 6: Outdated instructions
    cursor.execute("INSERT INTO AccessInstructions (location_id, current_content, confidence_score, active_status) VALUES (6, 'Turn left at old mill', 'LOW', 1)")
    inst_id = cursor.lastrowid
    cursor.execute("INSERT INTO InstructionVersions (instruction_id, content, source, created_at, updated_at, customer_confirmation_status, reliability_score) VALUES (?, 'Turn left at old mill', 'agent', ?, ?, 'PENDING', 'LOW')", (inst_id, (now - timedelta(days=365)).isoformat(), (now - timedelta(days=365)).isoformat()))

    # Location 7: Old successful delivery, never confirmed - the MEDIUM confidence demo example
    cursor.execute("INSERT INTO AccessInstructions (location_id, current_content, confidence_score, active_status) VALUES (7, 'Estate gate on the private road, ring the bell', 'MEDIUM', 1)")
    loc7_inst_id = cursor.lastrowid
    loc7_created = (now - timedelta(days=90)).isoformat()
    loc7_updated = (now - timedelta(days=60)).isoformat()
    cursor.execute("""
        INSERT INTO InstructionVersions
        (instruction_id, content, source, created_at, updated_at, customer_confirmation_status,
         successful_delivery_assoc, failed_delivery_assoc, reliability_score)
        VALUES (?, 'Estate gate on the private road, ring the bell', 'agent', ?, ?, 'PENDING', 1, 0, 'MEDIUM')
    """, (loc7_inst_id, loc7_created, loc7_updated))
    cursor.execute("INSERT INTO Deliveries (location_id, customer_id, agent_id, status, attempt_number) VALUES (7, 2, ?, 'COMPLETED', 1)", (agent_id,))
    del_id = cursor.lastrowid
    cursor.execute("INSERT INTO DeliveryOutcomes (delivery_id, location_id, attempt_number, outcome, optional_note, timestamp, instructions_available) VALUES (?, 7, 1, 'SUCCESS', 'Rang the bell, gate opened', ?, 1)", (del_id, loc7_updated))
    cursor.execute("""
        INSERT INTO InstructionUsageLogs (delivery_id, instruction_id, was_displayed, was_reused, was_verified, assoc_with_success, assoc_with_fail)
        VALUES (?, ?, 1, 1, 0, 1, 0)
    """, (del_id, loc7_inst_id))
    
    # Pending Deliveries for Demo (Current state)
    for loc_id, cust_id in [(1,1), (2,2), (3,3), (4,4), (5,5), (6,1), (7,2)]:
        cursor.execute("INSERT INTO Deliveries (location_id, customer_id, agent_id, status, attempt_number) VALUES (?, ?, ?, 'PENDING', 1)", (loc_id, cust_id, agent_id))

    conn.commit()

if __name__ == "__main__":
    conn = setup_database()
    generate_data(conn)
    print("Database and synthetic dataset successfully generated at:", DB_PATH)
    
    # Validation prints
    cursor = conn.cursor()
    print("\\n--- Validation Summary ---")
    
    cursor.execute("SELECT COUNT(*) FROM Locations")
    print(f"Locations generated: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM Deliveries WHERE status='PENDING'")
    print(f"Pending Deliveries for Demo: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM DeliveryOutcomes WHERE outcome='FAILURE'")
    print(f"Historical Failed Deliveries: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM AccessInstructions")
    print(f"Access Instructions captured: {cursor.fetchone()[0]}")

    print("\n--- Demo Login Credentials ---")
    print("Agent:    agent@example.com    / agent123")
    print("Customer: customer@example.com / customer123")
    print("Admin:    admin@example.com    / admin123")

    conn.close()
