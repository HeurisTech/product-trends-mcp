"""
Product Trends MCP Server

Provides tools to search and analyze product trends on social media platforms.
"""

import json
import logging
import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Any

import httpx
import uvicorn
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from apify_client import ApifyClient

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("product-trends-mcp")

# Configuration
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")
if not APIFY_API_TOKEN:
    logger.warning("APIFY_API_TOKEN not set. API calls will fail.")

# Create server
mcp = FastMCP(
    "Product Trends Expert",
    version="0.1.0",
    description="Access and analyze product trends on social media platforms",
)

# Initialize Apify client
apify_client = ApifyClient(APIFY_API_TOKEN)

# Define result schema for documentation
TREND_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "platform": {"type": "string"},
        "hashtag": {"type": "string"},
        "post_count": {"type": "integer"},
        "top_posts": {"type": "array", "items": {"type": "object"}},
        "engagement_metrics": {"type": "object"},
    },
}


@mcp.tool()
async def tiktok_hashtag_scraper(
    hashtags: List[str],
    results_per_page: int = 100,
    max_profiles_per_query: int = 10,
    ctx: Context
) -> Dict[str, Any]:
    """
    Scrape TikTok hashtags to analyze trends related to products.
    
    Args:
        hashtags: List of hashtags to scrape (without the # symbol)
        results_per_page: Number of results to fetch per page
        max_profiles_per_query: Maximum number of profiles to analyze per query
        
    Returns:
        Dictionary containing scraped hashtag data and analysis
    """
    logger.info(f"tiktok_hashtag_scraper called with hashtags: {hashtags}")
    
    if not APIFY_API_TOKEN:
        return {
            "error": "APIFY_API_TOKEN not set. Cannot scrape TikTok hashtags.",
            "hashtags": hashtags,
            "results": []
        }
    
    try:
        # Prepare the Actor input
        run_input = {
            "hashtags": hashtags,
            "resultsPerPage": results_per_page,
            "profileScrapeSections": ["videos"],
            "profileSorting": "latest",
            "excludePinnedPosts": False,
            "searchSection": "",
            "maxProfilesPerQuery": max_profiles_per_query,
            "shouldDownloadVideos": False,
            "shouldDownloadCovers": False,
            "shouldDownloadSubtitles": False,
            "shouldDownloadSlideshowImages": False,
            "shouldDownloadAvatars": False,
            "shouldDownloadMusicCovers": False,
            "proxyCountryCode": "None",
        }
        
        # Run the Actor and wait for it to finish
        run = apify_client.actor("GdWCkxBtKWOsKjdch").call(run_input=run_input)
        
        # Fetch the results
        results = []
        for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)
            
        # Analyze the results
        analysis = {
            "total_posts": len(results),
            "average_likes": sum(post.get("likesCount", 0) for post in results) / max(len(results), 1),
            "average_comments": sum(post.get("commentCount", 0) for post in results) / max(len(results), 1),
            "average_shares": sum(post.get("shareCount", 0) for post in results) / max(len(results), 1),
        }
        
        return {
            "platform": "TikTok",
            "hashtags": hashtags,
            "results_count": len(results),
            "results": results[:10],  # Return only first 10 results to avoid overwhelming response
            "analysis": analysis,
            "full_results_count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error scraping TikTok hashtags: {str(e)}")
        return {
            "error": f"Failed to scrape TikTok hashtags: {str(e)}",
            "hashtags": hashtags,
            "results": []
        }


@mcp.tool()
async def insta_hashtag_scraper(
    hashtags: List[str],
    results_limit: int = 200,
    ctx: Context
) -> Dict[str, Any]:
    """
    Scrape Instagram hashtags to analyze trends related to products.
    
    Args:
        hashtags: List of hashtags to scrape (without the # symbol)
        results_limit: Maximum number of results to fetch
        
    Returns:
        Dictionary containing scraped hashtag data and analysis
    """
    logger.info(f"insta_hashtag_scraper called with hashtags: {hashtags}")
    
    if not APIFY_API_TOKEN:
        return {
            "error": "APIFY_API_TOKEN not set. Cannot scrape Instagram hashtags.",
            "hashtags": hashtags,
            "results": []
        }
    
    try:
        # Format hashtags for Instagram URL format
        hashtag_urls = [f"https://www.instagram.com/explore/tags/{hashtag}/" for hashtag in hashtags]
        
        # Prepare the Actor input
        run_input = {
            "directUrls": hashtag_urls,
            "resultsType": "posts",
            "resultsLimit": results_limit,
            "searchType": "hashtag",
            "searchLimit": len(hashtags),
            "addParentData": False,
        }
        
        # Run the Actor and wait for it to finish
        run = apify_client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input)
        
        # Fetch the results
        results = []
        for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)
            
        # Analyze the results
        analysis = {
            "total_posts": len(results),
            "average_likes": sum(post.get("likesCount", 0) for post in results) / max(len(results), 1),
            "average_comments": sum(post.get("commentsCount", 0) for post in results) / max(len(results), 1),
            "posts_with_location": sum(1 for post in results if post.get("locationName")),
        }
        
        return {
            "platform": "Instagram",
            "hashtags": hashtags,
            "results_count": len(results),
            "results": results[:10],  # Return only first 10 results to avoid overwhelming response
            "analysis": analysis,
            "full_results_count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error scraping Instagram hashtags: {str(e)}")
        return {
            "error": f"Failed to scrape Instagram hashtags: {str(e)}",
            "hashtags": hashtags,
            "results": []
        }


@mcp.resource("trends://{platform}/{hashtag}")
def trend_resource(platform: str, hashtag: str) -> Dict[str, Any]:
    """
    Get trend information for a specific platform and hashtag.

    Args:
        platform: The social media platform (e.g., 'tiktok', 'instagram')
        hashtag: The hashtag to analyze

    Returns:
        Trend information or error if not found
    """
    logger.info(f"trend_resource accessed with platform: {platform}, hashtag: {hashtag}")
    
    if platform.lower() not in ["tiktok", "instagram"]:
        return {"error": f"Unsupported platform: {platform}"}
    
    # This is a placeholder. In a real implementation, this would fetch cached results
    # or trigger a new scrape
    return {
        "platform": platform,
        "hashtag": hashtag,
        "message": "Use the tiktok_hashtag_scraper or insta_hashtag_scraper tools to get actual data"
    }


def main():
    """Entry point for the server."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Product Trends MCP Server")
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to run the server on"
    )
    args = parser.parse_args()

    logger.info(f"Starting Product Trends MCP Server on port {args.port}")

    # Use a workaround to set port by setting environment variables that uvicorn will use
    os.environ["FASTMCP_HOST"] = "0.0.0.0"  # Bind to all interfaces
    os.environ["FASTMCP_PORT"] = str(args.port)

    # Run the server
    mcp.run()


if __name__ == "__main__":
    main() 