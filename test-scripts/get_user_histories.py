import asyncio
import json
import aiohttp
from pathlib import Path

# Config
BASE_URL = "https://travelplanner.ddns.net/user-history"
USER_IDS = list(range(125003, 125023))  # 125003-125022 inclusive (20 users)
OUTPUT_FILE = Path("user_histories.json")

async def get_user_history(session, user_id):
    """Get user history for a single user"""
    try:
        url = f"{BASE_URL}?user_id={user_id}"
        async with session.get(url, timeout=30) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✓ Retrieved history for user {user_id}")
                return user_id, data
            else:
                error_text = await response.text()
                print(f"✗ Error for user {user_id}: HTTP {response.status} - {error_text}")
                return user_id, {"error": f"HTTP {response.status}: {error_text}"}
    
    except Exception as e:
        print(f"✗ Exception for user {user_id}: {str(e)}")
        return user_id, {"error": str(e)}

async def get_all_user_histories():
    """Get user histories for all test users"""
    print(f"Fetching user histories for {len(USER_IDS)} users: {USER_IDS[0]}-{USER_IDS[-1]}")
    
    user_histories = {}
    
    async with aiohttp.ClientSession() as session:
        # Create tasks for all users
        tasks = []
        for user_id in USER_IDS:
            tasks.append(get_user_history(session, user_id))
        
        # Execute all requests in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                print(f"✗ Task exception: {result}")
                continue
            
            user_id, history_data = result
            user_histories[str(user_id)] = history_data
    
    return user_histories

async def main():
    """Main function to fetch and save user histories"""
    try:
        print("Starting user history collection...")
        
        # Get all user histories
        user_histories = await get_all_user_histories()
        
        # Save to JSON file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(user_histories, f, ensure_ascii=False, indent=2)
        
        # Summary
        successful_requests = sum(1 for data in user_histories.values() if "error" not in data)
        failed_requests = len(user_histories) - successful_requests
        
        print(f"\n📊 Summary:")
        print(f"Total users: {len(USER_IDS)}")
        print(f"Successful requests: {successful_requests}")
        print(f"Failed requests: {failed_requests}")
        print(f"Results saved to: {OUTPUT_FILE}")
        
        if failed_requests > 0:
            print(f"\n❌ Failed users:")
            for user_id, data in user_histories.items():
                if "error" in data:
                    print(f"  User {user_id}: {data['error']}")
        
        print(f"\n✅ User history collection complete!")
        
    except Exception as e:
        print(f"❌ Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())