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
            "user_id": user_id,
            "category": category,
            "plan_model": plan_model_from_data,
            "personalized_score": personalized_score,
            "non_personalized_score": non_personalized_score,
            "personalized_eval": personalized_eval,
            "non_personalized_eval": non_personalized_eval
        }
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None

def calculate_metrics(evaluations):
    """Calculate average personalized and non-personalized scores"""
    if not evaluations:
        return {"avg_personalized": 0.0, "avg_non_personalized": 0.0, "difference": 0.0}
    
    total_personalized = sum(e["personalized_score"] for e in evaluations)
    total_non_personalized = sum(e["non_personalized_score"] for e in evaluations)
    
    avg_personalized = total_personalized / len(evaluations)
    avg_non_personalized = total_non_personalized / len(evaluations)
    difference = avg_personalized - avg_non_personalized
    
    return {
        "avg_personalized": avg_personalized,
        "avg_non_personalized": avg_non_personalized,
        "difference": difference,
        "count": len(evaluations)
    }

def process_model_evaluations(eval_model, eval_model_folder):
    """Process all evaluations for a specific model, grouped by plan model"""
    print(f"Processing personalization evaluations for {eval_model}...")
    
    eval_files = get_evaluation_files(eval_model_folder)
    print(f"Found {len(eval_files)} personalization evaluation files for {eval_model}")
    
    # Parse all evaluation files
    evaluations = []
    for file_path, plan_model, category in eval_files:
        parsed = parse_evaluation_file(file_path, plan_model, category)
        if parsed:
            evaluations.append(parsed)
    
    print(f"Successfully parsed {len(evaluations)} personalization evaluations for {eval_model}")
    
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
                print(f"{plan_model} {difficulty}: Personalized={metrics['avg_personalized']:.1f}, Non-personalized={metrics['avg_non_personalized']:.1f}, Diff={metrics['difference']:.1f}")
        
        # Overall for this plan model
        if plan_model in by_plan_model:
            overall_metrics = calculate_metrics(by_plan_model[plan_model])
            results[f"{plan_model}_total"] = overall_metrics
            print(f"{plan_model} total: Personalized={overall_metrics['avg_personalized']:.1f}, Non-personalized={overall_metrics['avg_non_personalized']:.1f}, Diff={overall_metrics['difference']:.1f}")
    
    # Calculate overall metrics across all plan models
    overall_metrics = calculate_metrics(evaluations)
    results["total"] = overall_metrics
    print(f"Total: Personalized={overall_metrics['avg_personalized']:.1f}, Non-personalized={overall_metrics['avg_non_personalized']:.1f}, Diff={overall_metrics['difference']:.1f}")
    
    return results, evaluations

