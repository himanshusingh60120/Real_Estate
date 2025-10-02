from flask import Flask, jsonify, request
import mysql.connector
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

# --- Database Configuration ---
# Your credentials are now hardcoded here
db_config = {
    'host': 'localhost',
    'user': 'root', 
    'password': 'kings@123',
    'database': 'project'
}

# --- Database Connection Function ---
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# --- API Routes ---

@app.route('/')
def home():
    return "Welcome to the Real Estate Project API!"

@app.route('/properties', methods=['GET'])
def get_properties():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM Properties WHERE status = 'Available';"
    cursor.execute(query)
    properties = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(properties)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user_type = data.get('user_type')

    if not all([email, password, user_type]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    
    # Hash the password before storing it
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    try:
        query = "INSERT INTO Users (email, password_hash, user_type) VALUES (%s, %s, %s);"
        cursor.execute(query, (email, hashed_password, user_type))
        conn.commit()
        
        return jsonify({"message": "User created successfully"}), 201
    except mysql.connector.IntegrityError as err:
        if "Duplicate entry" in str(err):
            return jsonify({"error": "User with this email already exists"}), 409
        else:
            return jsonify({"error": "An error occurred"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor(dictionary=True)

    query = "SELECT user_id, email, password_hash, user_type FROM Users WHERE email = %s;"
    cursor.execute(query, (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    if bcrypt.check_password_hash(user['password_hash'], password):
        return jsonify({
            "message": "Login successful",
            "user_id": user['user_id'],
            "email": user['email'],
            "user_type": user['user_type']
        }), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401
    
@app.route('/add_property', methods=['POST'])
def add_property():
    data = request.json
    required_fields = ['title', 'address', 'city', 'price', 'status', 'bedrooms', 'bathrooms', 'area_sqft', 'property_type', 'agent_id', 'listed_date', 'owner_user_id']

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing one or more required fields"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    
    try:
        query = """
            INSERT INTO Properties (title, address, city, price, status, bedrooms, bathrooms, area_sqft, property_type, agent_id, listed_date, owner_user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        values = (
            data['title'],
            data['address'],
            data['city'],
            data['price'],
            data['status'],
            data['bedrooms'],
            data['bathrooms'],
            data['area_sqft'],
            data['property_type'],
            data['agent_id'],
            data['listed_date'],
            data['owner_user_id']
        )
        cursor.execute(query, values)
        conn.commit()
        
        return jsonify({"message": "Property added successfully"}), 201
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"error": "An error occurred while adding the property"}), 500
    
    finally:
        cursor.close()
        conn.close()

@app.route('/owner_dashboard/<int:user_id>', methods=['GET'])
def owner_dashboard(user_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        p.property_id,
        p.title AS property_title,
        p.price AS property_price,
        r.monthly_rent,
        (r.monthly_rent * 12) AS annual_rent,
        ROUND((r.monthly_rent * 12 / p.price) * 100, 2) AS rental_yield_percent,
        p.price / (r.monthly_rent * 12) AS years_to_cover_price
    FROM Properties as p
    JOIN Rentals as r 
        ON p.property_id = r.property_id
    WHERE p.owner_user_id = %s;
    """
    
    try:
        cursor.execute(query, (user_id,))
        properties = cursor.fetchall()
        
        if not properties:
            return jsonify({"message": "No properties found for this owner."}), 404
            
        return jsonify(properties)
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"error": "An error occurred while fetching properties"}), 500
    
    finally:
        cursor.close()
        conn.close()


@app.route('/like_property', methods=['POST'])
def like_property():
    data = request.json
    property_id = data.get('property_id')
    tenant_user_id = data.get('tenant_user_id')

    if not all([property_id, tenant_user_id]):
        return jsonify({"error": "Missing property_id or tenant_user_id"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()

    try:
        query = "INSERT INTO Property_Likes (property_id, tenant_user_id) VALUES (%s, %s);"
        cursor.execute(query, (property_id, tenant_user_id))
        conn.commit()
        
        return jsonify({"message": "Property liked successfully"}), 201
    
    except mysql.connector.IntegrityError as err:
        if "Duplicate entry" in str(err):
            return jsonify({"error": "You have already liked this property"}), 409
        else:
            return jsonify({"error": "An error occurred"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/get_likes/<int:property_id>', methods=['GET'])
def get_property_likes(property_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        u.email,
        pt.name,
        pt.phone
    FROM Property_Likes AS pl
    JOIN Users AS u ON pl.tenant_user_id = u.user_id
    JOIN Potential_Tenants AS pt ON pl.tenant_user_id = pt.tenant_id
    WHERE pl.property_id = %s;
    """
    
    try:
        cursor.execute(query, (property_id,))
        likers = cursor.fetchall()
        
        if not likers:
            return jsonify({"message": "No one has liked this property yet."}), 404
        
        total_likes = len(likers)
        
        return jsonify({
            "total_likes": total_likes,
            "interested_tenants": likers
        })
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"error": "An error occurred while fetching likes"}), 500
    
    finally:
        cursor.close()
        conn.close()


@app.route('/tenant_dashboard/<int:user_id>', methods=['GET'])
def tenant_dashboard(user_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        query = "SELECT property_id FROM Property_Likes WHERE tenant_user_id = %s;"
        cursor.execute(query, (user_id,))
        liked_properties_data = cursor.fetchall()
        
        if not liked_properties_data:
            return jsonify({"message": "You haven't liked any properties yet."}), 404

        liked_properties_list = []
        for row in liked_properties_data:
            property_id = row['property_id']
            
            property_query = "SELECT title, address, bedrooms, bathrooms FROM Properties WHERE property_id = %s;"
            cursor.execute(property_query, (property_id,))
            property_details = cursor.fetchone()

            if property_details:
                likes_query = """
                SELECT 
                    u.email,
                    pt.name,
                    pt.phone
                FROM Property_Likes AS pl
                JOIN Users AS u ON pl.tenant_user_id = u.user_id
                JOIN Potential_Tenants AS pt ON pl.tenant_user_id = pt.tenant_id
                WHERE pl.property_id = %s;
                """
                cursor.execute(likes_query, (property_id,))
                interested_tenants = cursor.fetchall()
                
                property_details['interested_tenants'] = interested_tenants
                property_details['total_likes'] = len(interested_tenants)
                liked_properties_list.append(property_details)
        
        return jsonify(liked_properties_list)
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"error": "An error occurred while fetching dashboard data"}), 500
    
    finally:
        cursor.close()
        conn.close()

# --- Run the application ---
if __name__ == '__main__':
    app.run(debug=True)