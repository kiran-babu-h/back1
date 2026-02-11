from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)
@app.route("/")
def home():
    return "QR Food Backend is running"



# TEMP STORAGE (later you can use DB)
orders = []

# =====================
# CUSTOMER PLACE ORDER
# =====================
@app.route("/api/order", methods=["POST"])
def place_order():
    data = request.json

    order = {
        "id": str(uuid.uuid4()),
        "table_no": data["table_no"],
        "customer_name": data["customer_name"],
        "items": data["items"],   # ["Dosa (2)", "Tea (1)"]
        "total": data["total"],
        "status": "Pending"
    }

    orders.append(order)
    return jsonify({"message": "Order placed successfully"})

# =====================
# ADMIN: GET ALL ORDERS
# =====================
@app.route("/api/admin/orders")
def get_orders():
    return jsonify(orders)

# =====================
# ADMIN: UPDATE STATUS
# =====================
@app.route("/api/admin/order/<id>/status", methods=["POST"])
def update_status(id):
    status = request.json["status"]
    for o in orders:
        if o["id"] == id:
            o["status"] = status
            break
    return jsonify({"message": "Status updated"})

# =====================
# ADMIN: REMOVE ORDER
# =====================
@app.route("/api/admin/order/<id>/remove", methods=["DELETE"])
def remove_order(id):
    global orders
    orders = [o for o in orders if o["id"] != id]
    return jsonify({"message": "Order removed"})

# =====================
if __name__ == "__main__":
    app.run(debug=True)




