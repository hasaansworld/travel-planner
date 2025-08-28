import json
import csv
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

# Config
PLAN_EVALS_DIR = Path("plan_evals")
QUERIES_CSV = Path("queries.csv")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

# Create results directory
RESULTS_DIR.mkdir(exist_ok=True)

# Load queries data to get constraint counts
queries_data = {}
with open(QUERIES_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        query_id = int(row["query_id"])
        constraints = row.get("hard_constraints", "")
        # Count hard constraints by splitting on '-'
        if constraints:
            constraint_count = len([c.strip() for c in constraints.split("-") if c.strip()])
        else:
            constraint_count = 0
        queries_data[query_id] = constraint_count

def get_evaluation_files(eval_model_folder):
    """Get all evaluation files for a specific model with plan model info"""
    eval_files = []
    model_dir = PLAN_EVALS_DIR / eval_model_folder
    if model_dir.exists():
        for file_path in model_dir.rglob("*_eval_*.json"):
            # Extract plan model from path: plan_evals/llama/category/plan_model/difficulty/file.json
            path_parts = file_path.parts
            if len(path_parts) >= 5:
                plan_model = path_parts[-3]  # plan_model is 3rd from end
                eval_files.append((file_path, plan_model))
            else:
                eval_files.append((file_path, "unknown"))
    return eval_files

def parse_evaluation_file(file_path, plan_model):
    """Parse an evaluation file and extract metrics"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        query_id = data.get("query_id")
        difficulty = data.get("difficulty")
        evaluation = data.get("evaluation", {})
        plan_model_from_data = data.get("plan_model", plan_model)
        
        # Count constraints for each day
        total_passed_common = 0
        total_failed_common = 0
        total_passed_hard = 0
        total_failed_hard = 0
        
        for day_key, day_eval in evaluation.items():
            if isinstance(day_eval, dict):
                total_passed_common += len(day_eval.get("passed_common_constraints", []))
                total_failed_common += len(day_eval.get("failed_common_constraints", []))
                total_passed_hard += len(day_eval.get("passed_hard_constraints", []))
                total_failed_hard += len(day_eval.get("failed_hard_constraints", []))
        
        # Calculate expected constraint counts
        num_days = len([k for k in evaluation.keys() if k.startswith("day")])
        expected_common_constraints = num_days * 5  # 5 common constraints per day
        expected_hard_constraints = queries_data.get(query_id, 0) * num_days  # hard constraints per day
        
        # Calculate actual constraint counts
        actual_common_constraints = total_passed_common + total_failed_common
        actual_hard_constraints = total_passed_hard + total_failed_hard
        
        return {
            "query_id": query_id,
            "difficulty": difficulty,
            "plan_model": plan_model_from_data,
            "passed_common": total_passed_common,
            "failed_common": total_failed_common,
            "passed_hard": total_passed_hard,
            "failed_hard": total_failed_hard,
            "expected_common": expected_common_constraints,
            "expected_hard": expected_hard_constraints,
            "actual_common": actual_common_constraints,
            "actual_hard": actual_hard_constraints
        }
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None

def calculate_metrics(evaluations):
    """Calculate micro and macro pass rates"""
    if not evaluations:
        return {"micro_pass": 0.0, "macro_pass": 0.0}
    
    # Micro pass: total passed / total constraints
    total_passed = sum(e["passed_common"] + e["passed_hard"] for e in evaluations)
    total_constraints = sum(e["actual_common"] + e["actual_hard"] for e in evaluations)
    
    micro_pass = (total_passed / total_constraints * 100) if total_constraints > 0 else 0.0
    
    # Macro pass: plans where all constraints passed / total plans
    plans_all_passed = sum(1 for e in evaluations 
                          if (e["passed_common"] + e["passed_hard"]) == (e["actual_common"] + e["actual_hard"]))
    
    macro_pass = (plans_all_passed / len(evaluations) * 100) if evaluations else 0.0
    
    return {
        "micro_pass": micro_pass,
        "macro_pass": macro_pass,
        "total_plans": len(evaluations),
        "total_passed": total_passed,
        "total_constraints": total_constraints,
        "plans_all_passed": plans_all_passed
    }

def process_model_evaluations(eval_model, eval_model_folder):
    """Process all evaluations for a specific model, grouped by plan model"""
    print(f"Processing evaluations for {eval_model}...")
    
    eval_files = get_evaluation_files(eval_model_folder)
    print(f"Found {len(eval_files)} evaluation files for {eval_model}")
    
    # Parse all evaluation files
    evaluations = []
    for file_path, plan_model in eval_files:
        parsed = parse_evaluation_file(file_path, plan_model)
        if parsed:
            evaluations.append(parsed)
    
    print(f"Successfully parsed {len(evaluations)} evaluations for {eval_model}")
    
    # Group by plan model and difficulty
    by_plan_model_difficulty = defaultdict(lambda: defaultdict(list))
    by_plan_model = defaultdict(list)
    
    for eval_data in evaluations:
        plan_model = eval_data["plan_model"]
        difficulty = eval_data["difficulty"]
        by_plan_model_difficulty[plan_model][difficulty].append(eval_data)
        by_plan_model[plan_model].append(eval_data)
    
    # Calculate metrics by plan model and difficulty
    results = {}
    
    for plan_model in ["gpt", "llama", "deepseek"]:
        # By difficulty
        for difficulty in ["easy", "medium", "hard"]:
            if difficulty in by_plan_model_difficulty[plan_model]:
                metrics = calculate_metrics(by_plan_model_difficulty[plan_model][difficulty])
                results[f"{plan_model}_{difficulty}"] = metrics
                print(f"{plan_model} {difficulty}: Micro={metrics['micro_pass']:.1f}%, Macro={metrics['macro_pass']:.1f}%")
        
        # Overall for this plan model
        if plan_model in by_plan_model:
            overall_metrics = calculate_metrics(by_plan_model[plan_model])
            results[f"{plan_model}_total"] = overall_metrics
            print(f"{plan_model} total: Micro={overall_metrics['micro_pass']:.1f}%, Macro={overall_metrics['macro_pass']:.1f}%")
    
    # Calculate overall metrics across all plan models
    overall_metrics = calculate_metrics(evaluations)
    results["total"] = overall_metrics
    print(f"Total: Micro={overall_metrics['micro_pass']:.1f}%, Macro={overall_metrics['macro_pass']:.1f}%")
    
    return results, evaluations

def create_bar_chart(results_data, eval_model):
    """Create and save bar chart for a specific evaluation model"""
    categories = list(results_data.keys())
    micro_scores = [results_data[cat]["micro_pass"] for cat in categories]
    macro_scores = [results_data[cat]["macro_pass"] for cat in categories]
    
    x = np.arange(len(categories))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 8))
    bars1 = ax.bar(x - width/2, micro_scores, width, label='Micro Pass %', alpha=0.8)
    bars2 = ax.bar(x + width/2, macro_scores, width, label='Macro Pass %', alpha=0.8)
    
    ax.set_xlabel('Plan Model Categories')
    ax.set_ylabel('Pass Rate (%)')
    ax.set_title(f'Evaluation Results ({eval_model.upper()}): Micro vs Macro Pass Rates')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add value labels on bars
    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
    
    add_value_labels(bars1)
    add_value_labels(bars2)
    
    plt.tight_layout()
    
    # Save chart
    chart_path = RESULTS_DIR / f"evaluation_results_{eval_model}.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Chart saved to {chart_path}")

def main():
    """Main function to process all evaluations and generate results"""
    
    # Process Llama4 evaluations
    print("Processing Llama4 evaluations...")
    llama_results, llama_evals = process_model_evaluations("llama4", "llama")
    
    # Save Llama4 results to separate JSON
    llama_json_path = RESULTS_DIR / "evaluation_results_llama4.json"
    with open(llama_json_path, 'w', encoding='utf-8') as f:
        json.dump(llama_results, f, ensure_ascii=False, indent=2)
    print(f"Llama4 results saved to {llama_json_path}")
    
    # Create bar chart for Llama4
    print("Creating bar chart for Llama4 evaluations...")
    create_bar_chart(llama_results, "llama4")
    
    # Process GPT-5 evaluations
    print("\n" + "="*50)
    print("Processing GPT-5 evaluations...")
    gpt_results, gpt_evals = process_model_evaluations("gpt-5", "gpt")
    
    # Save GPT-5 results to separate JSON
    gpt_json_path = RESULTS_DIR / "evaluation_results_gpt5.json"
    with open(gpt_json_path, 'w', encoding='utf-8') as f:
        json.dump(gpt_results, f, ensure_ascii=False, indent=2)
    print(f"GPT-5 results saved to {gpt_json_path}")
    
    # Create bar chart for GPT-5
    print("Creating bar chart for GPT-5 evaluations...")
    create_bar_chart(gpt_results, "gpt-5")
    
    print(f"\nAnalysis complete! Results saved in {RESULTS_DIR}")

if __name__ == "__main__":
    main()