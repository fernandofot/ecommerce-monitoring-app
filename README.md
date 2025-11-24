# E-commerce Monitoring Application (Multi-Technology Microservices)
This project is a sample e-commerce application designed with a microservices architecture using a diverse set of technologies. Its primary purpose is to serve as a demonstration platform for Application Performance Monitoring (APM) tools like Dynatrace, IBM Instana, and AppDynamics, showcasing distributed tracing, performance metrics, and inter-service communication in a heterogeneous environment.

The application aims to mimic a simplified version of a large-scale e-commerce platform like Amazon, focusing on creating observable interactions across different technology stacks.

## Project Goal
To build a multi-technology microservices application that can be easily containerized with Docker and orchestrated with Kubernetes, providing a rich environment for comprehensive APM tool evaluation and demonstration.

## Architecture & Technologies
The application is structured as a set of independent microservices, each potentially using a different technology stack.

![Architecture of Microservices](/frontend/public/images/ArchitectureFlowchart.png)

* **Service Overview**

The application is structured as a set of independent microservices, each using a different technology stack.

| Service                                              | Language      | Description                                                                                                                       |
| ---------------------------------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Frontend Application                          | React / Nginx            | User-facing web interface. Built with React and served by an Nginx web server. |
| API Gateway                    | Node.js / Express            | The primary entry point for the frontend, routing and aggregating calls to backend services.                                                           |
| User & Authentication | Java / Spring Boot            | Handles user registration, authentication with a login endpoint, and JSON Web Token (JWT) generation.                        |
| Product Catalog             | Python / FastAPI       | Manages product data (CRUD operations) and stock levels from a MySQL database. |
| Order Processing               | .NET / ASP.NET Core       | Manages the order lifecycle, handling shopping carts and order-related operations.                                     |


* **Planned Services:** 
(Future additions to expand the microservices architecture)

| Service                                              | Language      | Description                                                                                                                       |
| ---------------------------------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Cart Service                           | C#            | Stores the items in the user's shopping cart in Redis and retrieves it. |
| Currency Service                     | Node.js            | Converts a monetary amount to another currency using real values from the European Central Bank. It's the highest QPS service.                                                           |
| Payment Service | Node.js            | Mocks charging a credit card with the given amount and returns a transaction ID.                        |
| Shipping Service             | Go       | Gives shipping cost estimates based on the shopping cart. |
| Email Service               | Python       | Mocks sending an order confirmation email to the user.                                     |
| Checkout Service             | Go            | Orchestrates the final checkout flow, retrieving the cart, preparing the order, and calling the payment, shipping, and email services.                                 |
| Recommendation Service                   | Python        | Recommends other products based on what's currently in the cart.                                                                                   |
| Ad Service             | Java            | Provides text ads based on given context words.                            |
| Load Generator | Python / Locust        | Continuously sends requests to the frontend, imitating realistic user shopping flows.                                                                      |


## Observability Focus

A core aspect of this project is its design for monitoring and observability. Future integrations will include:

* **Structured Logging:** Consistent logging with trace/span IDs.

* **Metrics Exposure:** Application-specific metrics for performance analysis.

* **Distributed Tracing (OpenTelemetry):** End-to-end transaction visibility across all services.

* **Health Checks:** Standardized endpoints for liveness and readiness probes.

### Order Service – APM-Focused Logging

The `.NET / ASP.NET Core` order-service exposes `/orders` (and is accessible externally via `/api/orders` through the API Gateway).  
On creating an order, it emits a structured log event like:

- `Event`: `order_created`
- `UserId`: user who placed the order
- `OrderId`: generated order identifier
- `TotalItems`: sum of quantities in the cart
- `TotalAmount`: total amount for the order
- `Items`: list of `{ ProductId, ProductName, Quantity, UnitPrice }`

This log can be ingested by Dynatrace, Instana, or other APM / log systems to analyze cart contents and order behavior without querying the database.

Example request (via Nginx + API Gateway):

```
bash
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-123",
    "items": [
      {
        "productId": "p-001",
        "productName": "Wireless Mouse",
        "quantity": 2,
        "unitPrice": 29.99
      },
      {
        "productId": "p-002",
        "productName": "Mechanical Keyboard",
        "quantity": 1,
        "unitPrice": 89.99
      }
    ]
  }'

```
The order-service responds with the created order and logs the OrderCreated event.

## Setup and Running the Application
This guide assumes you have Docker installed and running on your system.

**1. Project Structure**

Ensure your project directory is structured as follows:
```
ecommerce-monitoring-app/
├── api-gateway/
│ ├── Dockerfile
│ ├── package.json
│ └── server.js
├── user-service/
│ ├── pom.xml
│ ├── src/
│ │ └── ...
│ └── Dockerfile
├── product-catalog-service/
│ ├── main.py
│ ├── requirements.txt
│ └── Dockerfile
├── frontend/
│ ├── public/
│ │ ├── images/
│ │ │ ├── catalog_api.png
│ │ │ └── home.png
│ │ └── index.html
│ ├── src/
│ │ ├── App.js
│ │ └── index.js
│ ├── package.json
│ └── Dockerfile
├── nginx/
│ ├── nginx.conf
│ └── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md

```
**Base images note (Apple Silicon & modern runtimes)**

