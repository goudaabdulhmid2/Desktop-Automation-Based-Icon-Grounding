import requests
import json
from pathlib import Path
from typing import List, Dict
import config
from utils.logger import setup_logger
from utils.retry import retry_on_exception

logger = setup_logger(__name__)


class PostAPIClient:
    """
    Client for fetching blog posts from JSONPlaceholder API.
    Falls back to local data if API is unavailable.
    """
    
    def __init__(self, api_url: str = None, timeout: int = None):
        """
        Initialize API client.
        
        Args:
            api_url: API endpoint URL
            timeout: Request timeout in seconds
        """
        self.api_url = api_url or config.API_URL
        self.timeout = timeout or config.API_TIMEOUT
        self.fallback_data_path = Path(__file__).parent / "fallback_data.json"
        
        logger.info(f"API Client initialized: {self.api_url}")
    
    @retry_on_exception(max_attempts=2, delay=1, exceptions=(requests.RequestException,))
    def fetch_posts(self, count: int = None) -> List[Dict]:
        """
        Fetch blog posts from API.
        
        Args:
            count: Number of posts to fetch
        
        Returns:
            List of post dictionaries
        """
        count = count or config.POSTS_COUNT
        
        logger.info(f"Fetching {count} posts from API...")
        
        try:
            response = requests.get(self.api_url, timeout=self.timeout)
            response.raise_for_status()
            
            posts = response.json()[:count]
            logger.info(f"✓ Successfully fetched {len(posts)} posts from API")
            
            return posts
            
        except requests.RequestException as e:
            logger.warning(f"API request failed: {e}")
            raise  # Let retry decorator handle it
    
    def fetch_posts_with_fallback(self, count: int = None) -> List[Dict]:
        """
        Fetch posts from API with automatic fallback to local data.
        
        Args:
            count: Number of posts to fetch
        
        Returns:
            List of post dictionaries
        """
        count = count or config.POSTS_COUNT
        
        try:
            return self.fetch_posts(count)
        except Exception as e:
            logger.warning(f"API unavailable after retries: {e}")
            logger.info("Falling back to local data...")
            return self.load_fallback_data(count)
    
    def load_fallback_data(self, count: int = None) -> List[Dict]:
        """
        Load posts from local fallback JSON file.
        
        Args:
            count: Number of posts to load
        
        Returns:
            List of post dictionaries
        """
        count = count or config.POSTS_COUNT
        
        if not self.fallback_data_path.exists():
            logger.error(f"Fallback data not found: {self.fallback_data_path}")
            raise FileNotFoundError(f"Fallback data missing: {self.fallback_data_path}")
        
        logger.info(f"Loading fallback data from: {self.fallback_data_path}")
        
        with open(self.fallback_data_path, 'r', encoding='utf-8') as f:
            posts = json.load(f)[:count]
        
        logger.info(f"✓ Loaded {len(posts)} posts from fallback data")
        return posts
    
    def validate_post(self, post: Dict) -> bool:
        """
        Validate that a post has required fields.
        
        Args:
            post: Post dictionary to validate
        
        Returns:
            True if post is valid
        """
        required_fields = ['id', 'title', 'body']
        
        for field in required_fields:
            if field not in post:
                logger.warning(f"Post missing required field: {field}")
                return False
        
        return True
    
    def validate_posts(self, posts: List[Dict]) -> List[Dict]:
        """
        Filter posts to only valid ones.
        
        Args:
            posts: List of post dictionaries
        
        Returns:
            List of valid posts
        """
        valid_posts = [post for post in posts if self.validate_post(post)]
        
        if len(valid_posts) < len(posts):
            logger.warning(
                f"Filtered out {len(posts) - len(valid_posts)} invalid posts"
            )
        
        return valid_posts
    
    def format_post_content(self, post: Dict) -> str:
        """
        Format post for writing to file.
        
        Args:
            post: Post dictionary
        
        Returns:
            Formatted string
        """
        return f"Title: {post['title']}\n\n{post['body']}"
    
    def get_post_filename(self, post: Dict) -> str:
        """
        Generate filename for post.
        
        Args:
            post: Post dictionary
        
        Returns:
            Filename string
        """
        return f"post_{post['id']}.txt"


def create_fallback_data():
    """
    Create fallback_data.json from the uploaded data.json.
    This is a utility function for setup.
    """
    # Check if data.json exists in uploads
    uploads_data = Path("/mnt/user-data/uploads/data.json")
    fallback_path = Path(__file__).parent / "fallback_data.json"
    
    if uploads_data.exists():
        import shutil
        shutil.copy(uploads_data, fallback_path)
        logger.info(f"Created fallback data: {fallback_path}")
    else:
        logger.warning("data.json not found in uploads")


if __name__ == "__main__":
    # Test API client
    client = PostAPIClient()
    
    print("Testing API client...")
    
    try:
        posts = client.fetch_posts_with_fallback(count=3)
        print(f"\nFetched {len(posts)} posts:")
        
        for post in posts:
            print(f"\nPost {post['id']}:")
            print(f"Title: {post['title']}")
            print(f"Content: {client.format_post_content(post)[:100]}...")
            print(f"Filename: {client.get_post_filename(post)}")
    
    except Exception as e:
        print(f"Error: {e}")
