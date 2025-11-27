import React from 'react';
import { X, ShoppingBag, CreditCard, MapPin, CheckCircle } from 'lucide-react';

function CheckoutPage({ cartItems, products, cartSessionId, onClose, onOrderComplete }) {
  const [step, setStep] = React.useState(1);
  const [shippingInfo, setShippingInfo] = React.useState({
    fullName: '',
    email: '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
    country: ''
  });

  const [paymentInfo, setPaymentInfo] = React.useState({
    cardNumber: '',
    cardName: '',
    expiryDate: '',
    cvv: ''
  });

  const [orderPlaced, setOrderPlaced] = React.useState(false);
  const [orderId, setOrderId] = React.useState('');
  const [loading, setLoading] = React.useState(false);

  // Calculate totals
  const productMap = new Map(products.map(p => [p.id, p]));
  const subtotal = cartItems.reduce((total, item) => {
    const product = productMap.get(item.product_id);
    return total + (product ? product.price * item.quantity : 0);
  }, 0);
  const shipping = 9.99;
  const tax = subtotal * 0.1;
  const total = subtotal + shipping + tax;

  const handleShippingChange = (e) => {
    setShippingInfo({ ...shippingInfo, [e.target.name]: e.target.value });
  };

  const handlePaymentChange = (e) => {
    let value = e.target.value;

    if (e.target.name === 'cardNumber') {
      value = value.replace(/\s/g, '').replace(/(\d{4})/g, '$1 ').trim();
    }

    if (e.target.name === 'expiryDate') {
      value = value.replace(/\D/g, '').replace(/(\d{2})(\d{0,2})/, '$1/$2').substr(0, 5);
    }

    setPaymentInfo({ ...paymentInfo, [e.target.name]: value });
  };

  const validateShipping = () => {
    return Object.values(shippingInfo).every(val => val.trim() !== '');
  };

  const validatePayment = () => {
    return paymentInfo.cardNumber.replace(/\s/g, '').length === 16 &&
           paymentInfo.cardName.trim() !== '' &&
           paymentInfo.expiryDate.length === 5 &&
           paymentInfo.cvv.length === 3;
  };

  const handlePlaceOrder = async () => {
    setLoading(true);

    try {
      // Transform cart items to match the Order Service JSON (camelCase)
      const orderItems = cartItems.map(item => {
        const product = productMap.get(item.product_id);
        return {
          productId: String(item.product_id),
          productName: product ? product.name : 'Unknown Product',
          quantity: item.quantity,
          unitPrice: product ? product.price : 0
        };
      });

      const payload = {
        userId: 'user-123', // TODO: Get from auth context when JWT is implemented
        items: orderItems
      };

      console.log('Sending order payload:', payload);

      const response = await fetch('/api/orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const text = await response.text();
      if (!response.ok) {
        console.error('Order failed, status:', response.status, 'body:', text);
        throw new Error('Order failed');
      }

      let data;
      try {
        data = JSON.parse(text);
      } catch {
        data = {};
      }

      console.log('Order success response:', data);

      setOrderId(data.orderId || data.OrderId || 'ORD-' + Date.now());
      setOrderPlaced(true);

      // Call the parent's order complete handler
      setTimeout(() => {
        onOrderComplete();
      }, 3000);

    } catch (error) {
      console.error('Order error:', error);
      alert('Failed to place order. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Order Summary Sidebar
  const OrderSummary = () => (
    <div className="bg-gray-50 p-6 rounded-lg">
      <h3 className="text-xl font-bold mb-4">Order Summary</h3>
      <div className="space-y-3 mb-4">
        {cartItems.map(item => {
          const product = productMap.get(item.product_id);
          if (!product) return null;
          return (
            <div key={item.product_id} className="flex justify-between text-sm">
              <span>{product.name} x {item.quantity}</span>
              <span>€{(product.price * item.quantity).toFixed(2)}</span>
            </div>
          );
        })}
      </div>
      <div className="border-t pt-3 space-y-2">
        <div className="flex justify-between text-sm">
          <span>Subtotal</span>
          <span>€{subtotal.toFixed(2)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>Shipping</span>
          <span>€{shipping.toFixed(2)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>Tax (10%)</span>
          <span>€{tax.toFixed(2)}</span>
        </div>
        <div className="flex justify-between font-bold text-lg border-t pt-2">
          <span>Total</span>
          <span>€{total.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );

  // Success Screen
  if (orderPlaced) {
    return (
      <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Order Placed!</h2>
          <p className="text-gray-600 mb-4">Thank you for your purchase</p>
          <div className="bg-gray-100 p-4 rounded-lg mb-6">
            <p className="text-sm text-gray-600">Order ID</p>
            <p className="text-xl font-bold text-indigo-600">{orderId}</p>
          </div>
          <p className="text-sm text-gray-500">
            A confirmation email has been sent to {shippingInfo.email}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 bg-black bg-opacity-50 overflow-y-auto">
      <div className="min-h-screen p-4 flex items-start justify-center pt-10">
        <div className="bg-white rounded-xl shadow-2xl max-w-6xl w-full">
          {/* Header */}
          <div className="flex justify-between items-center p-6 border-b">
            <h2 className="text-2xl font-bold text-gray-900">Checkout</h2>
            <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full">
              <X size={24} />
            </button>
          </div>

          {/* Progress Steps */}
          <div className="flex justify-center items-center p-6 border-b">
            <div className="flex items-center space-x-4">
              <div className={`flex items-center ${step >= 1 ? 'text-indigo-600' : 'text-gray-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 1 ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}>
                  1
                </div>
                <span className="ml-2 font-semibold">Cart</span>
              </div>
              <div className="w-12 h-0.5 bg-gray-300"></div>
              <div className={`flex items-center ${step >= 2 ? 'text-indigo-600' : 'text-gray-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 2 ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}>
                  2
                </div>
                <span className="ml-2 font-semibold">Shipping</span>
              </div>
              <div className="w-12 h-0.5 bg-gray-300"></div>
              <div className={`flex items-center ${step >= 3 ? 'text-indigo-600' : 'text-gray-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 3 ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}>
                  3
                </div>
                <span className="ml-2 font-semibold">Payment</span>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="grid md:grid-cols-3 gap-6 p-6">
            {/* Main Content */}
            <div className="md:col-span-2">
              {/* Step 1: Cart Review */}
              {step === 1 && (
                <div>
                  <h3 className="text-xl font-bold mb-4 flex items-center">
                    <ShoppingBag className="mr-2" /> Review Your Cart
                  </h3>
                  <div className="space-y-3">
                    {cartItems.map(item => {
                      const product = productMap.get(item.product_id);
                      if (!product) return null;
                      return (
                        <div key={item.product_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                          <div className="flex items-center space-x-4">
                            <img 
                              src={product.image_url || `https://placehold.co/80x80?text=${product.name}`} 
                              alt={product.name}
                              className="w-16 h-16 object-cover rounded"
                            />
                            <div>
                              <p className="font-semibold">{product.name}</p>
                              <p className="text-sm text-gray-600">Qty: {item.quantity}</p>
                            </div>
                          </div>
                          <p className="font-bold">€{(product.price * item.quantity).toFixed(2)}</p>
                        </div>
                      );
                    })}
                  </div>
                  <button
                    onClick={() => setStep(2)}
                    className="w-full mt-6 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition"
                  >
                    Continue to Shipping
                  </button>
                </div>
              )}

              {/* Step 2: Shipping Information */}
              {step === 2 && (
                <div>
                  <h3 className="text-xl font-bold mb-4 flex items-center">
                    <MapPin className="mr-2" /> Shipping Information
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-1">Full Name</label>
                      <input
                        type="text"
                        name="fullName"
                        value={shippingInfo.fullName}
                        onChange={handleShippingChange}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                        placeholder="John Doe"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">Email</label>
                      <input
                        type="email"
                        name="email"
                        value={shippingInfo.email}
                        onChange={handleShippingChange}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                        placeholder="john@example.com"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">Address</label>
                      <input
                        type="text"
                        name="address"
                        value={shippingInfo.address}
                        onChange={handleShippingChange}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                        placeholder="123 Main St"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">City</label>
                        <input
                          type="text"
                          name="city"
                          value={shippingInfo.city}
                          onChange={handleShippingChange}
                          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                          placeholder="New York"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1">State</label>
                        <input
                          type="text"
                          name="state"
                          value={shippingInfo.state}
                          onChange={handleShippingChange}
                          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                          placeholder="NY"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">Zip Code</label>
                        <input
                          type="text"
                          name="zipCode"
                          value={shippingInfo.zipCode}
                          onChange={handleShippingChange}
                          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                          placeholder="10001"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1">Country</label>
                        <input
                          type="text"
                          name="country"
                          value={shippingInfo.country}
                          onChange={handleShippingChange}
                          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                          placeholder="USA"
                        />
                      </div>
                    </div>
                  </div>
                  <div className="flex space-x-4 mt-6">
                    <button
                      onClick={() => setStep(1)}
                      className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-6 rounded-lg transition"
                    >
                      Back
                    </button>
                    <button
                      onClick={() => setStep(3)}
                      disabled={!validateShipping()}
                      className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition disabled:bg-gray-400 disabled:cursor-not-allowed"
                    >
                      Continue to Payment
                    </button>
                  </div>
                </div>
              )}

              {/* Step 3: Payment */}
              {step === 3 && (
                <div>
                  <h3 className="text-xl font-bold mb-4 flex items-center">
                    <CreditCard className="mr-2" /> Payment Information
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-1">Card Number</label>
                      <input
                        type="text"
                        name="cardNumber"
                        value={paymentInfo.cardNumber}
                        onChange={handlePaymentChange}
                        maxLength="19"
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                        placeholder="1234 5678 9012 3456"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">Cardholder Name</label>
                      <input
                        type="text"
                        name="cardName"
                        value={paymentInfo.cardName}
                        onChange={handlePaymentChange}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                        placeholder="John Doe"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">Expiry Date</label>
                        <input
                          type="text"
                          name="expiryDate"
                          value={paymentInfo.expiryDate}
                          onChange={handlePaymentChange}
                          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                          placeholder="MM/YY"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1">CVV</label>
                        <input
                          type="text"
                          name="cvv"
                          value={paymentInfo.cvv}
                          onChange={handlePaymentChange}
                          maxLength="3"
                          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                          placeholder="123"
                        />
                      </div>
                    </div>
                  </div>
                  <div className="flex space-x-4 mt-6">
                    <button
                      onClick={() => setStep(2)}
                      className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-6 rounded-lg transition"
                    >
                      Back
                    </button>
                    <button
                      onClick={handlePlaceOrder}
                      disabled={!validatePayment() || loading}
                      className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition disabled:bg-gray-400 disabled:cursor-not-allowed"
                    >
                      {loading ? 'Processing...' : 'Place Order'}
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Sidebar - Order Summary */}
            <div className="md:col-span-1">
              <OrderSummary />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CheckoutPage;