//  api-gateway/server.js
// This is the core of our API Gateway. It's built with Express and handles
// all incoming API requests, routing them to the right microservice.

const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

// Let's set up our Express application.
const app = express();
// We'll use port 3000, or whatever the environment specifies.
const PORT = process.env.PORT || 3000;

// This is a simple middleware to log every request that hits our gateway.
// It's super helpful for debugging!
app.use((req, res, next) => {
    console.log(`[API Gateway] Received request: ${req.method} ${req.originalUrl}`);
    next();
});

// We're setting up a proxy for the Product Catalog Service.
// This is the magic that makes our microservices work together seamlessly.
const productCatalogProxy = createProxyMiddleware({
    // 'product_catalog_app' is the service name from our docker-compose.yml file.
    // Docker's internal DNS makes this work automatically.
    target: 'http://product_catalog_app:8000',
    // 'changeOrigin' is important to make sure the target host header is
    // set correctly for the backend service.
    changeOrigin: true,
    pathRewrite: {
        // This line is a crucial piece of the puzzle! It strips the '/api/products'
        // prefix from the incoming URL before it's sent to the backend.
        // For example: '/api/products/items' becomes just '/items'.
        '^/api/products': '/',
    },
    onProxyReq: (proxyReq, req, res) => {
        // Just a little log to let us know the request is being proxied.
        console.log(`[API Gateway] Proxying request to Product Catalog: ${proxyReq.path}`);
    },
});

// Here, we're telling Express to use our proxy for any requests that start
// with '/api/products'.
app.use('/api/products', productCatalogProxy);

// This is just a basic route to confirm that the gateway itself is up and running.
// You can hit this endpoint directly at http://localhost/ if you want to check.
app.get('/', (req, res) => {
    res.send('API Gateway is running!');
});

// Time to fire up the server!
app.listen(PORT, () => {
    console.log(`[API Gateway] Server is listening on port ${PORT}`);
});
