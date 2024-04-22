import React, { useState, useEffect } from "react";

function ProductList() {
  const [products, setProducts] = useState([]);
  const [cartId, setCartId] = useState(null);
  const [cartItems, setCartItems] = useState([]);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [paymentStatus, setPaymentStatus] = useState("pending");

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

    // Fetch the token
    fetch("http://127.0.0.1:5000/get_token")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch access token");
        }
        return response.json();
      })
      .then((data) => {
        const accessToken = data.access_token;

        // Send trigger request with the obtained access tokend
        fetch("http://127.0.0.1:5000/trigger", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            phone_number: phoneNumber,
            cart_id: cartId,
            access_token: accessToken, // Send the access token as a parameter
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
            // startPollingPaymentStatus();
          })
          .catch((error) => {
            console.error("Error initiating payment:", error);
            alert("Failed to initiate payment");
          });
      })
      .catch((error) => {
        console.error("Error fetching access token:", error);
        alert("Failed to fetch access token");
      });
  };
  const startPollingPaymentStatus = () => {
    const interval = setInterval(() => {
      fetch(`http://127.0.0.1:5000/poll_cart_status/${cartId}`)
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "paid") {
            setPaymentStatus("paid");
            clearInterval(interval);
          } else if (data.status === "failed") {
            setPaymentStatus("failed");
            clearInterval(interval);
          }
        })
        .catch((err) => {
          console.error("Error checking payment status:", err);
          setPaymentStatus("error");
          clearInterval(interval);
        });
    }, 5000);
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
        <button
          onClick={() => {
            handleCheckout();
            startPollingPaymentStatus();
          }}
        >
          Checkout
        </button>
      </div>
      {paymentStatus === "paid" && (
        <div>
          <h2>Payment Successful!</h2>
          {/* <div>Order ID: {orderData.order_id}</div>
          <div>Transaction ID: {orderData.transaction_id}</div> */}
        </div>
      )}
      {paymentStatus === "failed" && (
        <div>
          <h2>Payment Failed</h2>
        </div>
      )}
      {paymentStatus === "error" && (
        <div>
          <h2>Error checking payment status</h2>
        </div>
      )}
    </div>
  );
}

export default ProductList;
