"""
Tests for the taxonomy-based endpoints in the contract manufacturers MCP server.
"""

import asyncio
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from contract_manufacturers_mcp.server import (
    get_manufacturers_by_taxonomy,
    get_manufacturers_by_description,
    call_llm_for_taxonomy_classification,
)
from contract_manufacturers_mcp import db


class TestDbMock:
    """Test fixture to simulate database operations."""

    @staticmethod
    def setup_mocks():
        """Create mock data and patch database functions."""
        print("\nSetting up database mocks")

        # Define test data
        test_manufacturers = [
            {
                "company_name": "Test Beverage Co",
                "email": "info@testbeverage.com",
                "category": "beverages",
                "requirements": ["formulation", "packaging"],
                "taxonomy_path": "Food, Beverages & Tobacco > Beverages",
            },
            {
                "company_name": "Test Beer Makers",
                "email": "info@testbeer.com",
                "category": "beer",
                "requirements": ["brewing", "packaging"],
                "taxonomy_path": "Food, Beverages & Tobacco > Beverages > Alcoholic Beverages > Beer",
            },
            {
                "company_name": "Test Wine Bottlers",
                "email": "info@testwine.com",
                "category": "wine",
                "requirements": ["bottling", "packaging"],
                "taxonomy_path": "Food, Beverages & Tobacco > Beverages > Alcoholic Beverages > Wine",
            },
            {
                "company_name": "Test Bakery",
                "email": "info@testbakery.com",
                "category": "bakery",
                "requirements": ["baking", "packaging"],
                "taxonomy_path": "Food, Beverages & Tobacco > Food Items > Bakery",
            },
        ]

        # Create mock for get_manufacturers_by_taxonomy
        def mock_get_manufacturers_by_taxonomy(taxonomy_path):
            print(f"Mock get_manufacturers_by_taxonomy called with: {taxonomy_path}")
            if not taxonomy_path:
                return []

            results = []
            taxonomy_path_lower = taxonomy_path.lower()

            # Exact match first
            for manufacturer in test_manufacturers:
                if manufacturer["taxonomy_path"].lower() == taxonomy_path_lower:
                    results.append(manufacturer)

            # If no exact match, try partial match (child categories)
            if not results:
                for manufacturer in test_manufacturers:
                    if (
                        manufacturer["taxonomy_path"]
                        .lower()
                        .startswith(taxonomy_path_lower)
                    ):
                        results.append(manufacturer)

            return results

        # Create mocks for other db functions
        get_all_manufacturers_mock = MagicMock(return_value=test_manufacturers)

        # Setup the patches
        patches = [
            patch(
                "contract_manufacturers_mcp.db.get_manufacturers_by_taxonomy",
                side_effect=mock_get_manufacturers_by_taxonomy,
            ),
            patch(
                "contract_manufacturers_mcp.server.db.get_manufacturers_by_taxonomy",
                side_effect=mock_get_manufacturers_by_taxonomy,
            ),
            patch(
                "contract_manufacturers_mcp.db.get_all_manufacturers",
                return_value=test_manufacturers,
            ),
            patch(
                "contract_manufacturers_mcp.server.db.get_all_manufacturers",
                return_value=test_manufacturers,
            ),
        ]

        print(f"Test data created with {len(test_manufacturers)} manufacturers:")
        for m in test_manufacturers:
            print(f"  - {m['company_name']} ({m['taxonomy_path']})")

        return patches, test_manufacturers


