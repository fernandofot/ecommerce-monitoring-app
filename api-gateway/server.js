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
const PRODUCT_CATALOG_URL = process.env.PRODUCT_CATALOG_URL || 'http://product_catalog_app:8000';

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

// --- Consolidated API Proxy ---
// This is the core of our gateway. We're setting up a single middleware to
// handle all requests that start with '/api'.
// The pathRewrite now correctly removes the '/api' prefix from all requests
// before they are forwarded to the backend service. This is a more general
// and robust solution than specifying each path individually.
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
