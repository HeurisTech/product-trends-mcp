#!/usr/bin/env python
"""
HTTP Client Example for Contract Manufacturers Server

This script demonstrates how to access all endpoints of the Contract Manufacturers MCP server
using direct HTTP requests with the requests library, without relying on the FastMCP client.
It includes sample queries for each endpoint.

Usage:
    python http_client_examples.py

Prerequisites:
    - The Contract Manufacturers MCP server should be running
    - The requests package should be installed (pip install requests)
"""

import json
import os
import sys
from pprint import pprint

import requests

# Server connection settings
SERVER_URL = "http://localhost:8000"  # Change this if using a different port
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # For description-based matching


def print_result(description, result):
    """Print results in a formatted way."""
    print(f"\n=== {description} ===")

    if isinstance(result, list):
        print(f"Found {len(result)} results:")
        for i, item in enumerate(result[:3]):  # Show only first 3 items for brevity
            print(f"  {i+1}.")
            pprint(item)
        if len(result) > 3:
            print(f"  ... plus {len(result) - 3} more items")
    else:
        pprint(result)


def call_tool(tool_name, params=None):
    """Call a tool on the MCP server."""
    url = f"{SERVER_URL}/tools/{tool_name}"
    headers = {"Content-Type": "application/json"}

    try:
        if params:
            response = requests.post(url, json=params, headers=headers)
        else:
            response = requests.post(url, headers=headers)

        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling tool '{tool_name}': {e}")
        return None


def get_resource(resource_uri):
    """Get a resource from the MCP server."""
    # Convert MCP resource URI to HTTP path
    # Example: manufacturer://Example%20Co -> /resources/manufacturer/Example%20Co
    parts = resource_uri.split("://", 1)
    if len(parts) != 2:
        print(f"Invalid resource URI: {resource_uri}")
        return None

    resource_type, resource_path = parts
    url = f"{SERVER_URL}/resources/{resource_type}/{resource_path}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting resource '{resource_uri}': {e}")
        return None


def demonstrate_tool_calls():
    """Demonstrate all tool calls with example queries."""

    # 1. List all manufacturers
    all_manufacturers = call_tool("list_all_manufacturers")
    print_result("All Manufacturers (First 3)", all_manufacturers)

    # Get the first manufacturer for subsequent queries
    first_manufacturer = (
        all_manufacturers[0]["company_name"] if all_manufacturers else "Example Co"
    )

    # 2. Get manufacturer by name
    manufacturer = call_tool(
        "get_manufacturer_by_name", {"company_name": first_manufacturer}
    )
    print_result(f"Manufacturer by Name: '{first_manufacturer}'", manufacturer)

    # 3. Filter manufacturers by category
    category_results = call_tool(
        "filter_manufacturers_by_category", {"category": "beverage"}
    )
    print_result("Manufacturers in 'beverage' Category", category_results)

    # 4. Search manufacturers
    search_results = call_tool("search_manufacturers", {"query": "organic"})
    print_result("Search Results for 'organic'", search_results)

    # 5. Get manufacturer requirements
    requirements = call_tool(
        "get_manufacturer_requirements", {"company_name": first_manufacturer}
    )
    print_result(f"Requirements for '{first_manufacturer}'", requirements)

    # 6. Get manufacturers by requirement
    requirement_results = call_tool(
        "get_manufacturers_by_requirement", {"requirement": "packaging"}
    )
    print_result("Manufacturers with 'packaging' Requirement", requirement_results)

    # 7. Get manufacturers by taxonomy
    taxonomy_results = call_tool(
        "get_manufacturers_by_taxonomy",
        {"taxonomy_path": "Food, Beverages & Tobacco > Beverages"},
    )
    print_result("Manufacturers with 'Beverages' Taxonomy", taxonomy_results)

    # 8. Get manufacturers by description
    # Skip if no OpenAI API key is set
    if OPENAI_API_KEY:
        description_results = call_tool(
            "get_manufacturers_by_description",
            {"description": "I want to make a protein bar with nuts and chocolate"},
        )
        print_result("Manufacturers Matching Product Description", description_results)
    else:
        print("\n=== Manufacturers Matching Product Description ===")
        print("Skipped: OpenAI API key not set")


def demonstrate_resource_access():
    """Demonstrate accessing resource endpoints."""

    # 1. Get all manufacturers from catalog
    catalog = get_resource("manufacturers://catalog")
    print_result("Complete Manufacturers Catalog", catalog)

    # Get a manufacturer name from the catalog
    manufacturer_name = (
        catalog["manufacturers"][0]["company_name"]
        if catalog and "manufacturers" in catalog and catalog["manufacturers"]
        else "Example Co"
    )

    # 2. Get a specific manufacturer by name
    manufacturer = get_resource(f"manufacturer://{manufacturer_name}")
    print_result(f"Manufacturer Resource: {manufacturer_name}", manufacturer)

    # 3. Get manufacturers by taxonomy path
    # Note: We need to encode spaces and special characters in the path
    import urllib.parse

    taxonomy_path = urllib.parse.quote("Food, Beverages & Tobacco > Beverages")
    taxonomy_manufacturers = get_resource(f"manufacturers://taxonomy/{taxonomy_path}")
    print_result("Taxonomy Resource: Beverages", taxonomy_manufacturers)


def list_available_tools():
    """List all available tools on the server."""
    try:
        response = requests.get(f"{SERVER_URL}/tools")
        response.raise_for_status()
        tools = response.json()
        print("Available tools on server:")
        for tool in tools:
            print(f"  - {tool}")
        return tools
    except requests.exceptions.RequestException as e:
        print(f"Error listing tools: {e}")
        return []


def main():
    """Main function to run all examples."""
    print(f"Connecting to server at {SERVER_URL}")

    try:
        # Check if server is running by listing tools
        tools = list_available_tools()
        if not tools:
            print(f"Could not connect to server at {SERVER_URL}")
            return

        # Demonstrate tool calls
        demonstrate_tool_calls()

        # Demonstrate resource access
        demonstrate_resource_access()

    except Exception as e:
        print(f"Error: {e}")
        print(f"Make sure the server is running at {SERVER_URL}")


if __name__ == "__main__":
    main()
