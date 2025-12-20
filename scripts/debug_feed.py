
import requests
import pandas as pd
import io
import logging

url = "https://affiliate.shopee.com.br/api/v1/datafeed/download?id=YWJjZGVmZ2hpamtsbW5vcPNcbnfdFhhQkoz1FtnUm6DtED25ejObtofpYLqHBC0h"

try:
    print(f"Downloading {url}...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    content = io.BytesIO(response.content)
    df = pd.read_csv(content, nrows=5)
    
    print("\n--- CSV Columns ---")
    print(list(df.columns))
    
    print("\n--- First Row ---")
    print(df.iloc[0].to_dict())
    
except Exception as e:
    print(f"Error: {e}")
