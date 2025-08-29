import asyncio
import json
import os
import csv
import sys
import time
from pathlib import Path
from openai import AsyncOpenAI
from groq import AsyncGroq
from dotenv import load_dotenv
import traceback

load_dotenv()

# Config
TRAVEL_PLANS_DIR = Path("travel-plans")
PERSONALIZATION_EVALS_DIR = Path("personalization_evals")
USER_HISTORIES_FILE = Path("user_histories.json")
EVAL_MODELS = ["llama4", "gpt-5"]
PLAN_MODELS = ["gpt", "llama", "deepseek"]
DIFFICULTIES = ["easy", "medium", "hard"]
QUERIES_CSV = "queries.csv"

# Load user histories
with open(USER_HISTORIES_FILE, 'r', encoding='utf-8') as f:
    user_histories = json.load(f)

# Load queries data for mapping
queries_data = {}
with open(QUERIES_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        queries_data[int(row["query_id"])] = row

# Progress tracking
total_evals = 0
completed_evals = 0

async def generate_llm_response(messages, model_name, api_key="", **kwargs):
    # Set default parameters
    max_tokens = kwargs.get('max_tokens', 1000)
    temperature = kwargs.get('temperature', 0.0)
    top_p = kwargs.get('top_p', 1.0)
    
    if model_name == "deepseek":
        model_name = "deepseek-r1-distill-llama-70b"
    elif model_name == "llama":
        model_name = "meta-llama/llama-4-maverick-17b-128e-instruct"
    elif model_name == "llama4":
        model_name = "meta-llama/llama-4-maverick-17b-128e-instruct"
    
    try:
        # Route to OpenAI if model contains 'gpt'
        if 'gpt' in model_name.lower():
            if not api_key:
                api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required for GPT models")
            
            client = AsyncOpenAI(api_key=api_key)
        
        # Route to Groq for all other models
        else:
            if not api_key:
                api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable is required for non-GPT models")
            
            client = AsyncGroq(api_key=api_key)

        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            response_format={ "type": "json_object" },
            temperature=1 if model_name.lower() == "gpt-5" else temperature,
            top_p=top_p,
        )
         
        return response.choices[0].message.content
            
    except Exception as e:
        raise ValueError(f"Failed to generate response: {str(e)}")

def load_travel_plan(category, plan_model, difficulty, filename):
    """Load a travel plan JSON file"""
    file_path = TRAVEL_PLANS_DIR / category / plan_model / difficulty / filename
    if not file_path.exists():
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_evaluation(category, plan_model, difficulty, eval_model, filename, evaluation_data):
    """Save evaluation result to JSON file"""
    # Create filename with eval model suffix
    base_name = filename.replace('.json', '')
    eval_filename = f"{base_name}_personalization_eval_{eval_model}.json"
    
    # Use folder structure: personalization_evals/eval_model/category/plan_model/difficulty
    eval_model_folder = eval_model.replace("gpt-5", "gpt").replace("llama4", "llama")
    file_path = PERSONALIZATION_EVALS_DIR / eval_model_folder / category / plan_model / difficulty / eval_filename
    
    # Create directories if they don't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(evaluation_data, f, ensure_ascii=False, indent=2)

def evaluation_exists(category, plan_model, difficulty, eval_model, filename):
    """Check if evaluation file already exists"""
    base_name = filename.replace('.json', '')
    eval_filename = f"{base_name}_personalization_eval_{eval_model}.json"
    
    # Use folder structure: personalization_evals/eval_model/category/plan_model/difficulty
    eval_model_folder = eval_model.replace("gpt-5", "gpt").replace("llama4", "llama")
    file_path = PERSONALIZATION_EVALS_DIR / eval_model_folder / category / plan_model / difficulty / eval_filename
    return file_path.exists()

def get_user_id_from_query_id(query_id):
    """Map query_id to user_id based on the generation pattern"""
    # Query 1-20 map to users 125003-125022
    if 1 <= query_id <= 20:
        return 125002 + query_id  # query 1 -> 125003, query 2 -> 125004, etc.
    elif 51 <= query_id <= 70:
        return 125002 + (query_id - 50)  # query 51 -> 125003, query 52 -> 125004, etc.
    elif 101 <= query_id <= 120:
        return 125002 + (query_id - 100)  # query 101 -> 125003, query 102 -> 125004, etc.
    else:
        return None

