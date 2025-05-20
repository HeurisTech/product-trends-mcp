# Product Trends MCP Server

A production-ready MCP server providing tools to analyze product trends on social media platforms like TikTok and Instagram.

## Features

- TikTok hashtag scraping and trend analysis
- Instagram hashtag scraping and trend analysis
- Social engagement metrics and analytics
- Support for multiple hashtags in a single request
- Result filtering and pagination
- RESTful resource endpoints for integration with other systems
- Comprehensive logging
- Configurable through environment variables

## Installation

### Local Development

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd mcp-servers/trends-inspiration
   ```

2. Create and activate a virtual environment:

   ```bash
   uv init
   uv venv
   uv sync
   ```

3. Create a `.env` file from the example:

   ```bash
   cp example.env .env
   ```

4. Set your Apify API token in the `.env` file:

   ```
   APIFY_API_TOKEN=your_apify_api_token_here
   ```

5. Run using inspector

   ```zsh
   npx @modelcontextprotocol/inspector uv run --with fastmcp /Users/user/Desktop/fl100/contract-sourcing/mcp-servers/trends-inspiration/src/product_trends_mcp/server.py
   ```

## Test using config

```json
{
  "mcpServers": {
    "product-trends-mcp": {
      "command": "/opt/homebrew/bin/uv",
      "description": "Search for trends on tiktok and instagram (uses apify)",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/trends-inspiration/src/product_trends_mcp",
        "run",
        "--with",
        "fastmcp",
        "server.py"
      ],
      "env": {
         "APIFY_API_KEY": "<YOUR_APIFY_KEY>"
       }
    }
  }
}
```


### With Environment Variables

Set additional environment variables when starting the server:

```bash
APIFY_API_TOKEN=your_key_here python -m product_trends_mcp.server
```

This starts the server and opens a web interface for testing the tools and endpoints. The first method is preferred for development as it provides the interactive MCP Inspector UI.

## Configuration

The server can be configured using environment variables:

- `APIFY_API_TOKEN`: Your Apify API token (required for scraping social media)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)
- `DEBUG`: Enable debug mode (true/false)

## API Tools

The server provides the following tools:

- `tiktok_hashtag_scraper`: Scrapes TikTok hashtags to analyze trends related to products
- `insta_hashtag_scraper`: Scrapes Instagram hashtags to analyze trends related to products

## Resource Endpoints

The server provides the following resource endpoints:

- `trends://{platform}/{hashtag}`: Gets trend information for a specific platform and hashtag

## Example Client Usage

```python
from mcp.client import MCPClient

client = MCPClient()

# Scrape TikTok hashtags
tiktok_results = client.call_tool("productTrendsExpert.tiktok_hashtag_scraper",
                           hashtags=["organicfood", "healthysnacks"],
                           results_per_page=50,
                           max_profiles_per_query=5)

# Scrape Instagram hashtags
insta_results = client.call_tool("productTrendsExpert.insta_hashtag_scraper",
                                hashtags=["organicfood", "healthysnacks"],
                                results_limit=100)

# Access a resource endpoint
trend_resource = client.get_resource("productTrendsExpert.trends://tiktok/organicfood")
```

## License

[MIT](LICENSE)
