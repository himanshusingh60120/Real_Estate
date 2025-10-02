import sqlite3

DATABASE = 'real_estate.db'

def setup_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE Users (
        user_id INTEGER PRIMARY KEY,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        user_type VARCHAR(50) NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE Agents (
        agent_id INTEGER PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100),
        phone VARCHAR(20),
        specialization VARCHAR(50),
        years_experience INTEGER
    );
    """)

    cursor.execute("""
    CREATE TABLE Properties (
        property_id INTEGER PRIMARY KEY,
        title VARCHAR(100),
        address VARCHAR(150),
        city VARCHAR(50),
        price INTEGER,
        status VARCHAR(20),
        bedrooms INTEGER,
        bathrooms INTEGER,
        area_sqft INTEGER,
        property_type VARCHAR(50),
        agent_id INTEGER,
        listed_date TEXT,
        owner_user_id INTEGER,
        FOREIGN KEY (agent_id) REFERENCES Agents(agent_id),
        FOREIGN KEY (owner_user_id) REFERENCES Users(user_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE Rentals (
        rental_id INTEGER PRIMARY KEY,
        property_id INTEGER,
        tenant_name VARCHAR(100),
        tenant_phone VARCHAR(20),
        start_date TEXT,
        end_date TEXT,
        monthly_rent REAL,
        security_deposit REAL,
        FOREIGN KEY (property_id) REFERENCES Properties(property_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE MaintenanceRequests (
        request_id INTEGER PRIMARY KEY,
        rental_id INTEGER,
        request_date TEXT,
        issue_description TEXT,
        status VARCHAR(50),
        FOREIGN KEY (rental_id) REFERENCES Rentals(rental_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE Potential_Tenants (
        tenant_id INTEGER PRIMARY KEY,
        name VARCHAR(100),
        phone VARCHAR(15),
        budget INTEGER,
        preferred_location VARCHAR(100),
        room_type VARCHAR(20)
    );
    """)

    cursor.execute("""
    CREATE TABLE Property_Likes (
        like_id INTEGER PRIMARY KEY,
        property_id INTEGER,
        tenant_user_id INTEGER,
        FOREIGN KEY (property_id) REFERENCES Properties(property_id),
        FOREIGN KEY (tenant_user_id) REFERENCES Users(user_id),
        UNIQUE (property_id, tenant_user_id)
    );
    """)

    # Insert data
    # Note: For simplicity, we are not using Bcrypt for this setup script.
    cursor.execute("INSERT INTO Users (user_id, email, password_hash, user_type) VALUES (1, 'owner1@example.com', 'hashed_password_1', 'owner');")
    cursor.execute("INSERT INTO Users (user_id, email, password_hash, user_type) VALUES (2, 'tenant1@example.com', 'hashed_password_2', 'tenant');")
    cursor.execute("INSERT INTO Users (user_id, email, password_hash, user_type) VALUES (3, 'owner2@example.com', 'hashed_password_3', 'owner');")
    cursor.execute("INSERT INTO Users (user_id, email, password_hash, user_type) VALUES (4, 'tenant2@example.com', 'hashed_password_4', 'tenant');")
    cursor.execute("INSERT INTO Agents (agent_id, name, email, phone, specialization, years_experience) VALUES (1, 'Ricky Singh', 'ricky72@example.com', '9556441870', 'Residential', 5);")
    cursor.execute("INSERT INTO Properties (property_id, title, address, city, price, status, bedrooms, bathrooms, area_sqft, property_type, agent_id, listed_date, owner_user_id) VALUES (101, '2BHK Apartment in Pune', '12 MG Road', 'Pune', 7500000, 'Available', 2, 2, 1200, 'Apartment', 1, '2023-12-15', 1);")
    cursor.execute("INSERT INTO Rentals (rental_id, property_id, tenant_name, tenant_phone, start_date, end_date, monthly_rent, security_deposit) VALUES (401, 103, 'Sunil Mehta', '9876543211', '2024-01-01', '2024-12-31', 35000.00, 105000.00);")
    cursor.execute("INSERT INTO MaintenanceRequests (rental_id, request_date, issue_description, status) VALUES (401, '2024-04-10', 'Leaking bathroom faucet', 'Pending');")
    cursor.execute("INSERT INTO Potential_Tenants (tenant_id, name, phone, budget, preferred_location, room_type) VALUES (1, 'Rahul Deshmukh', '9876543210', 8000, 'Pune - Wakad', 'Shared');")
    cursor.execute("INSERT INTO Property_Likes (property_id, tenant_user_id) VALUES (101, 2);")

    conn.commit()
    conn.close()
    print("Database setup complete.")

if __name__ == '__main__':
    setup_database()