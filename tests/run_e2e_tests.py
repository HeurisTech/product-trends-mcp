#!/usr/bin/env python
"""
Run the end-to-end tests for the contract manufacturers MCP server.

This script:
1. Sets up the environment
2. Makes sure the CSV file and/or SQLite DB file are accessible
3. Runs the E2E tests
"""

import os
import sys
import unittest
import subprocess
from pathlib import Path
import shutil

# Get the root directory of the project
ROOT_DIR = Path(__file__).parent.parent.absolute()


def setup_environment():
    """Setup the environment for running tests."""
    print("Setting up environment for E2E tests...")

    # Check if the CSV file exists (needed for initial DB creation)
    csv_path = ROOT_DIR / "contract_manufacturers.csv"
    if not csv_path.exists():
        # Try to find it elsewhere
        alt_csv_path = ROOT_DIR / "data" / "contract_manufacturers.csv"
        if alt_csv_path.exists():
            # Copy it to the expected location
            print(f"Copying CSV from {alt_csv_path} to {csv_path}")
            shutil.copy(alt_csv_path, csv_path)
        else:
            print("WARNING: contract_manufacturers.csv not found!")
            print(f"Expected at: {csv_path}")
            print("Tests might fail if the server can't initialize the database.")
    else:
        print(f"Found CSV file at: {csv_path}")

    # Check if the database file exists
    db_path = ROOT_DIR / "contract_manufacturers.db"
    if db_path.exists():
        print(f"Found SQLite database at: {db_path}")
        # Optionally remove it to ensure clean test environment
        # print("Removing existing database to ensure clean test environment")
        # db_path.unlink()
    else:
        print("SQLite database not found. It will be created during the test.")

    # Set PYTHONPATH to include the src directory
    src_path = str(ROOT_DIR / "src")
    if "PYTHONPATH" in os.environ:
        os.environ["PYTHONPATH"] = f"{src_path}:{os.environ['PYTHONPATH']}"
    else:
        os.environ["PYTHONPATH"] = src_path

    # Set environment variables for tests
    os.environ["CONTRACT_MANUFACTURERS_CSV"] = str(csv_path)
    os.environ["CONTRACT_MANUFACTURERS_DB"] = str(db_path)

    # Check for OpenAI API key
    if "OPENAI_API_KEY" not in os.environ:
        print("WARNING: OPENAI_API_KEY environment variable not set")
        print("The description-based endpoint tests will be skipped")
    else:
        print("Found OPENAI_API_KEY in environment")


def run_tests():
    """Run the E2E tests."""
    print("Running E2E tests...")

    # Run the tests
    from test_e2e_server import TestContractManufacturersE2E

    # Create a test suite with our E2E tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestContractManufacturersE2E)

    # Run the tests
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    # Return success/failure
    return result.wasSuccessful()


if __name__ == "__main__":
    # Change to the project root directory to make imports work
    os.chdir(ROOT_DIR)

    # Setup the environment
    setup_environment()

    # Run the tests
    success = run_tests()

    # Exit with appropriate status code
    sys.exit(0 if success else 1)
