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
PLAN_EVALS_DIR = Path("plan_evals")
EVAL_MODELS = ["llama4", "gpt-5"]
PLAN_MODELS = ["gpt", "llama", "deepseek"]
DIFFICULTIES = ["easy", "medium", "hard"]
QUERIES_CSV = "queries.csv"

# Load queries data for constraints
queries_data = {}
with open(QUERIES_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        queries_data[int(row["query_id"])] = row

# Create folder structure for evaluations: plan_evals/eval_model/category/plan_model/difficulty
for eval_model in EVAL_MODELS:
    eval_model_folder = eval_model.replace("gpt-5", "gpt").replace("llama4", "llama")
    for category in ["personalized", "non-personalized"]:
        for plan_model in PLAN_MODELS:
            for difficulty in DIFFICULTIES:
                (PLAN_EVALS_DIR / eval_model_folder / category / plan_model / difficulty).mkdir(parents=True, exist_ok=True)

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
    eval_filename = f"{base_name}_eval_{eval_model}.json"
    
    # Use new folder structure: plan_evals/eval_model/category/plan_model/difficulty
    eval_model_folder = eval_model.replace("gpt-5", "gpt").replace("llama4", "llama")
    file_path = PLAN_EVALS_DIR / eval_model_folder / category / plan_model / difficulty / eval_filename
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(evaluation_data, f, ensure_ascii=False, indent=2)

def evaluation_exists(category, plan_model, difficulty, eval_model, filename):
    """Check if evaluation file already exists"""
    base_name = filename.replace('.json', '')
    eval_filename = f"{base_name}_eval_{eval_model}.json"
    
    # Use new folder structure: plan_evals/eval_model/category/plan_model/difficulty
    eval_model_folder = eval_model.replace("gpt-5", "gpt").replace("llama4", "llama")
    file_path = PLAN_EVALS_DIR / eval_model_folder / category / plan_model / difficulty / eval_filename
    return file_path.exists()

def get_query_constraints(query_id):
    """Get constraints for a query, formatted with newlines"""
    if query_id not in queries_data:
        return "No constraints found"
    
    constraints = queries_data[query_id].get("hard_constraints", "")
    if not constraints:
        return "No constraints specified"
    
    # Split by - and join with newlines
    constraint_list = [constraint.strip() for constraint in constraints.split("-") if constraint.strip()]
    return f"* {"\n* ".join(constraint_list)}"

def get_query_message(query_id):
    """Get the original user message for a query"""
    if query_id not in queries_data:
        return "No query message found"
    
    return queries_data[query_id].get("user_message", "No query message found")

def clean_itinerary_data(plan_data):
    """Clean travel plan data to only include necessary fields"""
    if "travel_plan" not in plan_data:
        # Try to find the actual travel plan data
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
    
    cleaned_plan = {}
    
    for day_key, day_data in travel_plan.items():
        if not isinstance(day_data, dict) or "itinerary" not in day_data:
            continue
            
        cleaned_day = {
            "itinerary": []
        }
        
        for item in day_data["itinerary"]:
            cleaned_item = {
                "name": item.get("name", ""),
                "duration": item.get("duration", ""),
                "reason": item.get("reason", ""),
                "practical_notes": item.get("practical_notes", ""),
                "rating": item.get("rating", "")
            }
            cleaned_day["itinerary"].append(cleaned_item)
        
        cleaned_plan[day_key] = cleaned_day
    
    return cleaned_plan

async def evaluate_single_day(day_data, constraints, query, eval_model, day_name):
    """Evaluate a single day of travel itinerary"""
    system_message = """
    # Travel Itinerary Evaluator

You are evaluating a single day of travel itinerary against both common sense constraints and specific user requirements. You will be provided with the user's original query, their hard constraints, and one day's itinerary to evaluate in the user message. Review the provided day and evaluate all criteria comprehensively.

## EVALUATION CRITERIA:

### Common Sense Constraints:
1. **Diverse Attractions**: Check if the day has diversity of places, places are not too similar and no place is recommended more than once.
2. **Complete Daily Information**: Check if the day includes appropriate number of meals and at least 2-3 meaningful activities or attractions.
3. **Natural Visit Times**: Check if the timing of activities makes sense (appropriate meal times and POI visit times).
4. **Logical Activity Flow**: Check if the daily activity sequence is logical (not scheduling heavy meals right before physical activities, grouping related activities sensibly).
5. **Realistic Daily Pacing**: Check if the day has reasonable pacing - not too many activities crammed together, sufficient time between activities, realistic expectations.

### Hard Constraints:
Evaluate each specific user constraint provided in the USER CONSTRAINTS section. Check if this day's itinerary contributes to satisfying each requirement.

## EVALUATION PROCESS:
For each constraint, determine if it PASSES (fully meets requirement) or FAILS (does not meet requirement).

## RESPONSE FORMAT:
Return only a JSON object in the following exact format:

```json
{
  "passed_common_constraints": [
    "constraint_name"
  ],
  "failed_common_constraints": [
    "constraint_name"
  ],
  "passed_hard_constraints": [
    "constraint_name"
  ],
  "failed_hard_constraints": [
    "constraint_name"
  ]
}
```

### Common Constraint Names:
- "diverse_attractions"
- "complete_daily_information"
- "natural_visit_times"
- "logical_activity_flow"
- "realistic_daily_pacing"

### Hard Constraint Names:
Use the exact constraint identifiers from the USER CONSTRAINTS section.

## INSTRUCTIONS:
1. Carefully review the day's itinerary
2. Evaluate each common sense constraint for this day
3. Evaluate each user-specific hard constraint for this day
4. Categorize each constraint as passed or failed
5. Return the results in the specified JSON format
6. Do not include explanations or additional text - only the JSON response
    """

    user_message = f"""
Here's the required information:
query: {query}
hard constraints: 
{constraints}
day_itinerary: {json.dumps(day_data, indent=2)}
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
        
        # Count constraints
        passed_common = len(parsed_result.get("passed_common_constraints", []))
        failed_common = len(parsed_result.get("failed_common_constraints", []))
        passed_hard = len(parsed_result.get("passed_hard_constraints", []))
        failed_hard = len(parsed_result.get("failed_hard_constraints", []))
        
        print(f"{eval_model.upper()} {day_name.upper()}: {response_time:.2f}s | Common: {passed_common} passed, {failed_common} failed | Hard: {passed_hard} passed, {failed_hard} failed")
        
        return parsed_result
    except Exception as e:
        print(f"\n=== ERROR for {day_name.upper()} with {eval_model.upper()} ===")
        print(f"Error: {str(e)}")
        print("=" * 60)
        return {"error": str(e)}

async def evaluate_travel_plan(plan_data, eval_model, query_id):
    """Evaluate a travel plan day by day using the specified evaluation model"""
    # Get constraints and query message
    constraints = get_query_constraints(query_id)
    query = get_query_message(query_id)
    
    # Clean the itinerary data
    cleaned_plan = clean_itinerary_data(plan_data)
    
    if not cleaned_plan:
        return {"error": "No travel plan data found"}
    
    # Evaluate each day separately
    evaluation_results = {}
    
    for day_key, day_data in cleaned_plan.items():
        day_evaluation = await evaluate_single_day(day_data, constraints, query, eval_model, day_key)
        evaluation_results[day_key] = day_evaluation
    
    return evaluation_results

async def process_evaluations_for_model(eval_model):
    """Process all evaluations for a specific evaluation model"""
    global completed_evals
    print(f"\nProcessing evaluations with model: {eval_model}")
    
    # Process first 10 plans
    plans_processed = 0
    max_plans = 10
    
    for category in ["personalized", "non-personalized"]:
        for plan_model in PLAN_MODELS:
            for difficulty in DIFFICULTIES:
                plan_dir = TRAVEL_PLANS_DIR / category / plan_model / difficulty
                
                if not plan_dir.exists():
                    continue
                
                for plan_file in plan_dir.glob("*.json"):
                    if plans_processed >= max_plans:
                        return  # Exit after processing 10 plans
                    plans_processed += 1
                    # Extract query_id from filename (e.g., query_1_user_125003.json -> 1)
                    try:
                        query_id = int(plan_file.name.split('_')[1])
                    except (IndexError, ValueError):
                        print(f"Warning: Could not extract query_id from {plan_file.name}")
                        completed_evals += 1
                        continue
                    
                    # Skip if evaluation already exists
                    if evaluation_exists(category, plan_model, difficulty, eval_model, plan_file.name):
                        completed_evals += 1
                        print(f"Skipping existing evaluation: {category}/{plan_model}/{difficulty}/{plan_file.name} with {eval_model}")
                        print(f"Progress: {completed_evals}/{total_evals} evaluations completed ({completed_evals/total_evals*100:.1f}%)")
                        continue
                    
                    # Load the travel plan
                    plan_data = load_travel_plan(category, plan_model, difficulty, plan_file.name)
                    if plan_data is None:
                        completed_evals += 1
                        continue
                    
                    # Evaluate the plan
                    print(f"Evaluating: {category}/{plan_model}/{difficulty}/{plan_file.name} with {eval_model}")
                    evaluation = await evaluate_travel_plan(plan_data, eval_model, query_id)
                    
                    # Save evaluation data
                    save_evaluation(category, plan_model, difficulty, eval_model, plan_file.name, {
                        "evaluation": evaluation,
                        "eval_model": eval_model,
                        "plan_model": plan_model,
                        "category": category,
                        "difficulty": difficulty,
                        "query_id": query_id,
                        "constraints": get_query_constraints(query_id)
                    })
                    
                    completed_evals += 1
                    print(f"Progress: {completed_evals}/{total_evals} evaluations completed ({completed_evals/total_evals*100:.1f}%)")

async def run_evaluations():
    global total_evals
    
    # Count total evaluations needed
    total_plans = 0
    for category in ["personalized", "non-personalized"]:
        for plan_model in PLAN_MODELS:
            for difficulty in DIFFICULTIES:
                plan_dir = TRAVEL_PLANS_DIR / category / plan_model / difficulty
                if plan_dir.exists():
                    total_plans += len(list(plan_dir.glob("*.json")))
    
    total_evals = total_plans * len(EVAL_MODELS)
    print(f"Total evaluations to perform: {total_evals} ({total_plans} plans × {len(EVAL_MODELS)} eval models)")
    
    # Process evaluations for both models in parallel
    tasks = []
    for eval_model in EVAL_MODELS:
        tasks.append(process_evaluations_for_model(eval_model))
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(run_evaluations())
    print(f"\nEvaluation complete! Total evaluations performed: {completed_evals}")