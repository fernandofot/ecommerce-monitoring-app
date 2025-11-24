/**
 * @fileoverview A simple, yet powerful, API Gateway server using Express.
 * This server's job is to act as a reverse proxy, directing incoming
 * requests to the right backend services and cleaning up the paths along the way.
 */

// Let's bring in the tools we'll need.
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

// Create our Express app and set the port.
const app = express();
const PORT = process.env.PORT || 3000;

// =========================================================================
// Setting up our backend services
// =========================================================================
// Our backend URLs are pulled from environment variables.
// These are usually set up for us automatically by Docker Compose.
// The service names are what we use to talk to them within the Docker network.
const PRODUCT_CATALOG_URL = process.env.PRODUCT_CATALOG_URL || 'http://product-catalog-service:8000';
// NEW: We've added the URL for our new user and authentication service.
const USER_AUTH_URL = process.env.USER_AUTH_URL || 'http://user-service:8080';
// NEW: We've added the URL for our new order processing service.
const ORDER_SERVICE_URL = process.env.ORDER_SERVICE_URL || 'http://order-service:8082';

// =========================================================================
// API Gateway Routing and Proxying
// =========================================================================
// A little helper function to log every request that comes through our gateway.
// This is super helpful for debugging!
app.use((req, res, next) => {
    console.log(`[API Gateway] Received a request: ${req.method} ${req.originalUrl}`);
    next();
});

// --- API Health Check ---
// We've got to respond to the root path so Docker knows we're alive and well.
// This is a simple health check endpoint.
app.get('/', (req, res) => {
    res.send('API Gateway is running!');
});

// --- User & Authentication API Proxy ---
// This middleware specifically handles requests for the user service.
// It's important to place this before the more general /api route below,
// so requests to /api/auth get handled correctly.
app.use('/api/auth', createProxyMiddleware({
  target: USER_AUTH_URL,
  changeOrigin: true,
  // pathRewrite is not needed here as the path on the gateway matches
  // the path on the backend service.
}));

// --- NEW: Order Processing API Proxy ---
// This middleware handles requests for the new order service.
app.use('/api/orders', (req, res, next) => {
  console.log('[API Gateway] Proxying to Order Service:', {
    method: req.method,
    originalUrl: req.originalUrl
  });
  next();
}, createProxyMiddleware({
  target: ORDER_SERVICE_URL, // 'http://order-service:8082'
  changeOrigin: true,
  pathRewrite: {
    '^/api/orders$': '/orders',   // exact /api/orders
    '^/api/orders/': '/orders/'   // /api/orders/... 
  }
}));

// --- Product Catalog API Proxy ---
// This proxy handles all other requests that start with '/api' and
// forwards them to the Product Catalog Service.
app.use('/api', createProxyMiddleware({
  target: PRODUCT_CATALOG_URL,
  changeOrigin: true, // This is a good practice for virtual hosting.
  pathRewrite: {
    '^/api/': '/' // This regex-based rewrite removes '/api/' from the start of the path.
  }
}));

// =========================================================================
// Server Initialization
// =========================================================================
// And finally, let's fire up the server!
app.listen(PORT, () => {
  console.log(`[API Gateway] Server is listening on port ${PORT}`);
});