def extract_itinerary_from_plan(plan_data):
    """Extract clean itinerary data from travel plan"""
    if "travel_plan" not in plan_data:
        if "output" in plan_data and isinstance(plan_data["output"], dict):
            output_data = plan_data["output"]
            if "travel_plan" in output_data:
                travel_plan = output_data["travel_plan"]
            else:
                return {}
        else:
            return {}
    else:
        travel_plan = plan_data["travel_plan"]
    
    itinerary_data = {}
    
    for day_key, day_data in travel_plan.items():
        if not isinstance(day_data, dict) or "itinerary" not in day_data:
            continue
            
        day_itinerary = []
        for item in day_data["itinerary"]:
            clean_item = {
                "name": item.get("name", ""),
                "duration": item.get("duration", ""),
                "reason": item.get("reason", ""),
                "practical_notes": item.get("practical_notes", ""),
                "rating": item.get("rating", "")
            }
            day_itinerary.append(clean_item)
        
        itinerary_data[day_key] = day_itinerary
    
    return itinerary_data

async def evaluate_single_plan(plan_itinerary, user_history, query_id, plan_type, eval_model, query_text=""):
    """Evaluate personalization of a single plan against user history"""
    system_message = """
    You are evaluating how well a travel itinerary is personalized based on a user's past activity history while keeping the constraints of their travel query in mind. The plan has been personalized to match the user's preferences within the bounds of what they specifically requested. Review the user's historical preferences, their travel query constraints, and the generated itinerary, then provide a personalization score in the json format given below.

EVALUATION INSTRUCTIONS:
Analyze how well the itinerary personalizes the user's request by considering:

Query Constraint Adherence: The plan must fulfill the specific requirements mentioned in the travel query (destinations, activities, cuisine types, etc.)

Personalized Selection Within Constraints: Within the query requirements, how well does the plan choose options that align with the user's historical preferences?

Place Type Preferences: Does the itinerary include types of places the user frequently visits when selecting venues that meet the query constraints?

Time-of-Day Patterns: Are activities scheduled at times when the user typically prefers certain activities?

Cuisine Preferences: When restaurants are selected to meet query constraints, do they match the user's historical dining preferences?

Activity Style: Does the itinerary match the user's preferred activity intensity and style while fulfilling the query requirements?

Visit Duration Patterns: Are the recommended venues similar to places where the user typically spends time?


SCORING CRITERIA:
9-10: Excellent personalization - itinerary strongly reflects user's established preferences while perfectly meeting query constraints
7-8: Good personalization - most selections within query constraints align well with user history
5-6: Moderate personalization - some alignment with preferences while meeting query requirements
3-4: Poor personalization - meets query constraints but limited connection to user's past behavior
1-2: No personalization - generic selections that ignore user preferences despite meeting query constraints

RESPONSE FORMAT:
{"score": x, "explanation": ""}

Explanation:
- How well the plan personalizes selections within the query constraints
- What aspects match the user's preferences well
- What aspects don't align with user history
- Important user preferences that could have been incorporated while still meeting query requirements

EXAMPLE:
{"score": 8, "explanation": "Plan successfully incorporates user's preference for cultural attractions and fine dining within the query's museum and restaurant requirements. However, scheduled activities too early in the day when user historically prefers afternoon/evening activities. Could have selected more outdoor dining options that align with user's park visit history."}

    """
    
    user_message = f"""
travel_query: {query_text}
query_id: {query_id}
user_history: {user_history}
plan_type: {plan_type}
plan_itinerary: {json.dumps(plan_itinerary, indent=2)}
"""
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]
    
    try:
        start_time = time.time()
        result = await generate_llm_response(messages, eval_model)
        end_time = time.time()
        response_time = end_time - start_time
        
        parsed_result = json.loads(result)
        
        # Extract score
        score = parsed_result.get("score", 0)
        
        print(f"{eval_model.upper()} Query {query_id} ({plan_type}): {response_time:.2f}s | Score: {score}/10")
        
        return parsed_result
    except Exception as e:
        print(f"\n=== ERROR for Query {query_id} ({plan_type}) with {eval_model.upper()} ===")
        print(f"Error: {str(e)}")
        print("=" * 60)
        return {"error": str(e)}

async def evaluate_personalization(personalized_plan, non_personalized_plan, user_history, query_id, eval_model, query_text=""):
    """Evaluate personalization of two plans against user history separately"""
    
    # Evaluate personalized plan
    personalized_result = await evaluate_single_plan(
        personalized_plan, user_history, query_id, "personalized", eval_model, query_text
    )
    
    # Evaluate non-personalized plan
    non_personalized_result = await evaluate_single_plan(
        non_personalized_plan, user_history, query_id, "non-personalized", eval_model, query_text
    )
    
    # Combine results
    combined_result = {
        "personalized_evaluation": personalized_result,
        "non_personalized_evaluation": non_personalized_result,
        "personalized_score": personalized_result.get("score", 0) if "error" not in personalized_result else 0,
        "non_personalized_score": non_personalized_result.get("score", 0) if "error" not in non_personalized_result else 0
    }
    
    return combined_result

