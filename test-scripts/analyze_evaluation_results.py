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

def create_improved_plots(results_data, eval_model):
    """Create improved 4-subfigure plots for evaluation results"""
    
    # Define colors for models (normal and slightly lighter versions)
    model_colors = {
        'gpt': ['#1f77b4', '#4a90c2'],      # Blue (normal, slightly lighter)
        'llama': ['#ff7f0e', '#ff9a3c'],    # Orange (normal, slightly lighter)
        'deepseek': ['#2ca02c', '#4bb84b']  # Green (normal, slightly lighter)
    }
    
    # Define difficulty levels and model names
    difficulties = ['easy', 'medium', 'hard']
    models = ['gpt', 'llama', 'deepseek']
    
    # Create 1x4 subplot layout (single row)
    fig, axes = plt.subplots(1, 4, figsize=(24, 8))
    fig.suptitle(f'Quality Evaluation - judged by {eval_model.upper()}', fontsize=20, fontweight='bold', y=0.92)
    
    # Create a horizontal legend at the top
    legend_elements = []
    for model in models:
        if model == 'gpt':
            model_name = 'GPT'
        else:
            model_name = model.capitalize()
        
        # Add micro and macro pass entries for each model
        legend_elements.append(plt.Rectangle((0, 0), 1, 1, facecolor=model_colors[model][0], alpha=0.9, 
                                           label=f'{model_name} Micro Pass'))
        legend_elements.append(plt.Rectangle((0, 0), 1, 1, facecolor=model_colors[model][1], alpha=0.7, 
                                           label=f'{model_name} Macro Pass'))
    
    # Add the legend at the top in two rows with larger text (positioned between title and category names)
    fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 0.88), 
              ncol=3, fontsize=18, frameon=True, fancybox=True)
    
    # Plot each difficulty level in first 3 subplots
    for i, difficulty in enumerate(difficulties):
        ax = axes[i]
        
        # Extract data for this difficulty
        micro_scores = []
        macro_scores = []
        
        for model in models:
            key = f"{model}_{difficulty}"
            if key in results_data:
                micro_scores.append(results_data[key]["micro_pass"])
                macro_scores.append(results_data[key]["macro_pass"])
            else:
                micro_scores.append(0)
                macro_scores.append(0)
        
        # Create bars with increased spacing between models
        x = np.arange(len(models)) * 1.5  # Increase space between model groups
        width = 0.35
        gap = 0.2  # Increase gap between micro and macro bars
        
        # Create bars with updated labels
        bars_micro = ax.bar(x - width/2 - gap/2, micro_scores, width, 
                           color=[model_colors[model][0] for model in models], 
                           alpha=0.9)
        bars_macro = ax.bar(x + width/2 + gap/2, macro_scores, width,
                           color=[model_colors[model][1] for model in models], 
                           alpha=0.7)
        
        # Add percentages on top of bars and model names below bars
        for j, (bar_micro, bar_macro, model) in enumerate(zip(bars_micro, bars_macro, models)):
            # Format model name properly
            if model == 'gpt':
                model_name = 'GPT'
            else:
                model_name = model.capitalize()
            
            # Add percentage on top of micro bar
            height_micro = bar_micro.get_height()
            ax.text(bar_micro.get_x() + bar_micro.get_width()/2., height_micro + 1,
                   f'{height_micro:.1f}%', ha='center', va='bottom', 
                   fontsize=14, fontweight='bold', color='black')
            
            # Add percentage on top of macro bar
            height_macro = bar_macro.get_height()
            ax.text(bar_macro.get_x() + bar_macro.get_width()/2., height_macro + 1,
                   f'{height_macro:.1f}%', ha='center', va='bottom', 
                   fontsize=14, fontweight='bold', color='black')
        
        # Formatting
        ax.set_ylabel('Pass Rate (%)', fontsize=16)
        ax.set_ylim(0, 105)  # Bars start from 0 (bottom) and go up to just above 100%
        ax.set_xticks(x)
        ax.set_xticklabels([''] * len(models))  # Remove x-axis labels since model names are below figure
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add category title outside and above the figure (closer) in dark gray
        ax.set_title(f'{difficulty.upper()}', fontsize=16, fontweight='bold', pad=5, color='#333333')
        
        # Add model name labels below the figure (closer to axis)
        for j, model in enumerate(models):
            if model == 'gpt':
                model_name = 'GPT'
            else:
                model_name = model.capitalize()
            
            # Position label below the figure with large font (closer to axis)
            ax.text(x[j], -3, model_name, ha='center', va='top', 
                   fontsize=18, fontweight='bold', color='black')
        
    
    # Plot total results in fourth subplot
    ax = axes[3]
    
    # Extract total data
    micro_scores = []
    macro_scores = []
    
    for model in models:
        key = f"{model}_total"
        if key in results_data:
            micro_scores.append(results_data[key]["micro_pass"])
            macro_scores.append(results_data[key]["macro_pass"])
        else:
            micro_scores.append(0)
            macro_scores.append(0)
    
    # Create bars with increased spacing between models
    x = np.arange(len(models)) * 1.5  # Increase space between model groups
    width = 0.35
    gap = 0.2  # Increase gap between micro and macro bars
    
    bars_micro = ax.bar(x - width/2 - gap/2, micro_scores, width, 
                       color=[model_colors[model][0] for model in models], 
                       alpha=0.9)
    bars_macro = ax.bar(x + width/2 + gap/2, macro_scores, width,
                       color=[model_colors[model][1] for model in models], 
                       alpha=0.7)
    
    # Add percentages on top of bars and model names below bars
    for j, (bar_micro, bar_macro, model) in enumerate(zip(bars_micro, bars_macro, models)):
        # Format model name properly
        if model == 'gpt':
            model_name = 'GPT'
        else:
            model_name = model.capitalize()
        
        # Add percentage on top of micro bar
        height_micro = bar_micro.get_height()
        ax.text(bar_micro.get_x() + bar_micro.get_width()/2., height_micro + 1,
               f'{height_micro:.1f}%', ha='center', va='bottom', 
               fontsize=14, fontweight='bold', color='black')
        
        # Add percentage on top of macro bar
        height_macro = bar_macro.get_height()
        ax.text(bar_macro.get_x() + bar_macro.get_width()/2., height_macro + 1,
               f'{height_macro:.1f}%', ha='center', va='bottom', 
               fontsize=14, fontweight='bold', color='black')
    
    # Formatting
    ax.set_ylabel('Pass Rate (%)', fontsize=16)
    ax.set_ylim(0, 105)  # Bars start from 0 (bottom) and go up to just above 100%
    ax.set_xticks(x)
    ax.set_xticklabels([''] * len(models))  # Remove x-axis labels since model names are below figure
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add category title outside and above the figure (closer) in dark gray
    ax.set_title('TOTAL', fontsize=16, fontweight='bold', pad=5, color='#333333')
    
    # Add model name labels below the figure (closer to axis)
    for j, model in enumerate(models):
        if model == 'gpt':
            model_name = 'GPT'
        else:
            model_name = model.capitalize()
        
        # Position label below the figure with large font (closer to axis)
        ax.text(x[j], -3, model_name, ha='center', va='top', 
               fontsize=18, fontweight='bold', color='black')
    
    
    # Adjust layout and save with proper spacing for single row layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.70, wspace=0.2)
    
    # Save chart in both PNG and PDF formats
    chart_path_png = RESULTS_DIR / f"evaluation_results_{eval_model}.png"
    chart_path_pdf = RESULTS_DIR / f"evaluation_results_{eval_model}.pdf"
    plt.savefig(chart_path_png, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(chart_path_pdf, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Chart saved to {chart_path_png} and {chart_path_pdf}")

def main():
    """Main function to read evaluation results and generate improved plots"""
    
    # Read Llama4 results from JSON
    print("Reading Llama4 evaluation results...")
    llama_json_path = RESULTS_DIR / "evaluation_results_llama4.json"
    try:
        with open(llama_json_path, 'r', encoding='utf-8') as f:
            llama_results = json.load(f)
        print("Creating plots for Llama4 evaluations...")
        create_improved_plots(llama_results, "llama4")
    except FileNotFoundError:
        print(f"Llama4 results file not found at {llama_json_path}")
    
    # Read GPT-5 results from JSON
    print("\nReading GPT-5 evaluation results...")
    gpt_json_path = RESULTS_DIR / "evaluation_results_gpt5.json"
    try:
        with open(gpt_json_path, 'r', encoding='utf-8') as f:
            gpt_results = json.load(f)
        print("Creating plots for GPT-5 evaluations...")
        create_improved_plots(gpt_results, "gpt-5")
    except FileNotFoundError:
        print(f"GPT-5 results file not found at {gpt_json_path}")
    
    print(f"\nPlots generated! Results saved in {RESULTS_DIR}")

if __name__ == "__main__":
    main()