- The **user-service** uses `eclipse-temurin:17-jre` as the runtime image instead of the older `openjdk:17-jre-alpine`, which is deprecated and not available for Apple Silicon.
- The **frontend** builder uses `node:20-alpine` to align with the current Node.js LTS and avoid image metadata issues on M‑series Macs.

**2. Docker Compose Configuration**

The ```docker-compose.yml``` file orchestrates all services: the MySQL database, the Product Catalog Service, a frontend builder, and the Nginx reverse proxy, connecting them to a shared Docker network.

***(The full ```docker-compose.yml``` content is in the file itself, not replicated here for brevity and to avoid redundancy.)***

**3. Build and Run Services**

Navigate to the root of your ```ecommerce-app``` directory in your terminal:
```
cd ecommerce-monitoring-app
```
First, perform a clean shutdown and remove any old containers/volumes to ensure a fresh start:
```
docker compose down --volumes --remove-orphans
```
Next, build all the necessary Docker images:
```
docker compose build

```
Finally, start all services in detached mode:

```
docker compose up -d
```
This command will:

* Create and start the ```mysql_db``` container.

* Create and run the ```ecommerce_frontend_builder container```, which builds the React app and then exits.

* Create and start the ```user_auth_app``` container.

* Create and start the ```product_catalog_app``` container ensuring it waits for the database to be healthy.

* Create and start the ```order_service_app``` container.

* Create and start the ```api_gateway``` container.

* Create and start the ```ecommerce_nginx``` container, which serves the built React app and proxies API requests to the ```api_gateway```.

**4. Verify Services**

Check that both containers are running:
```
docker ps
```
You should see ```mysql_db```, ```user_auth_app```, ```product_catalog_app```, ```order_service_app``` ,```api_gateway```, and ```ecommerce_nginx``` listed with a ```Up``` status. The ```ecommerce_frontend_builder``` container should show as Exited.

**5. Access the Application**

* **Frontend Application:**

    Open your web browser and navigate to:
    
    ```
    http://localhost:8080
    ```

    You should see the E-commerce Store frontend displaying products.

    ![E-commerce Store Frontend](frontend/public/images/home.png)

  **New Feature: Add to Cart**
    
    * **Add to Cart:** Clicking the "Add to Cart" button on any product sends a request to the backend, updates a simulated cart count, and decreases the product's stock level.
    * **Clear Cart:** A new "Clear Cart" button on the cart page sends a request to the backend, which removes all items from the cart and returns the stock to the product catalog. 

* **Test the Authentication Service**

    Now that you've added the login endpoint, you can test it to get a JWT.

    ```
    curl -X POST http://localhost:8080/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{
      "username": "testuser",
      "password": "password123"
    }'
    ```

    A successful response will return a JSON Web Token (JWT), confirming that the authentication is working correctly.

Product Catalog Service API Docs (via API Gateway):**  You can access the FastAPI interactive documentation (Swagger UI) by navigating through the API Gateway, which Nginx proxies to:

```
http://localhost/api/docs
```

From the Swagger UI, you can test the API endpoints (e.g., ```GET /products/```, ```POST /products/```).

* The API documentation is now fully accessible and interactive via the Nginx proxy.

* Test the ```GET /health``` endpoint to confirm the service and database connection are healthy.

* Use the ```POST /products/``` endpoint to add new products to the catalog.

* Use ```GET /products/``` to retrieve all products.

![E-commerce Store Frontend](frontend/public/images/catalog_api.png)

**Order Service (via API Gateway)**

Create an order (for APM/logging demos):

```
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-123",
    "items": [
      {
        "productId": "p-001",
        "productName": "Wireless Mouse",
        "quantity": 2,
        "unitPrice": 29.99
      },
      {
        "productId": "p-002",
        "productName": "Mechanical Keyboard",
        "quantity": 1,
        "unitPrice": 89.99
      }
    ]
  }'

  ```

  This both:

* Returns the created order as JSON.
* Emits a structured OrderCreated log with full cart details.

## Development
**Adding New Services**

When adding a new microservice:

1.  Create a new directory for the service (e.g., ```user-service/```).

2.  Develop your service logic in the chosen technology (e.g., Java Spring Boot, Node.js Express).

3.  Create a ```Dockerfile``` for the new service.

4.  Add the new service to your ```docker-compose.yml``` file, defining its build context, ports, environment variables, and network.

5.  Update the ```README.md``` to reflect the new service.

**Monitoring Integration**

Future steps will involve integrating OpenTelemetry (or specific APM agent SDKs) into each service to emit traces, metrics, and logs, making the entire application observable.

This README provides a solid foundation.

### Hardware Requirements

To run this application smoothly, especially when starting all services simultaneously, your server should have a minimum of **8GB of RAM and 4 CPUs**. This recommendation is based on the resource-intensive nature of the services included, particularly the MySQL database and the Java/Spring Boot application. During startup, these services can consume significant amounts of memory, and on servers with limited resources (like 4GB RAM), this can lead to slow initialization and container health check failures. A more powerful machine ensures that all containers can start and become healthy without resource contention, providing a stable environment for the application.
