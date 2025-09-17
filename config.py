import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

#fetching the values from environment variables
API_KEY = os.getenv("AIRTABLE_ACCESS_TOKEN")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")