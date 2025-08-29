import json
import csv
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

# Config
PERSONALIZATION_EVALS_DIR = Path("personalization_evals")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

def get_evaluation_files(eval_model_folder):
    """Get all evaluation files for a specific model with plan model info"""
    eval_files = []
    model_dir = PERSONALIZATION_EVALS_DIR / eval_model_folder
    if model_dir.exists():
        for file_path in model_dir.rglob("*_personalization_eval_*.json"):
            # Extract plan model from path: personalization_evals/llama/category/plan_model/difficulty/file.json
            path_parts = file_path.parts
            if len(path_parts) >= 5:
                plan_model = path_parts[-3]  # plan_model is 3rd from end
                category = path_parts[-4]    # category is 4th from end
                eval_files.append((file_path, plan_model, category))
            else:
                eval_files.append((file_path, "unknown", "unknown"))
    return eval_files

def parse_evaluation_file(file_path, plan_model, category):
    """Parse an evaluation file and extract personalization scores"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        query_id = data.get("query_id")
        difficulty = data.get("difficulty")
        user_id = data.get("user_id")
        evaluation = data.get("evaluation", {})
        plan_model_from_data = data.get("plan_model", plan_model)
        
        # Extract personalization scores
        personalized_score = evaluation.get("personalized_score", 0)
        non_personalized_score = evaluation.get("non_personalized_score", 0)
        
        # Extract individual evaluations for detailed analysis
        personalized_eval = evaluation.get("personalized_evaluation", {})
        non_personalized_eval = evaluation.get("non_personalized_evaluation", {})
        
        return {
            "query_id": query_id,
            "difficulty": difficulty,
            "category": category,
            "user_id": user_id,
            "plan_model": plan_model_from_data,
            "personalized_score": personalized_score,
            "non_personalized_score": non_personalized_score,
            "personalized_explanation": personalized_eval.get("explanation", ""),
            "non_personalized_explanation": non_personalized_eval.get("explanation", ""),
            "score_difference": personalized_score - non_personalized_score
        }
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None

def calculate_metrics(evaluations):
    """Calculate personalization metrics"""
    if not evaluations:
        return {
            "avg_personalized": 0.0, 
            "avg_non_personalized": 0.0, 
            "avg_difference": 0.0,
            "total_evaluations": 0,
            "personalized_wins": 0,
            "win_rate": 0.0
        }
    
    # Calculate averages
    personalized_scores = [e["personalized_score"] for e in evaluations]
    non_personalized_scores = [e["non_personalized_score"] for e in evaluations]
    differences = [e["score_difference"] for e in evaluations]
    
    avg_personalized = sum(personalized_scores) / len(personalized_scores)
    avg_non_personalized = sum(non_personalized_scores) / len(non_personalized_scores)
    avg_difference = sum(differences) / len(differences)
    
    # Count wins (personalized > non-personalized)
    personalized_wins = sum(1 for diff in differences if diff > 0)
    win_rate = (personalized_wins / len(evaluations)) * 100
    
    return {
        "avg_personalized": avg_personalized,
        "avg_non_personalized": avg_non_personalized,
        "avg_difference": avg_difference,
        "total_evaluations": len(evaluations),
        "personalized_wins": personalized_wins,
        "win_rate": win_rate
    }

def process_model_evaluations(eval_model, eval_model_folder):
    """Process all evaluations for a specific model, grouped by plan model"""
    print(f"Processing personalization evaluations for {eval_model}...")
    
    eval_files = get_evaluation_files(eval_model_folder)
    print(f"Found {len(eval_files)} evaluation files for {eval_model}")
    
    # Parse all evaluation files
    evaluations = []
    for file_path, plan_model, category in eval_files:
        parsed = parse_evaluation_file(file_path, plan_model, category)
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
                print(f"{plan_model} {difficulty}: Avg Personalized={metrics['avg_personalized']:.1f}, Avg Non-personalized={metrics['avg_non_personalized']:.1f}, Diff={metrics['avg_difference']:.1f}, Win Rate={metrics['win_rate']:.1f}%")
        
        # Overall for this plan model
        if plan_model in by_plan_model:
            overall_metrics = calculate_metrics(by_plan_model[plan_model])
            results[f"{plan_model}_total"] = overall_metrics
            print(f"{plan_model} total: Avg Personalized={overall_metrics['avg_personalized']:.1f}, Avg Non-personalized={overall_metrics['avg_non_personalized']:.1f}, Diff={overall_metrics['avg_difference']:.1f}, Win Rate={overall_metrics['win_rate']:.1f}%")
    
    # Calculate overall metrics across all plan models
    overall_metrics = calculate_metrics(evaluations)
    results["total"] = overall_metrics
    print(f"Total: Avg Personalized={overall_metrics['avg_personalized']:.1f}, Avg Non-personalized={overall_metrics['avg_non_personalized']:.1f}, Diff={overall_metrics['avg_difference']:.1f}, Win Rate={overall_metrics['win_rate']:.1f}%")
    
    return results, evaluations

def create_personalization_charts(results_data, eval_model):
    """Create and save personalization charts for a specific evaluation model"""
    categories = list(results_data.keys())
    personalized_scores = [results_data[cat]["avg_personalized"] for cat in categories]
    non_personalized_scores = [results_data[cat]["avg_non_personalized"] for cat in categories]
    differences = [results_data[cat]["avg_difference"] for cat in categories]
    
    # Chart 1: Average Scores Comparison
    x = np.arange(len(categories))
    width = 0.35
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
    
    # Subplot 1: Score Comparison
    bars1 = ax1.bar(x - width/2, personalized_scores, width, label='Personalized Plans', alpha=0.8, color='#2E8B57')
    bars2 = ax1.bar(x + width/2, non_personalized_scores, width, label='Non-personalized Plans', alpha=0.8, color='#CD853F')
    
    ax1.set_xlabel('Plan Model Categories')
    ax1.set_ylabel('Average Personalization Score (out of 10)')
    ax1.set_title(f'Personalization Scores Comparison ({eval_model.upper()})')
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 10)
    
    # Add value labels on bars
    def add_value_labels(bars, ax):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{height:.1f}', ha='center', va='bottom', fontsize=8)
    
    add_value_labels(bars1, ax1)
    add_value_labels(bars2, ax1)
    
    # Subplot 2: Score Differences
    colors = ['green' if diff > 0 else 'red' for diff in differences]
    bars3 = ax2.bar(x, differences, color=colors, alpha=0.7)
    
    ax2.set_xlabel('Plan Model Categories')
    ax2.set_ylabel('Score Difference (Personalized - Non-personalized)')
    ax2.set_title(f'Personalization Score Differences ({eval_model.upper()})')
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories, rotation=45, ha='right')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    
    # Add value labels on difference bars
    for bar in bars3:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + (0.05 if height > 0 else -0.15),
               f'{height:.1f}', ha='center', va='bottom' if height > 0 else 'top', fontsize=8)
    
    plt.tight_layout()
    
    # Save chart
    chart_path = RESULTS_DIR / f"personalization_results_{eval_model}.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Personalization chart saved to {chart_path}")

def create_win_rate_chart(results_data, eval_model):
    """Create win rate chart showing percentage of times personalized beats non-personalized"""
    categories = list(results_data.keys())
    win_rates = [results_data[cat]["win_rate"] for cat in categories]
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    bars = ax.bar(categories, win_rates, alpha=0.8, color='#4682B4')
    
    ax.set_xlabel('Plan Model Categories')
    ax.set_ylabel('Win Rate (%)')
    ax.set_title(f'Personalized Plan Win Rate ({eval_model.upper()}): % of times personalized > non-personalized')
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 100)
    ax.axhline(y=50, color='red', linestyle='--', alpha=0.7, label='50% baseline')
    ax.legend()
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
               f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    
    # Save chart
    chart_path = RESULTS_DIR / f"personalization_win_rates_{eval_model}.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Win rate chart saved to {chart_path}")

def main():
    """Main function to process all evaluations and generate results"""
    
    # Process Llama4 evaluations
    print("Processing Llama4 personalization evaluations...")
    llama_results, llama_evals = process_model_evaluations("llama4", "llama")
    
    # Save Llama4 results to separate JSON
    llama_json_path = RESULTS_DIR / "personalization_results_llama4.json"
    with open(llama_json_path, 'w', encoding='utf-8') as f:
        json.dump(llama_results, f, ensure_ascii=False, indent=2)
    print(f"Llama4 personalization results saved to {llama_json_path}")
    
    # Create charts for Llama4
    print("Creating charts for Llama4 personalization evaluations...")
    create_personalization_charts(llama_results, "llama4")
    create_win_rate_chart(llama_results, "llama4")
    
    # Process GPT-5 evaluations 
    print("\n" + "="*50)
    print("Processing GPT-5 personalization evaluations...")
    gpt_results, gpt_evals = process_model_evaluations("gpt-5", "gpt")
    
    # Save GPT-5 results to separate JSON
    gpt_json_path = RESULTS_DIR / "personalization_results_gpt5.json"
    with open(gpt_json_path, 'w', encoding='utf-8') as f:
        json.dump(gpt_results, f, ensure_ascii=False, indent=2)
    print(f"GPT-5 personalization results saved to {gpt_json_path}")
    
    # Create charts for GPT-5
    print("Creating charts for GPT-5 personalization evaluations...")
    create_personalization_charts(gpt_results, "gpt-5")
    create_win_rate_chart(gpt_results, "gpt-5")
    
    print(f"\nPersonalization analysis complete! Results saved in {RESULTS_DIR}")

if __name__ == "__main__":
    main()