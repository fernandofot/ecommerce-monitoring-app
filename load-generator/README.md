# E-commerce Traffic Generator

This directory contains a Python script (`traffic_generator.py`) designed to simulate user traffic for the `ecommerce-monitoring-app`. Its primary purpose is to generate realistic load for testing and demonstrating Application Performance Monitoring (APM) tools.

## Features

*   **Simulates User Journeys:** Mimics typical user actions like logging in, browsing products, and creating orders.
*   **Configurable Load:** Adjust the number of concurrent users and the duration of the traffic.
*   **Traffic Modes:** Supports continuous traffic generation and burst (stress test) scenarios.
*   **Observability Focus:** Designed to create observable interactions across microservices, making it ideal for APM tool evaluation.

## Setup

1.  **Navigate to the `load-generator` directory:**
    ```bash
    cd load-generator
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Ensure you have Python and pip installed. It's recommended to use a virtual environment.)*

## Usage

The script connects to your running `ecommerce-monitoring-app` instance (typically at `http://localhost:8080`).

### Basic Continuous Traffic (Default)

This will run for 5 minutes (300 seconds) with 10 concurrent simulated users.

```
python traffic_generator.py
```

## Customizing Traffic 

You can adjust the behavior using command-line arguments:

* --url <URL>: Specify the base URL of your application (e.g., http://localhost:8080).
* --users <NUMBER>: Set the number of concurrent simulated users.
* --duration <SECONDS>: Define how long the continuous traffic will run.
* --mode <MODE>: Choose between continuous (default) or burst.
* --burst-requests <NUMBER>: For burst mode, specify the total number of requests to send.

**Examples**

* **Run for 10 minutes with 25 users:**

```
python traffic_generator.py --users 25 --duration 600
```

* **Perform a burst test with 500 requests:**

```
python traffic_generator.py --mode burst --burst-requests 500
```

* **Target a different deployment URL:**

```
python traffic_generator.py --url http://your-staging-env.com --users 15 --duration 900
```