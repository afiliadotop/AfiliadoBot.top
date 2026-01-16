import sys
import os
import time
import requests
import subprocess
from datetime import datetime

# Configuration
API_URL = "http://127.0.0.1:8000"
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def log(message, type="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    color = "\033[94m" if type == "INFO" else "\033[92m" if type == "SUCCESS" else "\033[91m"
    reset = "\033[0m"
    print(f"{color}[{type}] {timestamp} - {message}{reset}")

def check_backend():
    log("Checking Backend API...", "INFO")
    try:
        # Check Root/Health
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            log(f"Backend is reachable: {response.json()}", "SUCCESS")
        else:
            log(f"Backend unreachable (Status: {response.status_code})", "ERROR")
            return False

        # Check Database/Products (if endpoints exist)
        try:
            # Assuming there is a public or protected endpoint we can hit. 
            # If protected, we'd need to mock login, but let's try a public one or docs
            response = requests.get(f"{API_URL}/docs")
            if response.status_code == 200:
                log("API Documentation (Swagger) is accessible", "SUCCESS")
            
            # Try to fetch products (public endpoint usually)
            # You might need to adjust this endpoint based on your actual API routes
            # api/products usually
            response = requests.get(f"{API_URL}/products") 
            # If 401/403, it means Auth is working at least. 
            if response.status_code in [200, 401, 403]: 
                log(f"Products endpoint responded (Status: {response.status_code})", "SUCCESS")
            else:
                log(f"Products endpoint weird response: {response.status_code}", "WARNING")

        except Exception as e:
            log(f"Failed to check specific endpoints: {e}", "WARNING")
            
        return True
    except requests.ConnectionError:
        log("Backend Connection Refused. Is it running on port 8000?", "ERROR")
        return False

def check_frontend_build():
    log("Checking Frontend Build Integrity...", "INFO")
    try:
        # Run npm run build to check for TS/Vite errors
        # Use shell=True for Windows compatibility with npm
        result = subprocess.run(["npm", "run", "build"], cwd=FRONTEND_DIR, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            log("Frontend Build SUCCESS", "SUCCESS")
            return True
        else:
            log("Frontend Build FAILED", "ERROR")
            print("--- Build Error Log ---")
            print(result.stderr)
            return False
    except Exception as e:
        log(f"Failed to run frontend build: {e}", "ERROR")
        return False

def verify_system():
    print("========================================")
    print("   AFILIADOBOT SYSTEM VERIFICATION      ")
    print("========================================")
    
    backend_ok = check_backend()
    frontend_ok = check_frontend_build()
    
    print("\n========================================")
    print("           VERIFICATION RESULT          ")
    print("========================================")
    
    if backend_ok and frontend_ok:
        log("SYSTEM STATUS: OPERATIONAL 🟢", "SUCCESS")
        print("\nYour system appears to be correctly integrated.")
        print("- Backend is accepting connections.")
        print("- Frontend compiles without errors.")
    else:
        log("SYSTEM STATUS: ISSUES DETECTED 🔴", "ERROR")
        if not backend_ok:
            print("- FIX: Ensure backend is running (`npm run backend`)")
        if not frontend_ok:
            print("- FIX: Check frontend console errors (`npm run dev`)")

if __name__ == "__main__":
    verify_system()
