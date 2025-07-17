# E-commerce Monitoring Application (Multi-Technology Microservices)
This project is a sample e-commerce application designed with a microservices architecture using a diverse set of technologies. Its primary purpose is to serve as a demonstration platform for Application Performance Monitoring (APM) tools like Dynatrace, IBM Instana, and AppDynamics, showcasing distributed tracing, performance metrics, and inter-service communication in a heterogeneous environment.

The application aims to mimic a simplified version of a large-scale e-commerce platform like Amazon, focusing on creating observable interactions across different technology stacks.

## Project Goal
To build a multi-technology microservices application that can be easily containerized with Docker and orchestrated with Kubernetes, providing a rich environment for comprehensive APM tool evaluation and demonstration.

## Architecture & Technologies
The application is structured as a set of independent microservices, each potentially using a different technology stack.

* Current Services:**

    * **Product Catalog Service (Python / FastAPI / MySQL)**

        * **Role:** Manages product data (CRUD operations, search, filtering).

        * **Technology:** Python 3.9+, FastAPI, SQLAlchemy, MySQL.

        * **Database:** MySQL.

        * **Containerization:** Docker.

* Planned Services:

    * **Frontend Application (React):** User-facing web interface.

    * **API Gateway / Frontend BFF (Node.js / Express):** Primary entry point for the frontend, aggregating calls to backend services.

    * **User & Authentication Service (Java / Spring Boot):** Handles user registration, login, and authentication.

    * **Order Processing Service (.NET / ASP.NET Core):** Manages the order lifecycle.

    * **Inventory Service (Node.js):** Manages product stock levels.

## Observability Focus
A core aspect of this project is its design for monitoring and observability. Future integrations will include:

    * **Structured Logging:** Consistent logging with trace/span IDs.

    * **Metrics Exposure:** Application-specific metrics for performance analysis.

    * **Distributed Tracing (OpenTelemetry):** End-to-end transaction visibility across all services.

    * **Health Checks:** Standardized endpoints for liveness and readiness probes.

## Setup and Running the Application
This guide assumes you have Docker Desktop installed and running on your system.

**1. Project Structure**

Ensure your project directory is structured as follows:
```
ecommerce-app/
├── product-catalog-service/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
└── .gitignore
└── README.md (this file)
```
**2. Docker Compose Configuration**

The ```docker-compose.yml``` file orchestrates the services. It defines the MySQL database and the Product Catalog Service, connecting them to a shared Docker network.
```
# ecommerce-app/docker-compose.yml
version: '3.8'

services:
  db:
    image: mysql:8.0
    container_name: mysql_db
    environment:
      MYSQL_ROOT_PASSWORD: root_password # IMPORTANT: Change this in production!
      MYSQL_DATABASE: ecommerce_db
      MYSQL_USER: user
      MYSQL_PASSWORD: password # IMPORTANT: Change this in production!
    ports:
      - "3306:3306" # Expose MySQL port for local access
    volumes:
      - db_data:/var/lib/mysql # Persist data
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 20s
      retries: 10
    networks:
      - ecommerce_network

  product-catalog-service:
    build: ./product-catalog-service
    container_name: product_catalog_app
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: "mysql+mysqlconnector://user:password@db:3306/ecommerce_db"
    depends_on:
      db:
        condition: service_healthy
    networks:
      - ecommerce_network

networks:
  ecommerce_network:
    driver: bridge

volumes:
  db_data:
```
**3. Build and Run Services**

Navigate to the root of your ```ecommerce-app``` directory in your terminal:
```
cd ecommerce-app
```
First, ensure your ```product-catalog-service``` Docker image is built (or rebuilt if ```main.py``` was changed):
```
cd product-catalog-service
docker build -t product-catalog-service .
cd .. # Go back to the ecommerce-app root
```
Now, start all services defined in ```docker-compose.yml```:
```
docker compose up -d
```
This command will:

* Create and start the ```mysql_db``` container.

* Create and start the ```product_catalog_app``` container (using the image you just built), ensuring it waits for the database to be healthy.

**4. Verify Services**

Check that both containers are running:
```
docker ps
```
You should see both ```mysql_db``` and ```product_catalog_app``` listed with a ```Up``` status.

**5. Access the Product Catalog Service API**

Open your web browser and navigate to the FastAPI interactive documentation (Swagger UI):

* **Product Catalog Service API Docs:** ```http://localhost:8000/docs```

From the Swagger UI, you can:

* Test the ```GET /health``` endpoint to confirm the service and database connection are healthy.

* Use the ```POST /products/``` endpoint to add new products to the catalog.

* Use ```GET /products/``` to retrieve all products.

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