def create_improved_personalization_plots(results_data, eval_model):
    """Create plots showing total personalization results and differences"""
    
    # Define colors for models (same as evaluation script)
    model_colors = {
        'gpt': ['#1f77b4', '#4a90c2'],      # Blue (normal, slightly lighter)
        'llama': ['#ff7f0e', '#ff9a3c'],    # Orange (normal, slightly lighter)
        'deepseek': ['#2ca02c', '#4bb84b']  # Green (normal, slightly lighter)
    }
    
    # Define model names
    models = ['gpt', 'llama', 'deepseek']
    
    # Create 1x2 subplots (personalization scores and differences)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(19, 8), gridspec_kw={'width_ratios': [1.1, 0.9]}) 
    fig.suptitle(f'Personalization Results - judged by {eval_model.upper()}', fontsize=20, fontweight='bold', y=0.99)
    
    # Extract total data
    personalized_scores = []
    non_personalized_scores = []
    
    for model in models:
        key = f"{model}_total"
        if key in results_data:
            personalized_scores.append(results_data[key]["avg_personalized"])
            non_personalized_scores.append(results_data[key]["avg_non_personalized"])
        else:
            personalized_scores.append(0)
            non_personalized_scores.append(0)
    
    # SUBPLOT 1: Personalization Scores
    x = np.arange(len(models)) * 2.2
    width = 0.35
    gap = 0.2
    
    bars_personalized = ax1.bar(x - width/2 - gap/2, personalized_scores, width, 
                                color=[model_colors[model][0] for model in models], 
                                alpha=0.9)
    bars_non_personalized = ax1.bar(x + width/2 + gap/2, non_personalized_scores, width,
                                    color=[model_colors[model][1] for model in models], 
                                    alpha=0.7)
    
    # Add scores on top of bars
    for j, (bar_personalized, bar_non_personalized) in enumerate(zip(bars_personalized, bars_non_personalized)):
        height_personalized = bar_personalized.get_height()
        ax1.text(bar_personalized.get_x() + bar_personalized.get_width()/2., height_personalized + 0.1,
                f'{height_personalized:.1f}', ha='center', va='bottom', 
                fontsize=14, fontweight='bold', color='black')
        
        height_non_personalized = bar_non_personalized.get_height()
        ax1.text(bar_non_personalized.get_x() + bar_non_personalized.get_width()/2., height_non_personalized + 0.1,
                f'{height_non_personalized:.1f}', ha='center', va='bottom', 
                fontsize=14, fontweight='bold', color='black')
    
    # Formatting for first subplot
    ax1.set_ylabel('Personalization Score', fontsize=16)
    ax1.set_title('Personalization Scores', fontsize=16, fontweight='bold', pad=12)
    ax1.set_ylim(0, 11)
    ax1.set_xticks(x)
    ax1.set_xticklabels([''] * len(models))
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_xlim(x[0] - 1.0, x[-1] + 1.0) # Add space before first and after last bars
    
    # Add model name labels below first subplot
    for j, model in enumerate(models):
        if model == 'gpt':
            model_name = 'GPT'
        else:
            model_name = model.capitalize()
        
        ax1.text(x[j], -0.2, model_name, ha='center', va='top', 
                fontsize=18, fontweight='bold', color='black')

    # Create the legend with 6 items in 2 rows, 3 columns
    legend_elements = []
    for model in models:
        if model == 'gpt':
            model_name = 'GPT'
        else:
            model_name = model.capitalize()
        
        legend_elements.append(plt.Rectangle((0, 0), 1, 1, facecolor=model_colors[model][0], alpha=0.9, 
                                           label=f'{model_name} Personalized'))
        legend_elements.append(plt.Rectangle((0, 0), 1, 1, facecolor=model_colors[model][1], alpha=0.7, 
                                           label=f'{model_name} Non-personalized'))

    # Reorder legend elements to be in the desired 2-row, 3-column format
    reordered_legend_elements = [
        legend_elements[0], legend_elements[2], legend_elements[4],
        legend_elements[1], legend_elements[3], legend_elements[5]
    ]

    # Add the legend to the top-right corner of the first subplot
    ax1.legend(handles=reordered_legend_elements, loc='upper right', bbox_to_anchor=(1, 1), 
              ncol=2, fontsize=15, frameon=True, fancybox=True)
    
    # SUBPLOT 2: Difference Scores
    diff_scores = [p - n for p, n in zip(personalized_scores, non_personalized_scores)]
    
    bars_diff = ax2.bar(x, diff_scores, width * 2,
                        color=[model_colors[model][0] for model in models], 
                        alpha=0.9)
    
    # Add difference scores on top of bars
    for j, bar in enumerate(bars_diff):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{height:.1f}', ha='center', va='bottom', 
                fontsize=14, fontweight='bold', color='black')
    
    # Formatting for second subplot
    ax2.set_ylabel('Score Difference', fontsize=16)
    ax2.set_title('Difference Scores', fontsize=16, fontweight='bold', pad=12)
    ax2.set_ylim(0, 4)
    ax2.set_xticks(x)
    ax2.set_xticklabels([''] * len(models))
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_xlim(x[0] - 1.0, x[-1] + 1.0) # Add space before first and after last bars
    
    # Add model name labels below second subplot
    for j, model in enumerate(models):
        if model == 'gpt':
            model_name = 'GPT'
        else:
            model_name = model.capitalize()
        
        ax2.text(x[j], -0.06, model_name, ha='center', va='top', 
                fontsize=18, fontweight='bold', color='black')
    
    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.88, wspace=0.2)
    
    # Save chart
    chart_path = RESULTS_DIR / f"personalization_results_{eval_model}_improved.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Improved personalization chart saved to {chart_path}")

def main():
    """Main function to read personalization results and generate improved plots"""
    
    # Read Llama4 results from JSON
    print("Reading Llama4 personalization results...")
    llama_json_path = RESULTS_DIR / "personalization_results_llama4.json"
    try:
        with open(llama_json_path, 'r', encoding='utf-8') as f:
            llama_results = json.load(f)
        print("Creating improved plots for Llama4 personalization evaluations...")
        create_improved_personalization_plots(llama_results, "llama4")
    except FileNotFoundError:
        print(f"Llama4 personalization results file not found at {llama_json_path}")
    
    # Read GPT-5 results from JSON
    print("\nReading GPT-5 personalization results...")
    gpt_json_path = RESULTS_DIR / "personalization_results_gpt5.json"
    try:
        with open(gpt_json_path, 'r', encoding='utf-8') as f:
            gpt_results = json.load(f)
        print("Creating improved plots for GPT-5 personalization evaluations...")
        create_improved_personalization_plots(gpt_results, "gpt-5")
    except FileNotFoundError:
        print(f"GPT-5 personalization results file not found at {gpt_json_path}")
    
    print(f"\nImproved personalization plots generated! Results saved in {RESULTS_DIR}")

if __name__ == "__main__":
    main()