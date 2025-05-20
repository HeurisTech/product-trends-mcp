#!/usr/bin/env python
"""
FastMCP Client Example for Contract Manufacturers Server

This script demonstrates how to access all endpoints of the Contract Manufacturers MCP server
using the FastMCP client library. It includes sample queries for each endpoint.

Usage:
    python client_examples.py

Prerequisites:
    - The Contract Manufacturers MCP server should be running
    - The fastmcp package should be installed
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional, List

from fastmcp import Client


# Server connection settings
SERVER_URL = "http://localhost:8000"  # Change this if using a different port
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # For description-based matching


async def print_result(description: str, result: Any):
    """Print results in a formatted way."""
    print(f"\n=== {description} ===")

    if hasattr(result, "value"):
        # If it's a tool result, get the value
        value = result.value
    else:
        # Otherwise use the result directly
        value = result

    if isinstance(value, list):
        print(f"Found {len(value)} results:")
        for i, item in enumerate(value[:3]):  # Show only first 3 items for brevity
            print(f"  {i+1}. {json.dumps(item, indent=2)}")
        if len(value) > 3:
            print(f"  ... plus {len(value) - 3} more items")
    else:
        print(json.dumps(value, indent=2))


async def demonstrate_tool_calls(client: Client):
    """Demonstrate all tool calls with example queries."""

    # 1. List all manufacturers
    all_manufacturers = await client.call_tool("list_all_manufacturers")
    await print_result("All Manufacturers (First 3)", all_manufacturers)

    # Get the first manufacturer for subsequent queries
    first_manufacturer = (
        all_manufacturers.value[0]["company_name"]
        if all_manufacturers.value
        else "Example Co"
    )

    # 2. Get manufacturer by name
    manufacturer = await client.call_tool(
        "get_manufacturer_by_name", {"company_name": first_manufacturer}
    )
    await print_result(f"Manufacturer by Name: '{first_manufacturer}'", manufacturer)

    # 3. Filter manufacturers by category
    category_results = await client.call_tool(
        "filter_manufacturers_by_category", {"category": "beverage"}
    )
    await print_result("Manufacturers in 'beverage' Category", category_results)

    # 4. Search manufacturers
    search_results = await client.call_tool(
        "search_manufacturers", {"query": "organic"}
    )
    await print_result("Search Results for 'organic'", search_results)

    # 5. Get manufacturer requirements
    requirements = await client.call_tool(
        "get_manufacturer_requirements", {"company_name": first_manufacturer}
    )
    await print_result(f"Requirements for '{first_manufacturer}'", requirements)

    # 6. Get manufacturers by requirement
    requirement_results = await client.call_tool(
        "get_manufacturers_by_requirement", {"requirement": "packaging"}
    )
    await print_result(
        "Manufacturers with 'packaging' Requirement", requirement_results
    )

    # 7. Get manufacturers by taxonomy
    taxonomy_results = await client.call_tool(
        "get_manufacturers_by_taxonomy",
        {"taxonomy_path": "Food, Beverages & Tobacco > Beverages"},
    )
    await print_result("Manufacturers with 'Beverages' Taxonomy", taxonomy_results)

    # 8. Get manufacturers by description
    # Skip if no OpenAI API key is set
    if OPENAI_API_KEY:
        description_results = await client.call_tool(
            "get_manufacturers_by_description",
            {"description": "I want to make a protein bar with nuts and chocolate"},
        )
        await print_result(
            "Manufacturers Matching Product Description", description_results
        )
    else:
        print("\n=== Manufacturers Matching Product Description ===")
        print("Skipped: OpenAI API key not set")

    # 9. Reload manufacturers data
    # NOTE: This is commented out as it's typically not needed in normal client operations
    # reload_results = await client.call_tool("reload_manufacturers_data")
    # await print_result("Reload Manufacturers Data", reload_results)


async def demonstrate_resource_access(client: Client):
    """Demonstrate accessing resource endpoints."""

    # 1. Get all manufacturers from catalog
    catalog = await client.get_resource("manufacturers://catalog")
    await print_result("Complete Manufacturers Catalog", catalog)

    # Get a manufacturer name from the catalog
    manufacturer_name = (
        catalog["manufacturers"][0]["company_name"]
        if catalog["manufacturers"]
        else "Example Co"
    )

    # 2. Get a specific manufacturer by name
    manufacturer = await client.get_resource(f"manufacturer://{manufacturer_name}")
    await print_result(f"Manufacturer Resource: {manufacturer_name}", manufacturer)

    # 3. Get manufacturers by taxonomy path
    taxonomy_manufacturers = await client.get_resource(
        "manufacturers://taxonomy/Food, Beverages & Tobacco > Beverages"
    )
    await print_result("Taxonomy Resource: Beverages", taxonomy_manufacturers)


async def main():
    """Main function to run all examples."""
    print(f"Connecting to server at {SERVER_URL}")

    try:
        async with Client(SERVER_URL) as client:
            # List available tools on the server
            tools = await client.list_tools()
            print(f"Available tools on server: {', '.join(tools)}")

            # Demonstrate tool calls
            await demonstrate_tool_calls(client)

            # Demonstrate resource access
            await demonstrate_resource_access(client)

    except Exception as e:
        print(f"Error connecting to server: {e}")
        print(f"Make sure the server is running at {SERVER_URL}")


if __name__ == "__main__":
    # Set up pretty printing for JSON
    try:
        import pygments
        from pygments.lexers import JsonLexer
        from pygments.formatters import TerminalFormatter

        # Override the json.dumps to add syntax highlighting
        _original_dumps = json.dumps

        def _highlighted_dumps(obj, *args, **kwargs):
            formatted = _original_dumps(obj, *args, **kwargs)
            return pygments.highlight(
                formatted, JsonLexer(), TerminalFormatter()
            ).strip()

        if os.isatty(1):  # Only apply highlighting if output is to a terminal
            json.dumps = _highlighted_dumps
    except ImportError:
        # If pygments is not available, just use normal JSON formatting
        pass

    asyncio.run(main())
