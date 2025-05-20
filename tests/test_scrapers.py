"""
Unit tests for the Product Trends scrapers.

This module tests the scraper functions by mocking the Apify API interactions.
"""

import os
import json
import unittest
from unittest import mock
from typing import Dict, List, Any

from product_trends_mcp.server import tiktok_hashtag_scraper, insta_hashtag_scraper

# Sample data for mocking Apify responses
SAMPLE_TIKTOK_POSTS = [
    {
        "authorMeta": {
            "name": "sample_user1",
            "nickName": "Sample User 1",
            "following": 100,
            "fans": 1000,
            "heart": 10000,
            "verified": False
        },
        "id": "123456789",
        "text": "Sample TikTok post about #organicfood and #healthysnacks",
        "createTime": 1600000000,
        "likesCount": 1500,
        "commentCount": 75,
        "shareCount": 30,
        "videoUrl": "https://example.com/video1.mp4"
    },
    {
        "authorMeta": {
            "name": "sample_user2",
            "nickName": "Sample User 2",
            "following": 200,
            "fans": 2000,
            "heart": 20000,
            "verified": True
        },
        "id": "234567890",
        "text": "Another sample post about #healthyfood",
        "createTime": 1600001000,
        "likesCount": 2500,
        "commentCount": 125,
        "shareCount": 50,
        "videoUrl": "https://example.com/video2.mp4"
    }
]

SAMPLE_INSTAGRAM_POSTS = [
    {
        "id": "abc123",
        "type": "Image",
        "caption": "Sample Instagram post about #organicfood and #healthysnacks",
        "likesCount": 1200,
        "commentsCount": 45,
        "timestamp": "2021-01-01T12:00:00Z",
        "locationName": "New York, NY",
        "ownerUsername": "sample_insta_user1"
    },
    {
        "id": "def456",
        "type": "Carousel",
        "caption": "Another sample post about #healthyfood",
        "likesCount": 800,
        "commentsCount": 30,
        "timestamp": "2021-01-02T14:00:00Z",
        "locationName": "",
        "ownerUsername": "sample_insta_user2"
    }
]


class MockContext:
    """Mock context for the tool functions."""
    
    def __init__(self):
        self.something = "mock_context"


class MockApifyDataset:
    """Mock class for Apify dataset."""
    
    def __init__(self, items):
        self.items = items
    
    def iterate_items(self):
        """Return the mocked items."""
        return self.items


class MockApifyClient:
    """Mock class for Apify client."""
    
    def __init__(self, token):
        self.token = token
        self.tiktok_posts = SAMPLE_TIKTOK_POSTS
        self.instagram_posts = SAMPLE_INSTAGRAM_POSTS
    
    def actor(self, actor_id):
        """Return self to chain the call."""
        self.actor_id = actor_id
        return self
    
    def call(self, run_input):
        """Mock the call to Apify actor."""
        # Return a mock response with a dataset ID
        return {
            "id": "mock-run-id",
            "defaultDatasetId": "mock-dataset-id"
        }
    
    def dataset(self, dataset_id):
        """Return a mock dataset based on the actor type."""
        if self.actor_id == "GdWCkxBtKWOsKjdch":  # TikTok actor
            return MockApifyDataset(self.tiktok_posts)
        elif self.actor_id == "shu8hvrXbJbY3Eb9W":  # Instagram actor
            return MockApifyDataset(self.instagram_posts)
        else:
            return MockApifyDataset([])


class TestScrapers(unittest.TestCase):
    """Unit tests for the Product Trends scrapers."""
    
    @mock.patch('product_trends_mcp.server.ApifyClient', MockApifyClient)
    @mock.patch('product_trends_mcp.server.APIFY_API_TOKEN', 'test_token')
    async def test_tiktok_hashtag_scraper(self):
        """Test the TikTok hashtag scraper tool."""
        # Call the scraper function
        result = await tiktok_hashtag_scraper(
            hashtags=["organicfood", "healthysnacks"],
            results_per_page=50,
            max_profiles_per_query=5,
            ctx=MockContext()
        )
        
        # Check the result
        self.assertEqual(result["platform"], "TikTok")
        self.assertEqual(result["hashtags"], ["organicfood", "healthysnacks"])
        self.assertEqual(result["results_count"], len(SAMPLE_TIKTOK_POSTS))
        self.assertIn("analysis", result)
        self.assertIn("total_posts", result["analysis"])
        self.assertIn("average_likes", result["analysis"])
        self.assertIn("results", result)
    
    @mock.patch('product_trends_mcp.server.ApifyClient', MockApifyClient)
    @mock.patch('product_trends_mcp.server.APIFY_API_TOKEN', 'test_token')
    async def test_insta_hashtag_scraper(self):
        """Test the Instagram hashtag scraper tool."""
        # Call the scraper function
        result = await insta_hashtag_scraper(
            hashtags=["organicfood", "healthysnacks"],
            results_limit=100,
            ctx=MockContext()
        )
        
        # Check the result
        self.assertEqual(result["platform"], "Instagram")
        self.assertEqual(result["hashtags"], ["organicfood", "healthysnacks"])
        self.assertEqual(result["results_count"], len(SAMPLE_INSTAGRAM_POSTS))
        self.assertIn("analysis", result)
        self.assertIn("total_posts", result["analysis"])
        self.assertIn("average_likes", result["analysis"])
        self.assertIn("results", result)
    
    @mock.patch('product_trends_mcp.server.APIFY_API_TOKEN', '')
    async def test_tiktok_scraper_no_api_token(self):
        """Test TikTok scraper with no API token."""
        # Call the scraper function with no API token
        result = await tiktok_hashtag_scraper(
            hashtags=["organicfood"],
            results_per_page=50,
            max_profiles_per_query=5,
            ctx=MockContext()
        )
        
        # Check the result
        self.assertIn("error", result)
        self.assertEqual(result["hashtags"], ["organicfood"])
        self.assertEqual(result["results"], [])
    
    @mock.patch('product_trends_mcp.server.APIFY_API_TOKEN', '')
    async def test_insta_scraper_no_api_token(self):
        """Test Instagram scraper with no API token."""
        # Call the scraper function with no API token
        result = await insta_hashtag_scraper(
            hashtags=["organicfood"],
            results_limit=100,
            ctx=MockContext()
        )
        
        # Check the result
        self.assertIn("error", result)
        self.assertEqual(result["hashtags"], ["organicfood"])
        self.assertEqual(result["results"], [])


if __name__ == "__main__":
    unittest.main() 