class TestTaxonomyEndpoints(unittest.TestCase):
    """Tests for the taxonomy-based endpoints."""

    def setUp(self):
        """Set up the test environment."""
        print("\n=== Setting up TestTaxonomyEndpoints ===")
        self.mock_context = MagicMock()
        self.patches, self.test_manufacturers = TestDbMock.setup_mocks()

        # Start patches
        for p in self.patches:
            p.start()

        print("Patched db module functions with test data")

    def tearDown(self):
        """Clean up after tests."""
        print("=== Tearing down TestTaxonomyEndpoints ===")

        # Stop patches
        for p in self.patches:
            p.stop()

        print("Removed patches for db module functions")

    def test_get_manufacturers_by_taxonomy_exact_match(self):
        """Test getting manufacturers with an exact taxonomy match."""
        print("\n--- Running test_get_manufacturers_by_taxonomy_exact_match ---")

        # Input
        taxonomy_path = "Food, Beverages & Tobacco > Beverages"
        print(f"INPUT: taxonomy_path = '{taxonomy_path}'")

        # Function call
        result = get_manufacturers_by_taxonomy(taxonomy_path, self.mock_context)

        # Output
        print("OUTPUT:")
        print(f"  - Result count: {len(result)} manufacturers")
        for idx, manufacturer in enumerate(result):
            print(
                f"  - Result[{idx}]: {manufacturer['company_name']} | {manufacturer['email']} | {manufacturer['taxonomy_path']}"
            )
        print(f"  - Raw result: {result}")

        # Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["company_name"], "Test Beverage Co")
        print("✅ Test passed: Found exactly 1 manufacturer with correct name")

    def test_get_manufacturers_by_taxonomy_partial_match(self):
        """Test getting manufacturers with a partial taxonomy match (parent category)."""
        print("\n--- Running test_get_manufacturers_by_taxonomy_partial_match ---")

        # Input
        taxonomy_path = "Food, Beverages & Tobacco > Beverages > Alcoholic Beverages"
        print(f"INPUT: taxonomy_path = '{taxonomy_path}'")

        # Function call
        result = get_manufacturers_by_taxonomy(taxonomy_path, self.mock_context)

        # Output
        print("OUTPUT:")
        print(f"  - Result count: {len(result)} manufacturers")
        for idx, manufacturer in enumerate(result):
            print(
                f"  - Result[{idx}]: {manufacturer['company_name']} | {manufacturer['email']} | {manufacturer['taxonomy_path']}"
            )
        print(f"  - Raw result: {result}")

        # Assertions
        self.assertEqual(len(result), 2)
        company_names = [m["company_name"] for m in result]
        self.assertIn("Test Beer Makers", company_names)
        self.assertIn("Test Wine Bottlers", company_names)
        print("✅ Test passed: Found 2 manufacturers with correct company names")

    def test_get_manufacturers_by_taxonomy_no_match(self):
        """Test getting manufacturers with no taxonomy match."""
        print("\n--- Running test_get_manufacturers_by_taxonomy_no_match ---")

        # Input
        taxonomy_path = "Health & Beauty > Personal Care"
        print(f"INPUT: taxonomy_path = '{taxonomy_path}'")

        # Function call
        result = get_manufacturers_by_taxonomy(taxonomy_path, self.mock_context)

        # Output
        print("OUTPUT:")
        print(f"  - Result count: {len(result)} manufacturers")
        print(f"  - Raw result: {result}")

        # Assertions
        self.assertEqual(len(result), 0)
        print("✅ Test passed: No manufacturers were found (as expected)")

    def test_get_manufacturers_by_taxonomy_empty_input(self):
        """Test getting manufacturers with empty taxonomy path."""
        print("\n--- Running test_get_manufacturers_by_taxonomy_empty_input ---")

        # Input
        taxonomy_path = ""
        print(f"INPUT: taxonomy_path = '{taxonomy_path}'")

        # Function call
        result = get_manufacturers_by_taxonomy(taxonomy_path, self.mock_context)

        # Output
        print("OUTPUT:")
        print(f"  - Result count: {len(result)} manufacturers")
        print(f"  - Raw result: {result}")

        # Assertions
        self.assertEqual(len(result), 0)
        print("✅ Test passed: No manufacturers were found (as expected)")