async def process_evaluations_for_model(eval_model):
    """Process all personalization evaluations for a specific evaluation model"""
    global completed_evals
    print(f"\nProcessing personalization evaluations with model: {eval_model}")
    
    for plan_model in PLAN_MODELS:
        for difficulty in DIFFICULTIES:
            # Get personalized plan directory
            personalized_dir = TRAVEL_PLANS_DIR / "personalized" / plan_model / difficulty
            non_personalized_dir = TRAVEL_PLANS_DIR / "non-personalized" / plan_model / difficulty
            
            if not personalized_dir.exists() or not non_personalized_dir.exists():
                continue
            
            # Process each query file
            for plan_file in personalized_dir.glob("*.json"):
                # Extract query_id from filename (e.g., query_1_user_125003.json -> 1)
                try:
                    query_id = int(plan_file.name.split('_')[1])
                except (IndexError, ValueError):
                    print(f"Warning: Could not extract query_id from {plan_file.name}")
                    completed_evals += 1
                    continue
                
                # Get corresponding user_id
                user_id = get_user_id_from_query_id(query_id)
                if user_id is None:
                    print(f"Warning: Could not map query_id {query_id} to user_id")
                    completed_evals += 1
                    continue
                
                # Get user history
                user_history_data = user_histories.get(str(user_id))
                if not user_history_data or "error" in user_history_data:
                    print(f"Warning: No valid user history for user {user_id}")
                    completed_evals += 1
                    continue
                
                user_history = user_history_data.get("user_activity", "")
                
                # Skip if evaluation already exists (using personalized category as reference)
                if evaluation_exists("personalized", plan_model, difficulty, eval_model, plan_file.name):
                    completed_evals += 1
                    print(f"Skipping existing evaluation: {plan_model}/{difficulty}/{plan_file.name} with {eval_model}")
                    print(f"Progress: {completed_evals}/{total_evals} evaluations completed ({completed_evals/total_evals*100:.1f}%)")
                    continue
                
                # Load both plans
                personalized_plan = load_travel_plan("personalized", plan_model, difficulty, plan_file.name)
                
                # Find corresponding non-personalized plan
                non_personalized_filename = f"query_{query_id}_user_125001.json"
                non_personalized_plan = load_travel_plan("non-personalized", plan_model, difficulty, non_personalized_filename)
                
                if personalized_plan is None or non_personalized_plan is None:
                    print(f"Warning: Could not load plans for query {query_id}")
                    completed_evals += 1
                    continue
                
                # Extract itineraries
                personalized_itinerary = extract_itinerary_from_plan(personalized_plan)
                non_personalized_itinerary = extract_itinerary_from_plan(non_personalized_plan)
                
                if not personalized_itinerary or not non_personalized_itinerary:
                    print(f"Warning: Could not extract itineraries for query {query_id}")
                    completed_evals += 1
                    continue
                
                # Get query text from queries_data
                query_text = queries_data.get(query_id, {}).get("user_message", "")
                
                # Evaluate personalization
                print(f"Evaluating personalization: {plan_model}/{difficulty}/query_{query_id} with {eval_model}")
                evaluation = await evaluate_personalization(
                    personalized_itinerary, 
                    non_personalized_itinerary, 
                    user_history, 
                    query_id, 
                    eval_model,
                    query_text
                )
                
                # Save evaluation data for both categories (same result applies to both)
                evaluation_data = {
                    "evaluation": evaluation,
                    "eval_model": eval_model,
                    "plan_model": plan_model,
                    "difficulty": difficulty,
                    "query_id": query_id,
                    "user_id": user_id,
                    "user_history": user_history
                }
                
                # Save to personalized category
                save_evaluation("personalized", plan_model, difficulty, eval_model, plan_file.name, evaluation_data)
                
                # Save to non-personalized category with different filename
                save_evaluation("non-personalized", plan_model, difficulty, eval_model, non_personalized_filename, evaluation_data)
                
                completed_evals += 1
                print(f"Progress: {completed_evals}/{total_evals} evaluations completed ({completed_evals/total_evals*100:.1f}%)")

async def run_evaluations():
    global total_evals
    
    # Count total evaluations needed (unique query/plan_model/difficulty combinations)
    total_combinations = 0
    for plan_model in PLAN_MODELS:
        for difficulty in DIFFICULTIES:
            personalized_dir = TRAVEL_PLANS_DIR / "personalized" / plan_model / difficulty
            if personalized_dir.exists():
                total_combinations += len(list(personalized_dir.glob("*.json")))
    
    total_evals = total_combinations * len(EVAL_MODELS)
    print(f"Total personalization evaluations to perform: {total_evals} ({total_combinations} combinations × {len(EVAL_MODELS)} eval models)")
    
    # Process evaluations
    tasks = []
    tasks.append(process_evaluations_for_model("llama4"))
    
    # Process GPT-5 evaluations (commented out)
    tasks.append(process_evaluations_for_model("gpt-5"))
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(run_evaluations())
    print(f"\nPersonalization evaluation complete! Total evaluations performed: {completed_evals}")