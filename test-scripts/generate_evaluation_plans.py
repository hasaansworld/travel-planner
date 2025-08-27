import asyncio
import csv
import json
from pathlib import Path
from datetime import datetime
import random
import httpx

# Config
CSV_FILE = "queries.csv"
BASE_URL = "https://travelplanner.ddns.net/plan"
OUTPUT_DIR = Path("travel-plans")
MODELS = ["gpt-4.1", "llama", "deepseek"]
PARALLEL_REQUESTS = 5

# Create folder structure
for category in ["personalized", "non-personalized"]:
    for model in ["gpt", "llama", "deepseek"]:
        for difficulty in ["easy", "medium", "hard"]:
            (OUTPUT_DIR / category / model / difficulty).mkdir(parents=True, exist_ok=True)

# Load queries
count = 0
queries = []
with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if count < 10:
            queries.append(row)
            count += 1

# Prepare users
personalized_users = [random.randint(1, 125000) for _ in range(25)] + list(range(125003, 125028))
non_personalized_user = 125001

# Dictionaries to track calls and errors
api_call_tracker = {}
errors = {}

# Helper to save JSON
def save_response(category, model, difficulty, query_id, user_id, response_data):
    model_folder = model if model != "gpt-4.1" else "gpt"
    difficulty_folder = difficulty.lower()
    filename = OUTPUT_DIR / category / model_folder / difficulty_folder / f"query_{query_id}_user_{user_id}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(response_data, f, ensure_ascii=False, indent=2)

async def call_api(client, params, category, model, difficulty):
    key = (params["user_id"], params["query_id"], model)
    try:
        # response = await client.get(BASE_URL, params=params, timeout=30)
        # response.raise_for_status()
        # result = response.json()
        result = {"success": True}
        api_call_tracker[key] = True
        save_response(category, model, difficulty, params["query_id"], params["user_id"], {"input": params, "output": result})
    except Exception as e:
        errors[key] = str(e)
        print(f"Error for user {params['user_id']}, query {params['query_id']}, model {model}: {e}")

async def process_user(client, user_id, category, is_personalized=True):
    if is_personalized:
        user_queries = queries[:3]  # personalized users get first 3 queries
    else:
        user_queries = queries  # non-personalized user gets all 150 queries

    for query in user_queries:
        for model in MODELS:
            params = {
                "user_id": user_id,
                "city_id": 1,
                "lat": float(query["latitude"]),
                "lon": float(query["longitude"]),
                "radius_km": int(query["radius_km"]),
                "rating": float(query["min_rating"]),
                "intent": query["user_message"],  # use user_message as intent
                "start_date": query["start_date"],
                "number_of_days": int(query["num_days"]),
                "model": model,
                "query_id": int(query["query_id"]),
            }
            await call_api(client, params, category, model, query["difficulty"])

async def run_all():
    semaphore = asyncio.Semaphore(PARALLEL_REQUESTS)
    async with httpx.AsyncClient() as client:
        tasks = []

        # Personalized users
        # for user_id in personalized_users:
        #     tasks.append(process_user(client, user_id, "personalized", is_personalized=True))

        # Non-personalized user
        tasks.append(process_user(client, non_personalized_user, "non-personalized", is_personalized=False))

        # Run tasks with concurrency limit
        async def sem_task(task):
            async with semaphore:
                await task

        await asyncio.gather(*(sem_task(t) for t in tasks))

if __name__ == "__main__":
    asyncio.run(run_all())
    print(f"Total successful API calls: {len(api_call_tracker)}")
    if errors:
        print("\nFailed API calls:")
        for key, err in errors.items():
            user_id, query_id, model = key
            print(f"User {user_id}, Query {query_id}, Model {model} → Error: {err}")
