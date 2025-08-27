import asyncio
import csv
import json
from pathlib import Path
from datetime import datetime
import random
import httpx
from collections import defaultdict

# Config
CSV_FILE = "queries.csv"
BASE_URL = "https://travelplanner.ddns.net/plan"
OUTPUT_DIR = Path("travel-plans")
MODELS = ["gpt-4.1", "llama", "deepseek"]

# Create folder structure
for category in ["personalized", "non-personalized"]:
    for model in ["gpt", "llama", "deepseek"]:
        for difficulty in ["easy", "medium", "hard"]:
            (OUTPUT_DIR / category / model / difficulty).mkdir(parents=True, exist_ok=True)

# Load and filter queries - use first 20 from each difficulty (ignore last 30 from each)
queries_by_difficulty = defaultdict(list)
with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        queries_by_difficulty[row["difficulty"].lower()].append(row)

# Take first 20 queries from each difficulty (total 60 queries)
selected_queries = []
for difficulty in ["easy", "medium", "hard"]:
    selected_queries.extend(queries_by_difficulty[difficulty][:20])

print(f"Loaded {len(selected_queries)} queries (20 from each difficulty)")

# Prepare users
personalized_users = list(range(125003, 125023))  # 20 users (125003-125022 inclusive)
non_personalized_user = 125001

# Dictionaries to track calls and errors
api_call_tracker = {}
errors = {}
total_calls = 0
completed_calls = 0

# Helper to check if response file exists
def response_file_exists(category, model, difficulty, query_id, user_id):
    model_folder = model if model != "gpt-4.1" else "gpt"
    difficulty_folder = difficulty.lower()
    filename = OUTPUT_DIR / category / model_folder / difficulty_folder / f"query_{query_id}_user_{user_id}.json"
    return filename.exists()

# Helper to save JSON
def save_response(category, model, difficulty, query_id, user_id, response_data):
    model_folder = model if model != "gpt-4.1" else "gpt"
    difficulty_folder = difficulty.lower()
    filename = OUTPUT_DIR / category / model_folder / difficulty_folder / f"query_{query_id}_user_{user_id}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(response_data, f, ensure_ascii=False, indent=2)

async def call_api(client, params, category, model, difficulty, retry):
    global completed_calls
    key = (params["user_id"], params["query_id"], model)
    
    # Skip if file already exists
    if response_file_exists(category, model, difficulty, params["query_id"], params["user_id"]):
        completed_calls += 1
        print(f"Skipping existing file: user {params['user_id']}, query {params['query_id']}, model {model}")
        print(f"Progress: {completed_calls}/{total_calls} API calls completed ({completed_calls/total_calls*100:.1f}%)")
        return
    
    # Create API params without internal tracking fields
    api_params = {k: v for k, v in params.items() if k not in ["query_id", "difficulty", "category"]}
    
    try:
        response = await client.get(BASE_URL, params=api_params, timeout=600)
        response.raise_for_status()
        result = response.json()
        # result = {"success": True}
        api_call_tracker[key] = True
        save_response(category, model, difficulty, params["query_id"], params["user_id"], {"input": params, "output": result})
        
        completed_calls += 1
        print(f"Completed: user {params['user_id']}, query {params['query_id']}, model {model}")
        print(f"Progress: {completed_calls}/{total_calls} API calls completed ({completed_calls/total_calls*100:.1f}%)")
        
    except Exception as e:
        if not retry:
            await call_api(client, params, category, model, difficulty, True)
        else:
            error_details = str(e)
            try:
                # Try to get response body for more detailed error info
                if hasattr(e, 'response') and e.response is not None:
                    error_details += f" - Response body: {e.response.text}"
                elif 'response' in locals():
                    error_details += f" - Response body: {response.text}"
            except:
                pass  # If we can't get response body, just use the original error
            
            errors[key] = error_details
            completed_calls += 1
            print(f"Error for user {params['user_id']}, query {params['query_id']}, model {model}: {error_details}")
            print(f"Progress: {completed_calls}/{total_calls} API calls completed ({completed_calls/total_calls*100:.1f}%)")

# Generate API calls organized by model
def generate_api_calls_by_model():
    api_calls_by_model = {model: [] for model in MODELS}
    
    # Organize queries by difficulty for even distribution
    easy_queries = queries_by_difficulty["easy"][:20]
    medium_queries = queries_by_difficulty["medium"][:20] 
    hard_queries = queries_by_difficulty["hard"][:20]
    
    # For personalized users: 20 users × 3 queries (1 per difficulty) per model
    for i, user_id in enumerate(personalized_users):
        # Each user gets 1 query from each difficulty category
        user_queries = [
            easy_queries[i % len(easy_queries)],
            medium_queries[i % len(medium_queries)], 
            hard_queries[i % len(hard_queries)]
        ]
        
        for query in user_queries:
            for model in MODELS:
                api_calls_by_model[model].append({
                    "user_id": user_id,
                    "city_id": 1,
                    "lat": float(query["latitude"]),
                    "lon": float(query["longitude"]),
                    "radius_km": int(query["radius_km"]),
                    "rating": float(query["min_rating"]),
                    "intent": query["user_message"],
                    "start_date": query["start_date"],
                    "number_of_days": int(query["num_days"]),
                    "model": model,
                    "query_id": int(query["query_id"]),
                    "difficulty": query["difficulty"],
                    "category": "personalized"
                })
    
    # For non-personalized user: 60 queries per model
    for query in selected_queries:
        for model in MODELS:
            api_calls_by_model[model].append({
                "user_id": non_personalized_user,
                "city_id": 1,
                "lat": float(query["latitude"]),
                "lon": float(query["longitude"]),
                "radius_km": int(query["radius_km"]),
                "rating": float(query["min_rating"]),
                "intent": query["user_message"],
                "start_date": query["start_date"],
                "number_of_days": int(query["num_days"]),
                "model": model,
                "query_id": int(query["query_id"]),
                "difficulty": query["difficulty"],
                "category": "non-personalized"
            })
    
    return api_calls_by_model

async def process_model_calls(client, model, calls):
    print(f"\nProcessing {len(calls)} calls for model: {model}")
    
    for call_data in calls:
        category = call_data["category"]
        difficulty = call_data["difficulty"]
        await call_api(client, call_data, category, model, difficulty, False)

async def run_all():
    global total_calls
    
    # Generate API calls organized by model
    api_calls_by_model = generate_api_calls_by_model()
    total_calls = sum(len(calls) for calls in api_calls_by_model.values())
    print(f"Total API calls to make: {total_calls}")
    
    async with httpx.AsyncClient() as client:
        # Process all models in parallel, but one request at a time per model
        tasks = []
        for model in MODELS:
            tasks.append(process_model_calls(client, model, api_calls_by_model[model]))
        
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(run_all())
    print(f"Total successful API calls: {len(api_call_tracker)}")
    if errors:
        print("\nFailed API calls:")
        for key, err in errors.items():
            user_id, query_id, model = key
            print(f"User {user_id}, Query {query_id}, Model {model} → Error: {err}")
