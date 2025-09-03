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
    """Create improved personalization plots with 4x2 layout"""
    
    # Define colors for models (same as evaluation script)
    model_colors = {
        'gpt': ['#1f77b4', '#4a90c2'],      # Blue (normal, slightly lighter)
        'llama': ['#ff7f0e', '#ff9a3c'],    # Orange (normal, slightly lighter)
        'deepseek': ['#2ca02c', '#4bb84b']  # Green (normal, slightly lighter)
    }
    
    # Define difficulty levels and model names
    difficulties = ['easy', 'medium', 'hard']
    models = ['gpt', 'llama', 'deepseek']
    
    # Create 4x2 subplot layout (4 rows, 2 columns)
    fig, axes = plt.subplots(4, 2, figsize=(16, 24))
    fig.suptitle(f'Personalization Results - {eval_model.upper()}', fontsize=20, fontweight='bold', y=0.93)
    
    # Create a horizontal legend at the top
    legend_elements = []
    for model in models:
        if model == 'gpt':
            model_name = 'GPT'
        else:
            model_name = model.capitalize()
        
        # Add personalized and non-personalized entries for each model
        legend_elements.append(plt.Rectangle((0, 0), 1, 1, facecolor=model_colors[model][0], alpha=0.9, 
                                           label=f'{model_name} Personalized'))
        legend_elements.append(plt.Rectangle((0, 0), 1, 1, facecolor=model_colors[model][1], alpha=0.7, 
                                           label=f'{model_name} Non-personalized'))
    
    # Add the legend at the top in two rows with larger text
    fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 0.91), 
              ncol=3, fontsize=15, frameon=True, fancybox=True, shadow=True)
    
    # Function to create a subplot
    def create_subplot(ax, title, personalized_scores, non_personalized_scores, is_diff=False):
        # Create bars with increased spacing between models
        x = np.arange(len(models)) * 1.5
        width = 0.35
        gap = 0.2
        
        if not is_diff:
            # Regular bars for actual scores
            bars_personalized = ax.bar(x - width/2 - gap/2, personalized_scores, width, 
                                       color=[model_colors[model][0] for model in models], 
                                       alpha=0.9)
            bars_non_personalized = ax.bar(x + width/2 + gap/2, non_personalized_scores, width,
                                           color=[model_colors[model][1] for model in models], 
                                           alpha=0.7)
            
            # Add scores on top of bars
            for j, (bar_personalized, bar_non_personalized) in enumerate(zip(bars_personalized, bars_non_personalized)):
                height_personalized = bar_personalized.get_height()
                ax.text(bar_personalized.get_x() + bar_personalized.get_width()/2., height_personalized + 0.1,
                       f'{height_personalized:.1f}', ha='center', va='bottom', 
                       fontsize=12, fontweight='bold', color='black')
                
                height_non_personalized = bar_non_personalized.get_height()
                ax.text(bar_non_personalized.get_x() + bar_non_personalized.get_width()/2., height_non_personalized + 0.1,
                       f'{height_non_personalized:.1f}', ha='center', va='bottom', 
                       fontsize=12, fontweight='bold', color='black')
            
            ax.set_ylabel('Personalization Score', fontsize=12)
            ax.set_ylim(0, 11)
        else:
            # Single bars for differences
            diff_scores = [p - n for p, n in zip(personalized_scores, non_personalized_scores)]
            bars = ax.bar(x, diff_scores, width * 2 + gap, 
                         color=[model_colors[model][0] for model in models], 
                         alpha=0.9)
            
            # Add difference scores on top of bars
            for j, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                       f'{height:.1f}', ha='center', va='bottom', 
                       fontsize=12, fontweight='bold', color='black')
            
            ax.set_ylabel('Score Difference', fontsize=12)
            ax.set_ylim(0, 4)
        
        # Formatting
        ax.set_xticks(x)
        ax.set_xticklabels([''] * len(models))
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=5, color='#333333')
        
        # Add model name labels below the figure
        for j, model in enumerate(models):
            if model == 'gpt':
                model_name = 'GPT'
            else:
                model_name = model.capitalize()
            
            # Adjust label position based on scale
            y_pos = -0.5 if not is_diff else -0.2
            ax.text(x[j], y_pos, model_name, ha='center', va='top', 
                   fontsize=18, fontweight='bold', color='black')
    
    # ROWS 1-2: Actual Scores
    subplot_positions = [(0, 0), (0, 1), (1, 0), (1, 1)]  # easy, medium, hard, total
    
    # Easy, Medium, Hard
    for i, difficulty in enumerate(difficulties):
        row, col = subplot_positions[i]
        ax = axes[row, col]
        
        # Extract data for this difficulty
        personalized_scores = []
        non_personalized_scores = []
        
        for model in models:
            key = f"{model}_{difficulty}"
            if key in results_data:
                personalized_scores.append(results_data[key]["avg_personalized"])
                non_personalized_scores.append(results_data[key]["avg_non_personalized"])
            else:
                personalized_scores.append(0)
                non_personalized_scores.append(0)
        
        create_subplot(ax, difficulty.upper(), personalized_scores, non_personalized_scores)
    
    # Total
    ax = axes[1, 1]
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
    
    create_subplot(ax, 'TOTAL', personalized_scores, non_personalized_scores)
    
    # Add "Difference Scores" title between rows 2 and 3 with gaps
    fig.text(0.5, 0.42, 'Difference Scores', ha='center', va='center', 
             fontsize=18, fontweight='bold', color='#333333', 
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    
    # ROWS 3-4: Difference Scores
    diff_positions = [(2, 0), (2, 1), (3, 0), (3, 1)]  # easy, medium, hard, total
    
    # Easy, Medium, Hard differences
    for i, difficulty in enumerate(difficulties):
        row, col = diff_positions[i]
        ax = axes[row, col]
        
        # Extract data for this difficulty
        personalized_scores = []
        non_personalized_scores = []
        
        for model in models:
            key = f"{model}_{difficulty}"
            if key in results_data:
                personalized_scores.append(results_data[key]["avg_personalized"])
                non_personalized_scores.append(results_data[key]["avg_non_personalized"])
            else:
                personalized_scores.append(0)
                non_personalized_scores.append(0)
        
        create_subplot(ax, f'DIFFERENCE ({difficulty.upper()})', personalized_scores, non_personalized_scores, is_diff=True)
    
    # Total difference
    ax = axes[3, 1]
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
    
    create_subplot(ax, 'DIFFERENCE (TOTAL)', personalized_scores, non_personalized_scores, is_diff=True)
    
    # Manually position subplots with proper spacing (no tight_layout)
    subplot_height = 0.16
    subplot_width = 0.38
    left_x = 0.08
    right_x = 0.54
    
    row_positions = [
        0.69,  # Row 1 (Easy, Medium) - moved up for more space
        0.48,  # Row 2 (Hard, Total) - increased gap from row 1
        # Large gap here for "Difference Scores" heading
        0.22,  # Row 3 (Difference Easy, Medium) - moved down for gap from heading
        0.01   # Row 4 (Difference Hard, Total) - increased gap from row 3
    ]
    
    # Set positions manually
    axes[0, 0].set_position([left_x, row_positions[0], subplot_width, subplot_height])   # Easy
    axes[0, 1].set_position([right_x, row_positions[0], subplot_width, subplot_height])  # Medium
    axes[1, 0].set_position([left_x, row_positions[1], subplot_width, subplot_height])   # Hard
    axes[1, 1].set_position([right_x, row_positions[1], subplot_width, subplot_height])  # Total
    axes[2, 0].set_position([left_x, row_positions[2], subplot_width, subplot_height])   # Diff Easy
    axes[2, 1].set_position([right_x, row_positions[2], subplot_width, subplot_height])  # Diff Medium
    axes[3, 0].set_position([left_x, row_positions[3], subplot_width, subplot_height])   # Diff Hard
    axes[3, 1].set_position([right_x, row_positions[3], subplot_width, subplot_height])  # Diff Total
    
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