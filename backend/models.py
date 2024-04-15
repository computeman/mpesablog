from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from datetime import datetime

db = SQLAlchemy()


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    order_items = db.relationship("OrderItem", backref="product", lazy=True)
    cart_items = db.relationship("CartItem", backref="cart_product", lazy=True)

    def __repr__(self):
        return f"Product(name={self.name}, price={self.price})"


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_items = db.relationship("OrderItem", backref="order", lazy=True)
    payment = db.relationship("Payment", backref="order", uselist=False)

    def __repr__(self):
        return f"Order(id={self.id})"


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"OrderItem(order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity})"


class Payment(db.Model):
    __tablename__ = "payment"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    payment_amount = db.Column(db.Float)
    payment_date = db.Column(db.DateTime)
    payment_method = db.Column(db.String)
    status = db.Column(db.String)
    transaction_id = db.Column(db.String)

    @validates("payment_amount")
    def validate_payment_amount(self, key, payment_amount):
        if payment_amount < 0:
            raise ValueError("Payment amount cannot be negative")
        return payment_amount


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="pending")
    cart_items = db.relationship("CartItem", backref="cart", lazy=True)

    def __repr__(self):
        return f"Cart(id={self.id})"


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("cart.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    product = db.relationship(
        "Product", backref=db.backref("cart_items_rel", lazy="dynamic")
    )

    def __repr__(self):
        return f"CartItem(cart_id={self.cart_id}, product_id={self.product_id}, quantity={self.quantity})"
