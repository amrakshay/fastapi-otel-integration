#!/usr/bin/env python3
"""
Standalone Python script to randomly make calls to FastAPI endpoints.
Makes random calls to /trust3, /snowflake, /salesforce, /exception endpoints
on localhost:8000 with random intervals within 1 minute, until 1000 total calls.
"""

import random
import time
import requests
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EndpointLoadTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.endpoints = ["/trust3", "/snowflake", "/salesforce", "/exception", "/bad-request", "/create-resource"]
        self.total_calls = 0
        self.target_calls = 1000
        self.stats = {
            "successful_calls": 0,
            "failed_calls": 0,
            "calls_per_endpoint": {endpoint: 0 for endpoint in self.endpoints},
            "start_time": None,
            "end_time": None
        }
        
        # Session for connection pooling
        self.session = requests.Session()
        
    def make_request(self, endpoint):
        """Make a single request to the specified endpoint."""
        url = f"{self.base_url}{endpoint}"
        try:
            # Add a reasonable timeout
            response = self.session.get(url, timeout=10)
            
            # Log the response
            if response.status_code == 200:
                self.stats["successful_calls"] += 1
                logger.info(f"✓ Call #{self.total_calls}: {endpoint} -> {response.status_code}")
            else:
                self.stats["failed_calls"] += 1
                logger.warning(f"⚠ Call #{self.total_calls}: {endpoint} -> {response.status_code}")
                
            self.stats["calls_per_endpoint"][endpoint] += 1
            return True
            
        except requests.exceptions.RequestException as e:
            self.stats["failed_calls"] += 1
            logger.error(f"✗ Call #{self.total_calls}: {endpoint} -> Error: {e}")
            self.stats["calls_per_endpoint"][endpoint] += 1
            return False
    
    def get_random_endpoint(self):
        """Get a randomly selected endpoint."""
        return random.choice(self.endpoints)
    
    def get_random_wait_time(self):
        """Get a random wait time between 0 and 60 seconds."""
        # return random.uniform(0, 60)
        return 1
    
    def print_progress(self):
        """Print current progress and statistics."""
        if self.total_calls % 50 == 0 or self.total_calls <= 10:
            logger.info(f"Progress: {self.total_calls}/{self.target_calls} calls made")
            logger.info(f"Success rate: {self.stats['successful_calls']}/{self.total_calls}")
            
    def print_final_stats(self):
        """Print final statistics."""
        duration = self.stats["end_time"] - self.stats["start_time"]
        logger.info("\n" + "="*60)
        logger.info("LOAD TEST COMPLETED!")
        logger.info("="*60)
        logger.info(f"Total calls made: {self.total_calls}")
        logger.info(f"Total duration: {duration:.2f} seconds")
        logger.info(f"Average calls per second: {self.total_calls/duration:.2f}")
        logger.info(f"Successful calls: {self.stats['successful_calls']}")
        logger.info(f"Failed calls: {self.stats['failed_calls']}")
        logger.info(f"Success rate: {(self.stats['successful_calls']/self.total_calls)*100:.1f}%")
        
        logger.info("\nCalls per endpoint:")
        for endpoint, count in self.stats["calls_per_endpoint"].items():
            percentage = (count/self.total_calls)*100
            logger.info(f"  {endpoint}: {count} calls ({percentage:.1f}%)")
        logger.info("="*60)
    
    def run_load_test(self):
        """Run the main load test."""
        logger.info(f"Starting load test: {self.target_calls} calls to {self.base_url}")
        logger.info(f"Endpoints: {', '.join(self.endpoints)}")
        logger.info("Random intervals between calls: 0-60 seconds")
        logger.info("-" * 60)
        
        self.stats["start_time"] = time.time()
        
        try:
            while self.total_calls < self.target_calls:
                # Select random endpoint
                endpoint = self.get_random_endpoint()
                
                # Increment call counter
                self.total_calls += 1
                
                # Make the request
                self.make_request(endpoint)
                
                # Print progress
                self.print_progress()
                
                # If we haven't reached the target, wait for a random interval
                if self.total_calls < self.target_calls:
                    wait_time = self.get_random_wait_time()
                    logger.debug(f"Waiting {wait_time:.1f} seconds before next call...")
                    time.sleep(wait_time)
                    
        except KeyboardInterrupt:
            logger.info("\n\nLoad test interrupted by user!")
        except Exception as e:
            logger.error(f"Unexpected error during load test: {e}")
        finally:
            self.stats["end_time"] = time.time()
            self.session.close()
            self.print_final_stats()

def main():
    """Main function to run the load test."""
    print("FastAPI Endpoint Load Tester")
    print("============================")
    
    # You can modify these parameters as needed
    base_url = "http://localhost:8000"
    
    # Create and run the load tester
    tester = EndpointLoadTester(base_url=base_url)
    
    try:
        # Test connectivity first
        logger.info(f"Testing connectivity to {base_url}...")
        response = requests.get(f"{base_url}/", timeout=5)
        logger.info(f"✓ Server is reachable: {response.status_code}")
        
        # Run the load test
        tester.run_load_test()
        
    except requests.exceptions.ConnectionError:
        logger.error(f"✗ Cannot connect to {base_url}")
        logger.error("Make sure the FastAPI server is running on localhost:8000")
        logger.error("You can start it with: python main.py or uvicorn main:app --reload")
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()