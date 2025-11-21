"""
Configuration file for the self-improving Amazon scraper
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Number of iterations to run
NUM_ITERATIONS = int(os.getenv("NUM_ITERATIONS", "3"))

# Amazon product page URL to scrape
AMAZON_URL = os.getenv(
    "AMAZON_URL",
    "https://www.amazon.com/blackfriday?ref_=nav_cs_td_bf_dt_cr"  # Example product page
)

# Fields to extract from Amazon product pages
FIELDS_TO_EXTRACT = [
    "product_name",
    "price",
    "description",
    "ratings",
    "reviews"
]

# Pattern storage file
PATTERNS_FILE = "patterns.json"

# Claude API Key (should be set as environment variable)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

