// frontend/src/App.js
import React, { useEffect, useState } from 'react';
import { ShoppingCart } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid'; // Need a way to generate unique IDs.

const API_BASE_URL = '/api';

function App() {
  // Let's keep track of our app's state
  const [products, setProducts] = useState([]);
  const [cartItems, setCartItems] = useState([]); // This will now hold the actual list of items
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState({ text: '', type: '' });

  // A little helper for our flash messages. It's a bit of a manual process, but it works!
  const showFlashMessage = (text, type = 'success') => {
    setMessage({ text, type });
    setTimeout(() => setMessage({ text: '', type: '' }), 3000);
  };

  // NEW! We'll generate a unique ID for our cart session.
  // We'll store it in localStorage so the cart persists across page reloads.
  const getCartSessionId = () => {
    let sessionId = localStorage.getItem('cartSessionId');
    if (!sessionId) {
      sessionId = uuidv4();
      localStorage.setItem('cartSessionId', sessionId);
    }
    return sessionId;
  };

  const cartSessionId = getCartSessionId();

  // Let's grab the products and the cart items when the component first loads
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setIsLoading(true);

        // First, fetch the products
        const productsResponse = await fetch(`${API_BASE_URL}/products/`);
        if (!productsResponse.ok) {
          throw new Error(`Failed to load products. Check the server!`);
        }
        const productsData = await productsResponse.json();
        setProducts(productsData);

        // NEW! Now, let's grab the cart items for this session
        const cartResponse = await fetch(`${API_BASE_URL}/cart/${cartSessionId}`);
        if (!cartResponse.ok) {
          throw new Error(`Failed to load cart items.`);
        }
        const cartData = await cartResponse.json();
        setCartItems(cartData);

      } catch (e) {
        console.error("Something went wrong with the fetch:", e);
        setError(`Failed to load data: ${e.message}. The backend might be down.`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchInitialData();
  }, []); // The empty array means this runs only once

  // Let's handle adding a product to the cart (the real version!)
  const handleAddToCart = async (product) => {
    try {
      // We'll send a POST request with the product ID and our session ID
      const response = await fetch(`${API_BASE_URL}/cart/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          product_id: product.id, 
          cart_session_id: cartSessionId,
          quantity: 1 // For now, we'll just add one at a time
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Couldn't add ${product.name} to cart.`);
      }

      // Success! Now let's update our local state with the new cart item
      const addedCartItem = await response.json();
      
      // Check if the item is already in our state. If so, just update the quantity.
      setCartItems(prevItems => {
        const existingItemIndex = prevItems.findIndex(item => item.product_id === addedCartItem.product_id);
        if (existingItemIndex > -1) {
          const updatedItems = [...prevItems];
          updatedItems[existingItemIndex].quantity += 1;
          return updatedItems;
        } else {
          // Otherwise, add the new item to the list.
          return [...prevItems, addedCartItem];
        }
      });

      showFlashMessage(`${product.name} added to cart. Nice!`);
    } catch (e) {
      console.error("Oh no, an error:", e);
      showFlashMessage(`Error adding to cart: ${e.message}`, 'error');
    }
  };

  // Now, let's calculate the total count of items in the cart
  const totalCartCount = cartItems.reduce((total, item) => total + item.quantity, 0);

  return (
    <div className="min-h-screen bg-gray-100 font-sans text-gray-800 p-4">
      <header className="bg-white shadow-md rounded-lg p-6 mb-8 flex justify-between items-center">
        <h1 className="text-4xl font-bold text-indigo-700 mb-2">
          Awesome E-Shop
        </h1>
        <div className="relative">
          <ShoppingCart className="w-8 h-8 text-indigo-600 cursor-pointer" />
          {/* Only show the badge if there are items */}
          {totalCartCount > 0 && (
            <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
              {totalCartCount}
            </span>
          )}
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto">
        <h2 className="text-3xl font-semibold text-gray-800 mb-6 text-center">
          What's for sale today?
        </h2>

        {/* Message display area - a bit messy, but it works */}
        {message.text && (
          <div className={`px-4 py-3 rounded relative text-center mb-4 ${
            message.type === 'success' ? 'bg-green-100 border border-green-400 text-green-700' :
            'bg-red-100 border border-red-400 text-red-700'
          }`} role="alert">
            <span className="block sm:inline">{message.text}</span>
          </div>
        )}

        {isLoading && (
          <div className="flex justify-center items-center h-48">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-indigo-500"></div>
            <p className="ml-4 text-xl text-indigo-600">Hold on, fetching products...</p>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative text-center" role="alert">
            <strong className="font-bold">Heads up!</strong>
            <span className="block sm:inline"> {error}</span>
          </div>
        )}

        {/* "No products" message */}
        {!isLoading && !error && products.length === 0 && (
          <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded relative text-center" role="alert">
            <strong className="font-bold">Wait, where are the products?</strong>
            <span className="block sm:inline"> Looks like there's nothing here yet.</span>
          </div>
        )}

        {/* The actual product grid */}
        {!isLoading && !error && products.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {products.map(product => (
              <div key={product.id} className="bg-white rounded-xl shadow-lg overflow-hidden transform transition-transform duration-300 hover:scale-105 hover:shadow-xl">
                <img
                  src={product.image_url || `https://placehold.co/400x300/e0e0e0/333333?text=${encodeURIComponent(product.name)}`}
                  alt={product.name}
                  className="w-full h-48 object-cover"
                  onError={(e) => { e.target.onerror = null; e.target.src="https://placehold.co/400x300/e0e0e0/333333?text=Image+Not+Found"; }}
                />
                <div className="p-5">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{product.name}</h3>
                  <p className="text-gray-600 text-sm mb-3 line-clamp-2">{product.description || 'No description provided.'}</p>
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-2xl font-extrabold text-indigo-600">€{product.price.toFixed(2)}</span>
                    <span className="text-sm text-gray-500">Only {product.stock_quantity} left!</span>
                  </div>
                  <button
                    onClick={() => handleAddToCart(product)}
                    className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition duration-300 ease-in-out transform hover:scale-105 shadow-md"
                  >
                    Add to Cart
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      <footer className="text-center text-gray-500 mt-12 p-4">
        &copy; {new Date().getFullYear()} Awesome E-Shop.
      </footer>
    </div>
  );
}

export default App;
