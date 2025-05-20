#!/usr/bin/env python3
"""
End-to-end test runner for the Product Trends MCP server.

This script:
1. Starts the Product Trends MCP server as a separate process
2. Runs tests against the live server
3. Stops the server when done
"""

import os
import sys
import time
import signal
import subprocess
import unittest
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("e2e-test-runner")

# Directory where the server module is located
SERVER_MODULE = "product_trends_mcp.server"
TEST_MODULE = "tests.test_e2e_server"

def run_server(port=8787):
    """Start the server as a separate process."""
    # Make sure PYTHONPATH includes the project root
    env = os.environ.copy()
    
    # Set a special environment variable to tell the server it's being run in test mode
    env["PRODUCT_TRENDS_TEST_MODE"] = "1"
    env["APIFY_API_TOKEN"] = "test_token"  # Use test token for testing
    
    # Start the server as a separate process
    command = [sys.executable, "-m", SERVER_MODULE, "--port", str(port)]
    process = subprocess.Popen(command, env=env)
    
    # Give the server time to start up
    time.sleep(2)
    
    return process

def run_tests():
    """Run the tests using unittest."""
    # Run the tests
    test_result = unittest.main(module=TEST_MODULE, exit=False)
    return test_result.result.wasSuccessful()

def main():
    """Main function to run the end-to-end tests."""
    server_process = None
    test_port = 8787
    
    try:
        logger.info("Starting Product Trends MCP server on port %s...", test_port)
        server_process = run_server(port=test_port)
        
        logger.info("Running end-to-end tests...")
        success = run_tests()
        
        if success:
            logger.info("✅ All tests passed!")
            return 0
        else:
            logger.error("❌ Tests failed")
            return 1
    except KeyboardInterrupt:
        logger.info("Tests interrupted")
        return 1
    finally:
        if server_process:
            logger.info("Stopping server (PID: %s)...", server_process.pid)
            # Try to terminate gracefully first
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # If graceful termination doesn't work, kill it
                server_process.kill()
                server_process.wait()
            logger.info("Server stopped")

if __name__ == "__main__":
    sys.exit(main())
