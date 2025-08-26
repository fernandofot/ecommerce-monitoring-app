// api-gateway/index.js

// We're setting up a simple API Gateway using Express.js and the http-proxy-middleware.
// This allows us to route requests to our different microservices from a single entry point.
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

// We're setting up our Express app, the core of our gateway.
const app = express();

// We'll use a dynamic port from the environment, defaulting to 3000 for development.
const PORT = process.env.PORT || 3000;

// This is our log function to keep track of incoming requests and see where they're going.
const logRequest = (req, res, next) => {
    console.log(`[API Gateway] Received a request: ${req.method} ${req.url}`);
    next();
};

// --- Service Proxies ---

// We'll use this proxy configuration for our Product Catalog Service.
// It matches any request that starts with /api/products or /api/cart and sends it there.
const productCatalogProxy = createProxyMiddleware({
    // We're using the service name from docker-compose as the target hostname.
    // Docker's internal DNS handles the resolution for us.
    target: 'http://product-catalog-service:8000',
    changeOrigin: true, // This changes the host header to match the target URL.
    pathRewrite: {
        // We'll remove the /api prefix before forwarding the request to the target service.
        '^/api': '/',
    },
});

// We're adding a new proxy for the User Service.
// It will match any request that starts with /api/users.
const userServiceProxy = createProxyMiddleware({
    // The target hostname is the name of our user-service container.
    target: 'http://user-service:8080',
    changeOrigin: true,
    pathRewrite: {
        // We'll also remove the /api prefix for this service.
        '^/api': '/',
    },
});

// We apply our log function to all incoming requests.
app.use(logRequest);

// --- Routing Rules ---

// Any request to /api/products will be forwarded to the Product Catalog Service.
app.use('/api/products', productCatalogProxy);

// Any request to /api/cart will also be forwarded to the Product Catalog Service.
app.use('/api/cart', productCatalogProxy);

// --- NEW ROUTING RULE FOR USER SERVICE ---
// Any request to /api/users will be forwarded to the User Service.
app.use('/api/users', userServiceProxy);

// If no other proxy matches, we'll assume it's a frontend request and send a friendly message.
app.get('/', (req, res) => {
    res.send('API Gateway is operational!');
});

// We start our gateway server and listen for incoming connections.
app.listen(PORT, () => {
    console.log(`[API Gateway] Server is listening on port ${PORT}`);
});
