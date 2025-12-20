
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"URL: {url}")
print(f"KEY: {key[:10]}..." if key else "KEY: None")

try:
    print("Attempting connection...")
    supabase: Client = create_client(url, key)
    response = supabase.table("products").select("count", count="exact").execute()
    print("✅ Connection Successful!")
    print(f"Count: {response.count}")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
