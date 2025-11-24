#!/usr/bin/env python3
"""
E-commerce Traffic Generator
Simulates realistic user behavior for APM monitoring
"""

import requests
import random
import time
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import argparse

class EcommerceTrafficGenerator:
    def __init__(self, base_url="http://localhost:8080", num_users=10, duration=300):
        self.base_url = base_url
        self.num_users = num_users
        self.duration = duration
        self.session = requests.Session()
        
        # Sample user data
        self.users = [f"user-{i:03d}" for i in range(1, num_users + 1)]
        
        # Sample products (you can fetch these from your API)
        self.products = [
            {"productId": "p-001", "productName": "Wireless Mouse", "unitPrice": 29.99},
            {"productId": "p-002", "productName": "Mechanical Keyboard", "unitPrice": 89.99},
            {"productId": "p-003", "productName": "USB-C Hub", "unitPrice": 49.99},
            {"productId": "p-004", "productName": "Laptop Stand", "unitPrice": 39.99},
            {"productId": "p-005", "productName": "Webcam HD", "unitPrice": 79.99},
            {"productId": "p-006", "productName": "Headphones", "unitPrice": 129.99},
            {"productId": "p-007", "productName": "Monitor 27\"", "unitPrice": 299.99},
            {"productId": "p-008", "productName": "Desk Lamp", "unitPrice": 34.99},
        ]
        
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "orders_created": 0,
            "products_viewed": 0,
            "logins": 0
        }

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def login_user(self, username):
        """Simulate user login"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": username, "password": "password123"},
                timeout=5
            )
            self.stats["total_requests"] += 1
            
            if response.status_code == 200:
                self.stats["successful_requests"] += 1
                self.stats["logins"] += 1
                token = response.json().get("token")
                self.log(f"✓ User {username} logged in")
                return token
            else:
                self.stats["failed_requests"] += 1
                self.log(f"✗ Login failed for {username}: {response.status_code}")
                return None
        except Exception as e:
            self.stats["failed_requests"] += 1
            self.log(f"✗ Login error for {username}: {str(e)}")
            return None

    def browse_products(self):
        """Simulate browsing product catalog"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/products/",
                timeout=5
            )
            self.stats["total_requests"] += 1
            
            if response.status_code == 200:
                self.stats["successful_requests"] += 1
                self.stats["products_viewed"] += 1
                self.log(f"✓ Browsed product catalog")
                return response.json()
            else:
                self.stats["failed_requests"] += 1
                self.log(f"✗ Failed to browse products: {response.status_code}")
                return []
        except Exception as e:
            self.stats["failed_requests"] += 1
            self.log(f"✗ Browse error: {str(e)}")
            return []

    def create_order(self, user_id):
        """Simulate creating an order"""
        # Select random products for the cart
        num_items = random.randint(1, 4)
        cart_items = []
        
        for _ in range(num_items):
            product = random.choice(self.products)
            quantity = random.randint(1, 3)
            cart_items.append({
                "productId": product["productId"],
                "productName": product["productName"],
                "quantity": quantity,
                "unitPrice": product["unitPrice"]
            })
        
        order_data = {
            "userId": user_id,
            "items": cart_items
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/orders",
                json=order_data,
                timeout=5
            )
            self.stats["total_requests"] += 1
            
            if response.status_code in [200, 201]:
                self.stats["successful_requests"] += 1
                self.stats["orders_created"] += 1
                order = response.json()
                total = sum(item["quantity"] * item["unitPrice"] for item in cart_items)
                self.log(f"✓ Order created for {user_id}: ${total:.2f} ({num_items} items)")
                return order
            else:
                self.stats["failed_requests"] += 1
                self.log(f"✗ Order failed for {user_id}: {response.status_code}")
                return None
        except Exception as e:
            self.stats["failed_requests"] += 1
            self.log(f"✗ Order error for {user_id}: {str(e)}")
            return None

    def check_health(self):
        """Check service health"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                self.log("✓ Health check passed")
                return True
            else:
                self.log(f"✗ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"✗ Health check error: {str(e)}")
            return False

    def simulate_user_session(self, user_id):
        """Simulate a complete user shopping session"""
        self.log(f"Starting session for {user_id}")
        
        # 1. Login
        token = self.login_user(user_id)
        time.sleep(random.uniform(0.5, 2))
        
        # 2. Browse products (1-3 times)
        browse_count = random.randint(1, 3)
        for _ in range(browse_count):
            self.browse_products()
            time.sleep(random.uniform(1, 3))
        
        # 3. Create order (70% chance)
        if random.random() < 0.7:
            self.create_order(user_id)
            time.sleep(random.uniform(1, 2))
        
        # 4. Sometimes browse again after ordering
        if random.random() < 0.3:
            self.browse_products()
        
        self.log(f"Session completed for {user_id}")

    def run_continuous_traffic(self):
        """Generate continuous traffic for specified duration"""
        self.log(f"Starting traffic generation for {self.duration} seconds")
        self.log(f"Simulating {self.num_users} concurrent users")
        self.log(f"Target: {self.base_url}")
        
        # Initial health check
        if not self.check_health():
            self.log("Warning: Initial health check failed, but continuing...")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.num_users) as executor:
            while time.time() - start_time < self.duration:
                # Submit user sessions
                user = random.choice(self.users)
                executor.submit(self.simulate_user_session, user)
                
                # Random delay between sessions
                time.sleep(random.uniform(0.5, 3))
        
        self.print_stats()

    def run_burst_traffic(self, num_requests=100):
        """Generate burst traffic (stress test)"""
        self.log(f"Starting burst traffic: {num_requests} requests")
        
        with ThreadPoolExecutor(max_workers=self.num_users) as executor:
            futures = []
            for i in range(num_requests):
                user = random.choice(self.users)
                futures.append(executor.submit(self.simulate_user_session, user))
            
            # Wait for all to complete
            for future in futures:
                future.result()
        
        self.print_stats()

    def print_stats(self):
        """Print traffic generation statistics"""
        print("\n" + "="*60)
        print("TRAFFIC GENERATION STATISTICS")
        print("="*60)
        print(f"Total Requests:      {self.stats['total_requests']}")
        print(f"Successful:          {self.stats['successful_requests']}")
        print(f"Failed:              {self.stats['failed_requests']}")
        print(f"Success Rate:        {(self.stats['successful_requests']/max(self.stats['total_requests'],1)*100):.2f}%")
        print("-"*60)
        print(f"Logins:              {self.stats['logins']}")
        print(f"Products Viewed:     {self.stats['products_viewed']}")
        print(f"Orders Created:      {self.stats['orders_created']}")
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="E-commerce Traffic Generator")
    parser.add_argument("--url", default="http://localhost:8080", help="Base URL of the application")
    parser.add_argument("--users", type=int, default=10, help="Number of concurrent users")
    parser.add_argument("--duration", type=int, default=300, help="Duration in seconds (for continuous mode)")
    parser.add_argument("--mode", choices=["continuous", "burst"], default="continuous", help="Traffic generation mode")
    parser.add_argument("--burst-requests", type=int, default=100, help="Number of requests for burst mode")
    
    args = parser.parse_args()
    
    generator = EcommerceTrafficGenerator(
        base_url=args.url,
        num_users=args.users,
        duration=args.duration
    )
    
    if args.mode == "continuous":
        generator.run_continuous_traffic()
    else:
        generator.run_burst_traffic(args.burst_requests)


if __name__ == "__main__":
    main()