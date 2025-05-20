# Product Trends Expert Client Examples

This directory contains example clients that demonstrate how to interact with the Product Trends Expert MCP server.

## Prerequisites

- The Product Trends Expert server should be running (see main README for instructions)
- Required Python packages should be installed
- An Apify API token for accessing TikTok and Instagram data

## Client Examples

### 1. Using FastMCP Client (`product_trends_client.py`)

This client uses the official FastMCP Python client library to interact with the server.

#### Installation

```bash
pip install fastmcp apify-client
```

#### Running the Example

```bash
python examples/product_trends_client.py
```

If you want to specify a custom product:

```bash
python examples/product_trends_client.py --product "dark chocolate almonds"
```

The script will:

- Convert the product name to relevant hashtags
- Connect to the server (default: http://localhost:8000)
- Fetch and analyze TikTok hashtag data
- Fetch and analyze Instagram hashtag data
- Save a sample of the results to a JSON file

### 2. Multi-Expert Agent Example (`multi_expert_agent.py`)

This example demonstrates how to use multiple MCP experts together to create a comprehensive workflow:

1. Contract Manufacturer Expert - to find suitable manufacturers
2. Product Trends Expert - to research product hashtags and trends
3. Email Expert - to reach out to potential manufacturers

#### Installation

```bash
pip install fastmcp apify-client
```

#### Running the Example

```bash
# Make sure you have the sample product file
python examples/multi_expert_agent.py
```

Or with a custom product file:

```bash
python examples/multi_expert_agent.py --product "path/to/your/product.md"
```

The agent will:

- Parse the product information from the markdown file
- Find suitable contract manufacturers
- Research social media trends for the product
- Draft personalized emails to manufacturers
- Save a final report with all the collected information

## Configuration

Both scripts require:

- An Apify API token set in your `.env` file or environment variables:
  ```
  APIFY_API_TOKEN=your_apify_api_token
  ```

## Customization

Both scripts connect to `http://localhost:8000` by default. To use a different server address or port, modify the client connection in the scripts.

## Example API Tools

The Product Trends Expert provides these main tools:

1. **TikTok Hashtag Scraper**

   - Scrapes TikTok for specified hashtags
   - Analyzes engagement metrics like likes, comments, shares
   - Returns trending content related to product categories

2. **Instagram Hashtag Scraper**
   - Scrapes Instagram for specified hashtags
   - Analyzes engagement metrics and location data
   - Returns trending posts related to product categories
