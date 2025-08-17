// Filename: server.js
// This file contains the code for the API Gateway microservice.

const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

// Create an Express application
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware to log incoming requests
app.use((req, res, next) => {
    console.log(`[API Gateway] Received request: ${req.method} ${req.originalUrl}`);
    next();
});

// Define the proxy middleware for the Product Catalog Service
// All requests to /api/products will be forwarded to the product_catalog_app service
const productCatalogProxy = createProxyMiddleware({
    target: 'http://product_catalog_app:8000', // Docker service name and port
    changeOrigin: true, // Needed for virtual hosts
    pathRewrite: {
        '^/api/products': '/', // Rewrite the URL: /api/products/items becomes /items
    },
    onProxyReq: (proxyReq, req, res) => {
        console.log(`[API Gateway] Proxying request to Product Catalog: ${proxyReq.path}`);
    },
});

// Use the proxy middleware for the specific route
app.use('/api/products', productCatalogProxy);

// Basic root route for testing the gateway
app.get('/', (req, res) => {
    res.send('API Gateway is running!');
});

// Start the server
app.listen(PORT, () => {
    console.log(`[API Gateway] Server is listening on port ${PORT}`);
});
