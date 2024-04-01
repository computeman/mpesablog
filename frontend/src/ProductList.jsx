import React, { useState, useEffect } from "react";

function ProductList() {
  const [products, setProducts] = useState([]);
  const [cartId, setCartId] = useState(null);
  const [cartItems, setCartItems] = useState([]);
  const [phoneNumber, setPhoneNumber] = useState("");

  useEffect(() => {
    // Fetch the current cart ID from the server
    fetch("http://127.0.0.1:5000/current_cart")
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          console.error("Error fetching cart ID:", data.error);
        } else {
          setCartId(data.cart_id);
          // Fetch cart items
          fetchCartItems(data.cart_id);
        }
      })
      .catch((error) => console.error("Error fetching cart ID:", error));

    // Fetch products
    fetchProducts();
  }, []);

  const fetchProducts = () => {
    fetch("http://127.0.0.1:5000/products")
      .then((response) => response.json())
      .then((data) => setProducts(data))
      .catch((error) => console.error("Error fetching products:", error));
  };

  const fetchCartItems = (cartId) => {
    fetch(`http://127.0.0.1:5000/cart?cart_id=${cartId}`)
      .then((response) => response.json())
      .then((data) => setCartItems(data))
      .catch((error) => console.error("Error fetching cart items:", error));
  };

  const addToCart = (productId) => {
    if (!cartId) {
      console.error("Cart ID not found");
      return;
    }

    // Add item to the current cart
    fetch(`http://127.0.0.1:5000/cart`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        product_id: productId,
        quantity: 1, // Default quantity is 1
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          console.error("Error adding to cart:", data.error);
        } else {
          fetchCartItems(cartId); // Refresh cart items
        }
      })
      .catch((error) => console.error("Error adding to cart:", error));
  };

  const handleCheckout = () => {
    if (phoneNumber.trim() === "") {
      alert("Please enter your phone number");
      return;
    }

    if (!cartId) {
      console.error("Cart ID not found");
      return;
    }

    // Send trigger request
    fetch("http://127.0.0.1:5000/trigger", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        phone_number: phoneNumber,
        cart_id: cartId,
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to initiate payment");
        }
        return response.text();
      })
      .then((data) => {
        console.log("Payment initiated:", data);
        alert("Payment initiated successfully");
      })
      .catch((error) => {
        console.error("Error initiating payment:", error);
        alert("Failed to initiate payment");
      });
  };

  const handleRemoveFromCart = (cartItemId) => {
    fetch(`http://127.0.0.1:5000/cart/${cartItemId}`, {
      method: "DELETE",
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          console.error("Error removing from cart:", data.error);
        } else {
          fetchCartItems(cartId); // Refresh cart items
        }
      })
      .catch((error) => console.error("Error removing from cart:", error));
  };

  return (
    <div>
      <h2>Products</h2>
      <ul>
        {products.map((product) => (
          <li key={product.id}>
            <div>{product.name}</div>
            <div>{product.description}</div>
            <div>{product.price}</div>
            <button
              onClick={() => addToCart(product.id)}
              style={{ backgroundColor: "green" }}
            >
              Add to Cart
            </button>
          </li>
        ))}
      </ul>

      <h2>Cart Items</h2>
      <ul>
        {cartItems.map((item) => (
          <li key={item.id}>
            <div>
              {item.product.name} (Quantity: {item.quantity})
            </div>
            <button
              onClick={() => handleRemoveFromCart(item.id)}
              style={{ backgroundColor: "red" }}
            >
              Remove
            </button>
          </li>
        ))}
      </ul>

      <div>
        <input
          type="text"
          placeholder="Enter Phone Number"
          value={phoneNumber}
          onChange={(e) => setPhoneNumber(e.target.value)}
        />
        <button onClick={handleCheckout}>Checkout</button>
      </div>
    </div>
  );
}

export default ProductList;
