// frontend/src/App.js
import React, { useEffect, useState } from 'react';
// Import lucide-react for icons
import { ShoppingCart } from 'lucide-react'; // Make sure lucide-react is available, if not, use inline SVG or emoji

function App() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cartCount, setCartCount] = useState(0); // New state for cart count
  const [message, setMessage] = useState({ text: '', type: '' }); // For success/error messages

  const API_BASE_URL = '/api';

  // Function to display temporary messages
  const showMessage = (text, type = 'success') => {
    setMessage({ text, type });
    setTimeout(() => setMessage({ text: '', type: '' }), 3000); // Message disappears after 3 seconds
  };

  // Function to handle adding product to cart
  const handleAddToCart = async (productId, productName) => {
    try {
      // Send POST request to backend to "add" item to cart
      const response = await fetch(`${API_BASE_URL}/cart/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ product_id: productId }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to add ${productName} to cart.`);
      }

      // If successful, update local cart count and show message
      setCartCount(prevCount => prevCount + 1);
      showMessage(`${productName} added to cart!`, 'success');

    } catch (e) {
      console.error("Error adding to cart:", e);
      showMessage(`Error adding ${productName} to cart: ${e.message}`, 'error');
    }
  };

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_BASE_URL}/products/`);
        if (!response.ok) {
          const errorText = await response.text();
          console.error(`HTTP error! status: ${response.status}, body: ${errorText}`);
          throw new Error(`Failed to fetch products: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        setProducts(data);
      } catch (e) {
        console.error("Failed to fetch products:", e);
        setError(`Failed to load products: ${e.message}. Please ensure the backend service is running and accessible.`);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 font-sans text-gray-800 p-4">
      <header className="bg-white shadow-md rounded-lg p-6 mb-8 flex justify-between items-center">
        <h1 className="text-4xl font-bold text-indigo-700 mb-2">
          E-commerce Store
        </h1>
        <div className="relative">
          <ShoppingCart className="w-8 h-8 text-indigo-600 cursor-pointer" />
          {cartCount > 0 && (
            <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
              {cartCount}
            </span>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto">
        <h2 className="text-3xl font-semibold text-gray-800 mb-6 text-center">Our Products</h2>

        {/* Message display area */}
        {message.text && (
          <div className={`px-4 py-3 rounded relative text-center mb-4 ${
            message.type === 'success' ? 'bg-green-100 border border-green-400 text-green-700' :
            'bg-red-100 border border-red-400 text-red-700'
          }`} role="alert">
            <span className="block sm:inline">{message.text}</span>
          </div>
        )}

        {loading && (
          <div className="flex justify-center items-center h-48">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-indigo-500"></div>
            <p className="ml-4 text-xl text-indigo-600">Loading products...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative text-center" role="alert">
            <strong className="font-bold">Error!</strong>
            <span className="block sm:inline"> {error}</span>
          </div>
        )}

        {!loading && !error && products.length === 0 && (
          <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded relative text-center" role="alert">
            <strong className="font-bold">No Products Found!</strong>
            <span className="block sm:inline"> Please add some products via the backend API.</span>
          </div>
        )}

        {!loading && !error && products.length > 0 && (
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
                  <p className="text-gray-600 text-sm mb-3 line-clamp-2">{product.description || 'No description available.'}</p>
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-2xl font-extrabold text-indigo-600">€{product.price.toFixed(2)}</span>
                    <span className="text-sm text-gray-500">Stock: {product.stock_quantity}</span>
                  </div>
                  <button
                    onClick={() => handleAddToCart(product.id, product.name)}
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
        &copy; {new Date().getFullYear()} E-commerce Store. All rights reserved.
      </footer>
    </div>
  );
}

export default App;