class TestDescriptionEndpoint(unittest.TestCase):
    """Tests for the description-based endpoint."""

    def setUp(self):
        """Set up the test environment."""
        print("\n=== Setting up TestDescriptionEndpoint ===")
        self.mock_context = MagicMock()
        self.patches, self.test_manufacturers = TestDbMock.setup_mocks()

        # Add LLM patch
        self.llm_patcher = patch(
            "contract_manufacturers_mcp.server.call_llm_for_taxonomy_classification"
        )

        # Start patches
        for p in self.patches:
            p.start()
        self.mock_llm = self.llm_patcher.start()

        print("Patched db module functions and LLM classification function")

    def tearDown(self):
        """Clean up after tests."""
        print("=== Tearing down TestDescriptionEndpoint ===")

        # Stop patches
        for p in self.patches:
            p.stop()
        self.llm_patcher.stop()

        print("Removed patches for db module functions and LLM classification")

    async def _run_get_manufacturers_by_description(
        self, description, mock_taxonomy_path
    ):
        """Helper to run the async method."""
        print(f"Setting up mock LLM to return taxonomy path: '{mock_taxonomy_path}'")
        self.mock_llm.return_value = mock_taxonomy_path
        return await get_manufacturers_by_description(description, self.mock_context)

    def test_get_manufacturers_by_description_match(self):
        """Test getting manufacturers by description with a match."""
        print("\n--- Running test_get_manufacturers_by_description_match ---")

        # Input
        description = "I want to make a new kind of beer"
        mock_taxonomy_path = (
            "Food, Beverages & Tobacco > Beverages > Alcoholic Beverages > Beer"
        )
        print(f"INPUT: description = '{description}'")
        print(
            f"INPUT: mock_taxonomy_path = '{mock_taxonomy_path}' (simulating LLM classification)"
        )

        # Function call
        result = asyncio.run(
            self._run_get_manufacturers_by_description(description, mock_taxonomy_path)
        )

        # Output
        print("OUTPUT:")
        print(f"  - Result taxonomy_path: '{result['taxonomy_path']}'")
        print(f"  - Result manufacturers count: {len(result['manufacturers'])}")
        for idx, manufacturer in enumerate(result["manufacturers"]):
            print(
                f"  - Result[{idx}]: {manufacturer['company_name']} | {manufacturer['email']} | {manufacturer['taxonomy_path']}"
            )
        print(f"  - Result error: {result['error']}")
        print(f"  - Raw result: {result}")

        # Assertions
        self.assertEqual(result["taxonomy_path"], mock_taxonomy_path)
        self.assertEqual(len(result["manufacturers"]), 1)
        self.assertEqual(result["manufacturers"][0]["company_name"], "Test Beer Makers")
        self.assertIsNone(result["error"])
        print(
            "✅ Test passed: Found 1 manufacturer with the correct taxonomy path and company name"
        )

        # Verify LLM was called with the description
        self.mock_llm.assert_called_once_with(description)
        print("✅ Test passed: LLM was called with the correct description")

    def test_get_manufacturers_by_description_no_match(self):
        """Test getting manufacturers by description with no match."""
        print("\n--- Running test_get_manufacturers_by_description_no_match ---")

        # Input
        description = "I want to make skincare products"
        mock_taxonomy_path = "Health & Beauty > Personal Care > Cosmetics > Skin Care"
        print(f"INPUT: description = '{description}'")
        print(
            f"INPUT: mock_taxonomy_path = '{mock_taxonomy_path}' (simulating LLM classification)"
        )

        # Function call
        result = asyncio.run(
            self._run_get_manufacturers_by_description(description, mock_taxonomy_path)
        )

        # Output
        print("OUTPUT:")
        print(f"  - Result taxonomy_path: '{result['taxonomy_path']}'")
        print(f"  - Result manufacturers count: {len(result['manufacturers'])}")
        print(f"  - Result error: {result['error']}")
        print(f"  - Raw result: {result}")

        # Assertions
        self.assertEqual(result["taxonomy_path"], mock_taxonomy_path)
        self.assertEqual(len(result["manufacturers"]), 0)
        self.assertEqual(
            result["error"], "No manufacturers found for this product category"
        )
        print("✅ Test passed: No manufacturers found (as expected)")

        # Verify LLM was called with the description
        self.mock_llm.assert_called_once_with(description)
        print("✅ Test passed: LLM was called with the correct description")

    def test_get_manufacturers_by_description_empty_input(self):
        """Test getting manufacturers with empty description."""
        print("\n--- Running test_get_manufacturers_by_description_empty_input ---")

        # Input
        description = ""
        print(f"INPUT: description = '{description}'")

        # Function call
        result = asyncio.run(
            self._run_get_manufacturers_by_description(description, "")
        )

        # Output
        print("OUTPUT:")
        print(f"  - Result taxonomy_path: '{result['taxonomy_path']}'")
        print(f"  - Result manufacturers count: {len(result['manufacturers'])}")
        print(f"  - Result error: {result['error']}")
        print(f"  - Raw result: {result}")

        # Assertions
        self.assertEqual(result["taxonomy_path"], "")
        self.assertEqual(len(result["manufacturers"]), 0)
        self.assertEqual(result["error"], "Empty product description provided")
        print("✅ Test passed: Error message indicates empty description")

        # Verify LLM was not called
        self.mock_llm.assert_not_called()
        print("✅ Test passed: LLM was not called (as expected)")

    def test_get_manufacturers_by_description_llm_failure(self):
        """Test getting manufacturers when LLM fails to classify."""
        print("\n--- Running test_get_manufacturers_by_description_llm_failure ---")

        # Input
        description = "I want to make a new product"
        print(f"INPUT: description = '{description}'")
        print("INPUT: mock_taxonomy_path = '' (simulating LLM failure to classify)")

        # Setup mock
        self.mock_llm.return_value = ""  # Simulate LLM failure

        # Function call
        result = asyncio.run(
            self._run_get_manufacturers_by_description(description, "")
        )

        # Output
        print("OUTPUT:")
        print(f"  - Result taxonomy_path: '{result['taxonomy_path']}'")
        print(f"  - Result manufacturers count: {len(result['manufacturers'])}")
        print(f"  - Result error: {result['error']}")
        print(f"  - Raw result: {result}")

        # Assertions
        self.assertEqual(result["taxonomy_path"], "")
        self.assertEqual(len(result["manufacturers"]), 0)
        self.assertEqual(result["error"], "Failed to classify product description")
        print("✅ Test passed: Error message indicates classification failure")

        # Verify LLM was called
        self.mock_llm.assert_called_once_with(description)
        print("✅ Test passed: LLM was called with the correct description")


if __name__ == "__main__":
    unittest.main()
