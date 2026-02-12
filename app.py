from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import datetime
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            table_no INTEGER,
            customer_name TEXT,
            items TEXT[],
            total NUMERIC,
            status TEXT,
            created_at TIMESTAMP WITH TIME ZONE
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Initialize DB when app starts
if DATABASE_URL:
    init_db()

@app.route("/")
def home():
    return "QR Food Backend is running with PostgreSQL"

# =====================
# CUSTOMER PLACE ORDER
# =====================
@app.route("/api/order", methods=["POST"])
def place_order():
    data = request.json
    order_id = str(uuid.uuid4())
    table_no = data["table_no"]
    customer_name = data["customer_name"]
    items = data["items"]
    total = data["total"]
    status = "Pending"
    created_at = datetime.datetime.now(datetime.timezone.utc)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (id, table_no, customer_name, items, total, status, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (order_id, table_no, customer_name, items, total, status, created_at)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Order placed successfully", "order_id": order_id})

# =====================
# CUSTOMER: CHECK STATUS
# =====================
@app.route("/api/order/<id>/status")
def get_order_status(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT status FROM orders WHERE id = %s", (id,))
    order = cur.fetchone()
    cur.close()
    conn.close()

    if order:
        return jsonify({"status": order["status"]})
    return jsonify({"error": "Order not found"}), 404

import decimal

# =====================
# ADMIN: GET ALL ORDERS
# =====================
@app.route("/api/admin/orders")
def get_orders():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM orders ORDER BY created_at DESC")
    orders = cur.fetchall()
    cur.close()
    conn.close()
    
    # Format for frontend if needed (datetime and decimal objects to serializable types)
    for o in orders:
        if isinstance(o['created_at'], datetime.datetime):
            o['created_at'] = o['created_at'].isoformat()
        if isinstance(o['total'], decimal.Decimal):
            o['total'] = float(o['total'])

    return jsonify(orders)


# =====================
# ADMIN: UPDATE STATUS
# =====================
@app.route("/api/admin/order/<id>/status", methods=["POST"])
def update_status(id):
    status = request.json["status"]
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = %s WHERE id = %s", (status, id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Status updated"})

# =====================
# ADMIN: REMOVE ORDER
# =====================
@app.route("/api/admin/order/<id>/remove", methods=["DELETE"])
def remove_order(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM orders WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Order removed"})

# =====================
if __name__ == "__main__":
    app.run(debug=True)




