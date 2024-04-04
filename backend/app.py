from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime
from models import db, Product, Order, Payment, CartItem, OrderItem, Cart

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shop.db"
CORS(app)
db.init_app(app)
migrate = Migrate(app, db)


@app.route("/trigger", methods=["POST"])
def trigger_request():
    data = request.get_json()
    cart_id = data.get("cart_id")
    phone_number = data.get("phone_number")
    callBackURL = f"https://public-phones-clean.loca.lt/callback/{cart_id}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer Ng9KCUo88DaBeynGGHP5DCENMBQr",
    }

    payload = {
        "BusinessShortCode": 174379,
        "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjQwMzI2MDAwMzU2",
        "Timestamp": "20240326000356",
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 1,
        "PartyA": phone_number,
        "PartyB": 174379,
        "PhoneNumber": phone_number,
        "CallBackURL": callBackURL,
        "AccountReference": "CompanyXLTD",
        "TransactionDesc": "Payment of X",
    }
    response = requests.request(
        "POST",
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        headers=headers,
        json=payload,
    )
    return response.text.encode("utf8")


# def create_order_from_cart(cart):
#     # Create an order instance
#     order = Order()

#     # Copy cart items to the order items
#     for cart_item in cart.cart_items:
#         order_item = OrderItem(
#             product_id=cart_item.product_id, quantity=cart_item.quantity
#         )
#         order.order_items.append(order_item)

#     # Add the order to the database session and commit
#     db.session.add(order)
#     db.session.commit()


#     return order

def create_order_from_cart(cart):
    if not cart:
        return jsonify({"error": "Cart not found"}), 404

    # Create an order using the cart items
    order = Order()
    db.session.add(order)
    db.session.flush()  # Flush to get the order ID before adding order items

    for cart_item in cart.cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
        )
        db.session.add(order_item)

    # Commit changes to the database
    db.session.commit()

    return order


@app.route("/callback/<int:cart_id>", methods=["POST"])
def callback_handler(cart_id):
    data = request.get_json()

    # Debugging: Print received data
    print("Received data:", data)

    # Extract the relevant data from the callback
    items = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]
    extracted_data = {item["Name"]: item.get("Value", None) for item in items}

    # Debugging: Print extracted data
    print("Extracted data:", extracted_data)

    mpesa_receipt_number = extracted_data.get("MpesaReceiptNumber")
    payment_amount = extracted_data.get("Amount")
    transaction_date = extracted_data.get("TransactionDate")

    # Debugging: Print extracted payment details
    print("Mpesa Receipt Number:", mpesa_receipt_number)
    print("Payment Amount:", payment_amount)
    print("Transaction Date:", transaction_date)

    # # Find the cart associated with the cart_id
    # cart = Cart.query.get(cart_id)
    # if not cart:
    #     return jsonify({"error": "Cart not found"}), 404

    # # Create an order using the cart items
    # order = create_order_from_cart(cart)

    # # Debugging: Print created order details
    # print("Created Order:", order)

    # # Create a new Payment record associated with the order
    # payment = Payment(
    #     order=order,
    #     payment_amount=payment_amount,
    #     payment_date=transaction_date,
    #     payment_method="mpesa",
    #     status="paid",
    #     transaction_id=mpesa_receipt_number,
    # )

    # # Debugging: Print created payment details
    # print("Created Payment:", payment)

    # # Add the payment to the database
    # db.session.add(payment)
    # db.session.commit()

    return jsonify({"success": True})


@app.route("/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    product_list = []
    for product in products:
        product_data = {"id": product.id, "name": product.name, "price": product.price}
        product_list.append(product_data)
    return jsonify(product_list)


# Route to get cart items
@app.route("/cart", methods=["GET"])
def get_cart_items():
    cart_id = request.args.get("cart_id")
    if not cart_id:
        return jsonify({"error": "No cart_id provided"}), 400

    cart = Cart.query.get(cart_id)
    if not cart:
        return jsonify({"error": "Cart not found"}), 404

    cart_items = CartItem.query.filter_by(cart_id=cart_id).all()

    # Convert cart items to a list of dictionaries for easy JSON response
    cart_data = [
        {
            "id": item.id,
            "product": {
                "id": item.product.id,
                "name": item.product.name,
                "price": item.product.price,
            },
            "quantity": item.quantity,
        }
        for item in cart_items
    ]

    return jsonify(cart_data)


@app.route("/current_cart", methods=["GET"])
def get_current_cart():
    current_cart = Cart.query.order_by(Cart.id.desc()).first()
    if not current_cart:
        return jsonify({"error": "No current cart found"}), 404

    return jsonify({"cart_id": current_cart.id})


# Route to add items to the cart
@app.route("/cart", methods=["POST"])
def add_to_cart():
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Get the current cart or create a new one if it doesn't exist
    current_cart = Cart.query.order_by(Cart.id.desc()).first()
    if not current_cart:
        current_cart = Cart()
        db.session.add(current_cart)
        db.session.commit()

    # Check if an item already exists in the cart
    existing_item = CartItem.query.filter_by(
        cart_id=current_cart.id, product_id=product_id
    ).first()
    if existing_item:
        existing_item.quantity += quantity
    else:
        cart_item = CartItem(
            cart=current_cart, product_id=product_id, quantity=quantity
        )
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({"message": "Item added to cart"})


# Route to remove an item from the cart
@app.route("/cart/<int:cart_item_id>", methods=["DELETE"])
def remove_from_cart(cart_item_id):
    cart_item = CartItem.query.get(cart_item_id)
    if not cart_item:
        return jsonify({"error": "Cart item not found"}), 404

    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({"message": "Item removed from cart"})


@app.route("/orders", methods=["GET"])
def get_orders():
    orders = Order.query.all()
    orders_list = []
    for order in orders:
        order_data = {
            "id": order.id,
            "order_items": [
                {"product_id": item.product_id, "quantity": item.quantity}
                for item in order.order_items
            ],
            "payment": (
                {
                    "payment_amount": order.payment.payment_amount,
                    "payment_date": order.payment.payment_date.strftime("%Y-%m-%d"),
                    "payment_method": order.payment.payment_method,
                    "status": order.payment.status,
                    "transaction_id": order.payment.transaction_id,
                }
                if order.payment
                else None
            ),
        }
        orders_list.append(order_data)

    return jsonify({"orders": orders_list})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
