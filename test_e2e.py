import requests
import time
import json
import sys

BASE_URL = "http://localhost:8000/api"

def test_campaign_generation():
    print("🚀 Starting End-to-End Campaign Generation Test...")
    
    brief = {
        "businessName": "AeroTech Solutions",
        "productName": "AeroFlow 3000",
        "productDescription": "A next-generation enterprise drone system for automated inventory management in large warehouses.",
        "targetAudience": "Warehouse Managers, Supply Chain Directors, and Logistics Executives in Fortune 500 companies.",
        "goals": ["Generate high-quality B2B leads", "Establish market dominance in automated drone inventory"],
        "budget": 50000,
        "duration": "3 months",
        "tone": "Professional, Innovative, and Trustworthy"
    }

    try:
        # Step 1: Submit Campaign
        print("📝 Submitting campaign brief...")
        res = requests.post(f"{BASE_URL}/campaigns", json=brief)
        res.raise_for_status()
        data = res.json()
        task_id = data["taskId"]
        print(f"✅ Campaign submitted. Task ID: {task_id}")

        # Step 2: Poll Status
        print("⏳ Polling task status (Waiting for 5 Agents)...")
        while True:
            time.sleep(3)
            status_res = requests.get(f"{BASE_URL}/tasks/{task_id}")
            status_res.raise_for_status()
            status_data = status_res.json()
            
            progress = status_data.get("progress", 0)
            status = status_data.get("status", "pending")
            msg = status_data.get("message", "")
            
            print(f"   [{status.upper()}] Progress: {progress}% - {msg}")
            
            if status == "completed":
                print("🎉 Task completed successfully!")
                break
            elif status == "failed":
                print(f"❌ Task failed: {status_data.get('error_message')}")
                sys.exit(1)

        # Step 3: Fetch Results
        print("📥 Fetching final content output...")
        content_res = requests.get(f"{BASE_URL}/campaigns/{task_id}/content")
        content_res.raise_for_status()
        content = content_res.json()
        
        # Save output to a file to show the user
        with open("e2e_test_output.json", "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2)
            
        print("✅ Success! Output saved to e2e_test_output.json")
        
    except Exception as e:
        print(f"💥 Error during test: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_campaign_generation()
