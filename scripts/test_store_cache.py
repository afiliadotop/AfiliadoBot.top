import sys
import os
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "afiliadohub"))

from dotenv import load_dotenv
load_dotenv()

from api.utils.supabase_client import get_supabase_manager

# Test store cache loading
supabase = get_supabase_manager()
result = supabase.client.table("stores").select("id, name").execute()

print("Stores loaded from Supabase:")
for store in result.data:
    print(f"  - ID {store['id']}: {store['name']}")

# Create cache like the importer does
cache = {store['name'].lower(): store['id'] for store in result.data}
print("\nStore cache (name -> id):")
for name, id in cache.items():
    print(f"  - '{name}' -> {id}")

# Test lookup
print("\nTesting lookup for 'shopee':")
print(f"  Result: {cache.get('shopee', 'NOT FOUND')}")
