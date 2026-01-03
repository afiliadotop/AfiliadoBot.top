import os
import sys
from dotenv import load_dotenv

# Add paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "afiliadohub"))

load_dotenv()

def check_supabase():
    try:
        from supabase import create_client
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        if not url or not key:
            return "MISSING_CREDS"
            
        client = create_client(url, key)
        count = client.table("products").select("id", count="exact").execute().count
        return f"OK ({count} products)"
    except Exception as e:
        return f"ERROR: {str(e)}"

def check_telegram():
    try:
        import requests
        token = os.getenv('BOT_TOKEN')
        if not token:
            return "MISSING_TOKEN"
            
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if response.status_code == 200 and data.get('ok'):
            return f"OK (@{data['result']['username']})"
        else:
            return f"INVALID: {data.get('description', 'Unknown error')}"
    except Exception as e:
        return f"ERROR: {str(e)}"

def check_stores():
    try:
        from supabase import create_client
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        if not url or not key:
            return "MISSING_CREDS"
            
        client = create_client(url, key)
        res = client.table("stores").select("name").execute()
        stores = [s['name'] for s in res.data]
        return f"OK ({len(stores)} stores: {', '.join(stores)})"
    except Exception as e:
        return f"ERROR: {str(e)}"

if __name__ == "__main__":
    print("-" * 30)
    print("PROJECT STATUS CHECK")
    print("-" * 30)
    print(f"Supabase DB: {check_supabase()}")
    print(f"Stores:      {check_stores()}")
    print(f"Telegram Bot: {check_telegram()}")
    print("-" * 30)
