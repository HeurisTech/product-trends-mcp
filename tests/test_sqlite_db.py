#!/usr/bin/env python
"""
Test script for the SQLite database implementation.
This script tests database creation, migration from CSV, and basic queries.
"""

import os
import sys
import csv
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# Import the database module
from contract_manufacturers_mcp import db

# Get the root directory
ROOT_DIR = Path(__file__).parent.parent.absolute()

# Set up environment
os.environ["CONTRACT_MANUFACTURERS_CSV"] = str(ROOT_DIR / "contract_manufacturers.csv")
os.environ["CONTRACT_MANUFACTURERS_DB"] = str(
    ROOT_DIR / "test_contract_manufacturers.db"
)

# Path to test database
TEST_DB_PATH = os.environ["CONTRACT_MANUFACTURERS_DB"]


def ensure_csv_exists():
    """Make sure the CSV file exists for testing."""
    csv_path = Path(os.environ["CONTRACT_MANUFACTURERS_CSV"])

    if not csv_path.exists():
        print(f"CSV file not found at {csv_path}. Creating a test CSV file...")
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["company_name", "email", "category", "requirements", "taxonomy_path"]
            )
            writer.writerow(
                [
                    "Test Beverage Co",
                    "info@testbeverage.com",
                    "beverages",
                    "[formulation, packaging]",
                    "Food, Beverages & Tobacco > Beverages",
                ]
            )
            writer.writerow(
                [
                    "Test Beer Makers",
                    "info@testbeer.com",
                    "beer",
                    "[brewing, packaging]",
                    "Food, Beverages & Tobacco > Beverages > Alcoholic Beverages > Beer",
                ]
            )
            writer.writerow(
                [
                    "Test Wine Bottlers",
                    "info@testwine.com",
                    "wine",
                    "[bottling, packaging]",
                    "Food, Beverages & Tobacco > Beverages > Alcoholic Beverages > Wine",
                ]
            )
            writer.writerow(
                [
                    "Test Bakery",
                    "info@testbakery.com",
                    "bakery",
                    "[baking, packaging]",
                    "Food, Beverages & Tobacco > Food Items > Bakery",
                ]
            )
        print(f"Created test CSV file with 4 manufacturers at {csv_path}")


def cleanup_test_db():
    """Remove the test database if it exists."""
    db_path = Path(TEST_DB_PATH)
    if db_path.exists():
        print(f"Removing existing test database at {db_path}")
        db_path.unlink()


def test_initialization():
    """Test database initialization and migration from CSV."""
    print("\n=== Testing Database Initialization ===")

    # Initialize the database
    db.initialize_database()

    # Check that the database file was created
    db_path = Path(TEST_DB_PATH)
    print(f"Database file exists: {db_path.exists()}")

    # Get all manufacturers to check if data was migrated
    manufacturers = db.get_all_manufacturers()

    # Print the manufacturers
    print(f"Found {len(manufacturers)} manufacturers in the database:")
    for manufacturer in manufacturers:
        print(f"  - {manufacturer['company_name']} ({manufacturer['taxonomy_path']})")
        print(f"    Requirements: {manufacturer['requirements']}")

    # Use assertion instead of returning a value
    assert len(manufacturers) > 0, "Database should contain at least one manufacturer"


def test_queries():
    """Test various database queries."""
    print("\n=== Testing Database Queries ===")

    # Test get_manufacturer_by_name
    print("\n--- Testing get_manufacturer_by_name ---")
    manufacturer = db.get_manufacturer_by_name("Beer")
    if manufacturer:
        print(f"Found manufacturer by name 'Beer': {manufacturer['company_name']}")
    else:
        print("Manufacturer not found by name 'Beer'")
    assert manufacturer is not None, "Should find a manufacturer containing 'Beer'"

    # Test filter_manufacturers_by_category
    print("\n--- Testing filter_manufacturers_by_category ---")
    manufacturers = db.filter_manufacturers_by_category("beverage")
    print(f"Found {len(manufacturers)} manufacturers in 'beverage' category:")
    for manufacturer in manufacturers:
        print(f"  - {manufacturer['company_name']} ({manufacturer['category']})")
    assert len(manufacturers) > 0, "Should find manufacturers in 'beverage' category"

    # Test search_manufacturers
    print("\n--- Testing search_manufacturers ---")
    manufacturers = db.search_manufacturers("packaging")
    print(f"Found {len(manufacturers)} manufacturers with 'packaging' in search:")
    for manufacturer in manufacturers:
        print(
            f"  - {manufacturer['company_name']} (Requirements: {manufacturer['requirements']})"
        )
    assert len(manufacturers) > 0, "Should find manufacturers with 'packaging'"

    # Test get_manufacturers_by_taxonomy
    print("\n--- Testing get_manufacturers_by_taxonomy ---")
    taxonomy_path = "Food, Beverages & Tobacco > Beverages > Alcoholic Beverages"
    manufacturers = db.get_manufacturers_by_taxonomy(taxonomy_path)
    print(
        f"Found {len(manufacturers)} manufacturers with taxonomy path '{taxonomy_path}':"
    )
    for manufacturer in manufacturers:
        print(f"  - {manufacturer['company_name']} ({manufacturer['taxonomy_path']})")
    assert (
        len(manufacturers) > 0
    ), "Should find manufacturers with the given taxonomy path"

    # Test get_manufacturer_requirements
    print("\n--- Testing get_manufacturer_requirements ---")
    requirements = db.get_manufacturer_requirements("Bakery")
    if requirements:
        print(f"Requirements for 'Bakery': {requirements}")
    else:
        print("Requirements not found for 'Bakery'")
    assert (
        requirements is not None
    ), "Should find requirements for manufacturer with 'Bakery' in name"

    # Test get_manufacturers_by_requirement
    print("\n--- Testing get_manufacturers_by_requirement ---")
    manufacturers = db.get_manufacturers_by_requirement("bottling")
    print(f"Found {len(manufacturers)} manufacturers with 'bottling' requirement:")
    for manufacturer in manufacturers:
        print(
            f"  - {manufacturer['company_name']} (Requirements: {manufacturer['requirements']})"
        )
    assert (
        len(manufacturers) > 0
    ), "Should find manufacturers with 'bottling' requirement"


def run_tests():
    """Run all the SQLite database tests."""
    try:
        # Make sure we have a CSV file for testing
        ensure_csv_exists()

        # Clean up any existing test database
        cleanup_test_db()

        # Run initialization test
        test_initialization()

        # Run query tests
        test_queries()

        print("\n✅ All SQLite database tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
