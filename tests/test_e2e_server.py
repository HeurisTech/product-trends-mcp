"""
End-to-end tests for the contract manufacturers MCP server.

These tests start the actual server and test the endpoints using a client.
"""

import asyncio
import os
import time
import unittest
import subprocess
import sys
from pathlib import Path

import pytest
from fastmcp import Client

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


class TestContractManufacturersE2E(unittest.TestCase):
    """End-to-end tests for the contract manufacturers server."""

    @classmethod
    def setUpClass(cls):
        """Start the server process before running the tests."""
        print("\n=== Starting contract manufacturers server for E2E tests ===")

        # Get the path to the server script
        module_path = "contract_manufacturers_mcp.server"

        # Use a specific port for the server
        cls.server_port = 8765
        cls.server_host = "127.0.0.1"
        cls.server_url = f"http://{cls.server_host}:{cls.server_port}"

        # Create environment with FASTMCP specific variables
        env = os.environ.copy()
        env["FASTMCP_HOST"] = "0.0.0.0"  # Bind to all interfaces so we can connect
        env["FASTMCP_PORT"] = str(cls.server_port)

        print(f"Starting server on port {cls.server_port}")

        # Start the server as a separate process
        cls.server_process = subprocess.Popen(
            [sys.executable, "-m", module_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,  # This enables text mode for more readable output
        )

        # Give the server a moment to start up
        time.sleep(2)

        # Capture any initial output from the server
        stdout_data, stderr_data = "", ""
        if cls.server_process.stdout.readable():
            stdout_data = cls.server_process.stdout.read(4096)
        if cls.server_process.stderr.readable():
            stderr_data = cls.server_process.stderr.read(4096)

        print(f"Server stdout: {stdout_data}")
        print(f"Server stderr: {stderr_data}")

        # Check if the server started successfully
        if cls.server_process.poll() is not None:
            # Server process exited - something went wrong
            stdout, stderr = cls.server_process.communicate()
            stdout = stdout_data + (stdout or "")
            stderr = stderr_data + (stderr or "")
            raise RuntimeError(
                f"Server failed to start. "
                f"Exit code: {cls.server_process.returncode}\n"
                f"stdout: {stdout}\n"
                f"stderr: {stderr}"
            )

        print(f"Server process started with PID {cls.server_process.pid}")
        print(f"Server URL: {cls.server_url}")

    @classmethod
    def tearDownClass(cls):
        """Terminate the server process after all tests have run."""
        print("\n=== Stopping contract manufacturers server ===")
        if hasattr(cls, "server_process"):
            cls.server_process.terminate()
            cls.server_process.wait(timeout=5)
            print(f"Server process terminated")

    async def _run_client_test(self, test_coroutine):
        """Helper to run a test with a client."""
        # Connect to the running server using the server URL
        print(f"Connecting to server at {self.server_url}")
        async with Client(self.server_url) as client:
            # Run the actual test
            return await test_coroutine(client)

    def run_client_test(self, test_coroutine):
        """Synchronous wrapper to run an async client test."""
        return asyncio.run(self._run_client_test(test_coroutine))

    async def _test_list_tools(self, client):
        """Test listing all tools."""
        print("\n--- Testing list_tools ---")

        # Get the list of available tools
        print("Listing available tools...")
        tools = await client.list_tools()

        # Print the tools for debugging
        print(f"Available tools:")
        for tool in tools:
            print(f"  - {tool}")

        # Check that expected tools exist
        expected_tools = [
            "list_all_manufacturers",
            "get_manufacturer_by_name",
            "filter_manufacturers_by_category",
            "search_manufacturers",
            "get_manufacturer_requirements",
            "get_manufacturers_by_requirement",
            "get_manufacturers_by_taxonomy",
            "get_manufacturers_by_description",
            "reload_manufacturers_data",
        ]

        for tool in expected_tools:
            self.assertIn(tool, tools, f"Tool '{tool}' not found in server tools")

        return tools

    def test_list_tools(self):
        """Test that we can list available tools on the server."""
        tools = self.run_client_test(self._test_list_tools)
        self.assertTrue(len(tools) >= 9, "Expected at least 9 tools")

    async def _test_list_all_manufacturers(self, client):
        """Test listing all manufacturers."""
        print("\n--- Testing list_all_manufacturers ---")

        # Call the tool
        print("Calling list_all_manufacturers...")
        result = await client.call_tool("list_all_manufacturers")

        # Print results
        print(f"Got {len(result.value)} manufacturers")
        if len(result.value) > 0:
            print(f"First manufacturer: {result.value[0]['company_name']}")

        # Validate the response
        self.assertTrue(isinstance(result.value, list), "Expected a list response")
        self.assertTrue(len(result.value) > 0, "Expected at least one manufacturer")

        # Check the structure of a manufacturer
        first = result.value[0]
        self.assertIn("company_name", first, "Missing company_name field")
        self.assertIn("email", first, "Missing email field")
        self.assertIn("category", first, "Missing category field")
        self.assertIn("requirements", first, "Missing requirements field")
        self.assertIn("taxonomy_path", first, "Missing taxonomy_path field")

        return result.value

    def test_list_all_manufacturers(self):
        """Test that we can list all manufacturers."""
        manufacturers = self.run_client_test(self._test_list_all_manufacturers)
        self.assertTrue(len(manufacturers) > 0, "Expected at least one manufacturer")

    async def _test_get_manufacturer_by_name(self, client):
        """Test getting a manufacturer by name."""
        print("\n--- Testing get_manufacturer_by_name ---")

        # Get a manufacturer name from the list first
        all_manufacturers = await client.call_tool("list_all_manufacturers")
        manufacturer_name = all_manufacturers.value[0]["company_name"]

        # Call the tool with the name
        print(f"Calling get_manufacturer_by_name with '{manufacturer_name}'...")
        result = await client.call_tool(
            "get_manufacturer_by_name", {"company_name": manufacturer_name}
        )

        # Print result
        print(f"Result: {result.value}")

        # Validate the response
        self.assertIsNotNone(result.value, "Expected a manufacturer, got None")
        self.assertEqual(
            result.value["company_name"],
            manufacturer_name,
            "Returned manufacturer name doesn't match requested name",
        )

        return result.value

    def test_get_manufacturer_by_name(self):
        """Test that we can get a manufacturer by name."""
        manufacturer = self.run_client_test(self._test_get_manufacturer_by_name)
        self.assertIsNotNone(manufacturer, "Expected a manufacturer")

    async def _test_get_manufacturers_by_taxonomy(self, client):
        """Test getting manufacturers by taxonomy path."""
        print("\n--- Testing get_manufacturers_by_taxonomy ---")

        # Get a taxonomy path from the list first
        all_manufacturers = await client.call_tool("list_all_manufacturers")
        taxonomy_path = all_manufacturers.value[0]["taxonomy_path"]

        # Call the tool with the taxonomy path
        print(f"Calling get_manufacturers_by_taxonomy with '{taxonomy_path}'...")
        result = await client.call_tool(
            "get_manufacturers_by_taxonomy", {"taxonomy_path": taxonomy_path}
        )

        # Print results
        print(f"Got {len(result.value)} manufacturers for taxonomy '{taxonomy_path}'")
        for idx, manufacturer in enumerate(result.value):
            print(
                f"  - Result[{idx}]: {manufacturer['company_name']} | {manufacturer['taxonomy_path']}"
            )

        # Validate the response
        self.assertTrue(isinstance(result.value, list), "Expected a list response")
        self.assertTrue(len(result.value) > 0, "Expected at least one manufacturer")

        # Verify all manufacturers have the correct taxonomy path
        for manufacturer in result.value:
            self.assertEqual(
                manufacturer["taxonomy_path"],
                taxonomy_path,
                "Manufacturer taxonomy path doesn't match requested path",
            )

        return result.value

    def test_get_manufacturers_by_taxonomy(self):
        """Test that we can get manufacturers by taxonomy path."""
        manufacturers = self.run_client_test(self._test_get_manufacturers_by_taxonomy)
        self.assertTrue(len(manufacturers) > 0, "Expected at least one manufacturer")

    async def _test_get_manufacturers_by_partial_taxonomy(self, client):
        """Test getting manufacturers by partial taxonomy path."""
        print("\n--- Testing get_manufacturers_by_taxonomy with partial path ---")

        # Use a partial taxonomy path
        taxonomy_path = "Food, Beverages & Tobacco > Beverages"

        # Call the tool with the partial taxonomy path
        print(
            f"Calling get_manufacturers_by_taxonomy with partial path '{taxonomy_path}'..."
        )
        result = await client.call_tool(
            "get_manufacturers_by_taxonomy", {"taxonomy_path": taxonomy_path}
        )

        # Print results
        print(
            f"Got {len(result.value)} manufacturers for partial taxonomy '{taxonomy_path}'"
        )
        for idx, manufacturer in enumerate(result.value):
            print(
                f"  - Result[{idx}]: {manufacturer['company_name']} | {manufacturer['taxonomy_path']}"
            )

        # Validate the response
        self.assertTrue(isinstance(result.value, list), "Expected a list response")

        # Verify all manufacturers have a taxonomy path that starts with the partial path
        for manufacturer in result.value:
            self.assertTrue(
                manufacturer["taxonomy_path"].startswith(taxonomy_path),
                f"Manufacturer taxonomy path '{manufacturer['taxonomy_path']}' doesn't start with '{taxonomy_path}'",
            )

        return result.value

    def test_get_manufacturers_by_partial_taxonomy(self):
        """Test that we can get manufacturers by partial taxonomy path."""
        manufacturers = self.run_client_test(
            self._test_get_manufacturers_by_partial_taxonomy
        )
        # Note: This test might return 0 manufacturers if no beverages category exists in the CSV
        # So we don't assert anything about the length

    async def _test_get_manufacturers_by_description(self, client):
        """Test getting manufacturers by product description."""
        print("\n--- Testing get_manufacturers_by_description ---")

        # Skip this test if no OpenAI API key is set
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            print(
                "Skipping test_get_manufacturers_by_description - no OPENAI_API_KEY set"
            )
            return None

        # Use a description
        description = "I want to manufacture a chocolate bar with nuts"

        # Call the tool with the description
        print(f"Calling get_manufacturers_by_description with '{description}'...")
        result = await client.call_tool(
            "get_manufacturers_by_description", {"description": description}
        )

        # Print results
        print(f"Result: {result.value}")
        print(f"Classified as taxonomy: '{result.value['taxonomy_path']}'")
        print(f"Found {len(result.value['manufacturers'])} matching manufacturers")

        # Validate the response structure
        self.assertIn(
            "taxonomy_path", result.value, "Missing taxonomy_path in response"
        )
        self.assertIn(
            "manufacturers", result.value, "Missing manufacturers in response"
        )
        self.assertIn("error", result.value, "Missing error field in response")

        return result.value

    def test_get_manufacturers_by_description(self):
        """Test that we can get manufacturers by product description."""
        # Skip this test if no OpenAI API key is set
        if "OPENAI_API_KEY" not in os.environ:
            print(
                "Skipping test_get_manufacturers_by_description - no OPENAI_API_KEY set"
            )
            self.skipTest("OPENAI_API_KEY not set")

        result = self.run_client_test(self._test_get_manufacturers_by_description)
        self.assertIsNotNone(result, "Expected a result")
        self.assertIn("taxonomy_path", result, "Missing taxonomy_path in response")


if __name__ == "__main__":
    unittest.main()
