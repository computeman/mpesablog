from app import app, db
from models import Product, Order, OrderItem, Payment, CartItem, Cart
from datetime import datetime, date

with app.app_context():
    # Create some products
    product1 = Product(name="Product 1", description="This is product 1", price=9.99)
    product2 = Product(name="Product 2", description="This is product 2", price=19.99)
    product3 = Product(name="Product 3", description="This is product 3", price=29.99)

    # Create a cart
    cart = Cart(created_at=datetime.utcnow())

    # Create cart items
    cart_item1 = CartItem(cart=cart, product=product1, quantity=2)
    cart_item2 = CartItem(cart=cart, product=product2, quantity=1)

    # Create an order
    order = Order()

    # Create order items
    order_item1 = OrderItem(order=order, product=product1, quantity=3)
    order_item2 = OrderItem(order=order, product=product3, quantity=1)

    # Create a payment
    payment = Payment(
        order=order,
        payment_amount=100,
        payment_date=datetime.utcnow(),
        payment_method="Credit Card",
        status="Paid",
        transaction_id="12345",
    )

    # Add objects to the session
    db.session.add(product1)
    db.session.add(product2)
    db.session.add(product3)
    db.session.add(cart)
    db.session.add(cart_item1)
    db.session.add(cart_item2)
    db.session.add(order)
    db.session.add(order_item1)
    db.session.add(order_item2)
    db.session.add(payment)
    # Commit the changes
    db.session.commit()

    print("Seed data created successfully!")
