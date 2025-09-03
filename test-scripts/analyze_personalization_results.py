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

def create_improved_personalization_plots(results_data, eval_model):
    """Create improved personalization plots matching evaluation results style"""
    
    # Define colors for models (same as evaluation script)
    model_colors = {
        'gpt': ['#1f77b4', '#4a90c2'],      # Blue (normal, slightly lighter)
        'llama': ['#ff7f0e', '#ff9a3c'],    # Orange (normal, slightly lighter)
        'deepseek': ['#2ca02c', '#4bb84b']  # Green (normal, slightly lighter)
    }
    
    # Define difficulty levels and model names
    difficulties = ['easy', 'medium', 'hard']
    models = ['gpt', 'llama', 'deepseek']
    
    # Create 2x4 subplot layout (2 rows, 4 columns)
    fig, axes = plt.subplots(2, 4, figsize=(24, 12))
    fig.suptitle(f'Personalization Results - {eval_model.upper()}', fontsize=20, fontweight='bold', y=0.98)
    
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
    fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 0.96), 
              ncol=3, fontsize=15, frameon=True, fancybox=True, shadow=True)
    
    # ROW 1: Actual Scores
    for i, difficulty in enumerate(difficulties):
        ax = axes[0, i]
        
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
        
        # Create bars with increased spacing between models
        x = np.arange(len(models)) * 1.5  # Increase space between model groups
        width = 0.35
        gap = 0.2  # Increase gap between personalized and non-personalized bars
        
        # Create bars
        bars_personalized = ax.bar(x - width/2 - gap/2, personalized_scores, width, 
                                   color=[model_colors[model][0] for model in models], 
                                   alpha=0.9)
        bars_non_personalized = ax.bar(x + width/2 + gap/2, non_personalized_scores, width,
                                       color=[model_colors[model][1] for model in models], 
                                       alpha=0.7)
        
        # Add scores on top of bars and model names on bars
        for j, (bar_personalized, bar_non_personalized, model) in enumerate(zip(bars_personalized, bars_non_personalized, models)):
            # Format model name properly
            if model == 'gpt':
                model_name = 'GPT'
            else:
                model_name = model.capitalize()
            
            # Add score on top of personalized bar
            height_personalized = bar_personalized.get_height()
            ax.text(bar_personalized.get_x() + bar_personalized.get_width()/2., height_personalized + 0.1,
                   f'{height_personalized:.1f}', ha='center', va='bottom', 
                   fontsize=12, fontweight='bold', color='black')
            
            # Add score on top of non-personalized bar
            height_non_personalized = bar_non_personalized.get_height()
            ax.text(bar_non_personalized.get_x() + bar_non_personalized.get_width()/2., height_non_personalized + 0.1,
                   f'{height_non_personalized:.1f}', ha='center', va='bottom', 
                   fontsize=12, fontweight='bold', color='black')
        
        # Formatting
        ax.set_ylabel('Personalization Score', fontsize=12)
        ax.set_ylim(0, 11)  # Scores are out of 10
        ax.set_xticks(x)
        ax.set_xticklabels([''] * len(models))  # Remove x-axis labels since model names are below figure
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add category title outside and above the figure in dark gray
        ax.set_title(f'{difficulty.upper()}', fontsize=16, fontweight='bold', pad=5, color='#333333')
        
        # Add model name labels below the figure
        for j, model in enumerate(models):
            if model == 'gpt':
                model_name = 'GPT'
            else:
                model_name = model.capitalize()
            
            # Position label below the figure with large font
            ax.text(x[j], -0.5, model_name, ha='center', va='top', 
                   fontsize=18, fontweight='bold', color='black')
    
    # TOTAL for Row 1
    ax = axes[0, 3]
    
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
    
    # Create bars with increased spacing between models
    x = np.arange(len(models)) * 1.5
    width = 0.35
    gap = 0.2
    
    bars_personalized = ax.bar(x - width/2 - gap/2, personalized_scores, width, 
                               color=[model_colors[model][0] for model in models], 
                               alpha=0.9)
    bars_non_personalized = ax.bar(x + width/2 + gap/2, non_personalized_scores, width,
                                   color=[model_colors[model][1] for model in models], 
                                   alpha=0.7)
    
    # Add scores on top of bars
    for j, (bar_personalized, bar_non_personalized, model) in enumerate(zip(bars_personalized, bars_non_personalized, models)):
        # Format model name properly
        if model == 'gpt':
            model_name = 'GPT'
        else:
            model_name = model.capitalize()
        
        # Add score on top of personalized bar
        height_personalized = bar_personalized.get_height()
        ax.text(bar_personalized.get_x() + bar_personalized.get_width()/2., height_personalized + 0.1,
               f'{height_personalized:.1f}', ha='center', va='bottom', 
               fontsize=12, fontweight='bold', color='black')
        
        # Add score on top of non-personalized bar
        height_non_personalized = bar_non_personalized.get_height()
        ax.text(bar_non_personalized.get_x() + bar_non_personalized.get_width()/2., height_non_personalized + 0.1,
               f'{height_non_personalized:.1f}', ha='center', va='bottom', 
               fontsize=12, fontweight='bold', color='black')
    
    # Formatting
    ax.set_ylabel('Personalization Score', fontsize=12)
    ax.set_ylim(0, 11)
    ax.set_xticks(x)
    ax.set_xticklabels([''] * len(models))
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add category title
    ax.set_title('TOTAL', fontsize=16, fontweight='bold', pad=5, color='#333333')
    
    # Add model name labels below the figure
    for j, model in enumerate(models):
        if model == 'gpt':
            model_name = 'GPT'
        else:
            model_name = model.capitalize()
        
        ax.text(x[j], -0.5, model_name, ha='center', va='top', 
               fontsize=18, fontweight='bold', color='black')
    
    # ROW 2: Difference Bars
    for i, difficulty in enumerate(difficulties):
        ax = axes[1, i]
        
        # Extract difference data for this difficulty
        differences = []
        
        for model in models:
            key = f"{model}_{difficulty}"
            if key in results_data:
                differences.append(results_data[key]["avg_difference"])
            else:
                differences.append(0)
        
        # Create difference bars
        x = np.arange(len(models)) * 1.5
        
        # Color bars based on difference (positive = model color, negative = lighter)
        bar_colors = []
        for j, (diff, model) in enumerate(zip(differences, models)):
            if diff >= 0:
                bar_colors.append(model_colors[model][0])  # Normal color for positive
            else:
                bar_colors.append(model_colors[model][1])  # Lighter color for negative
        
        bars_diff = ax.bar(x, differences, color=bar_colors, alpha=0.9)
        
        # Add difference values on top of bars
        for j, (bar, diff, model) in enumerate(zip(bars_diff, differences, models)):
            if model == 'gpt':
                model_name = 'GPT'
            else:
                model_name = model.capitalize()
            
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + (0.05 if height >= 0 else -0.15),
                   f'{height:.1f}', ha='center', va='bottom' if height >= 0 else 'top', 
                   fontsize=12, fontweight='bold', color='black')
        
        # Formatting
        ax.set_ylabel('Score Difference', fontsize=12)
        ax.set_ylim(0, 4)  # Scale from 0 to 4 for differences
        ax.set_xticks(x)
        ax.set_xticklabels([''] * len(models))
        ax.grid(True, alpha=0.3, axis='y')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        # Add category title
        ax.set_title(f'DIFFERENCE ({difficulty.upper()})', fontsize=16, fontweight='bold', pad=5, color='#333333')
        
        # Add model name labels below the figure
        for j, model in enumerate(models):
            if model == 'gpt':
                model_name = 'GPT'
            else:
                model_name = model.capitalize()
            
            ax.text(x[j], -0.3, model_name, ha='center', va='top', 
                   fontsize=18, fontweight='bold', color='black')
    
    # TOTAL DIFF for Row 2
    ax = axes[1, 3]
    
    # Extract total difference data
    differences = []
    
    for model in models:
        key = f"{model}_total"
        if key in results_data:
            differences.append(results_data[key]["avg_difference"])
        else:
            differences.append(0)
    
    # Create difference bars
    x = np.arange(len(models)) * 1.5
    
    # Color bars based on difference
    bar_colors = []
    for j, (diff, model) in enumerate(zip(differences, models)):
        if diff >= 0:
            bar_colors.append(model_colors[model][0])
        else:
            bar_colors.append(model_colors[model][1])
    
    bars_diff = ax.bar(x, differences, color=bar_colors, alpha=0.9)
    
    # Add difference values on top of bars
    for j, (bar, diff, model) in enumerate(zip(bars_diff, differences, models)):
        if model == 'gpt':
            model_name = 'GPT'
        else:
            model_name = model.capitalize()
        
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + (0.05 if height >= 0 else -0.15),
               f'{height:.1f}', ha='center', va='bottom' if height >= 0 else 'top', 
               fontsize=12, fontweight='bold', color='black')
    
    # Formatting
    ax.set_ylabel('Score Difference', fontsize=12)
    ax.set_ylim(0, 4)
    ax.set_xticks(x)
    ax.set_xticklabels([''] * len(models))
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    
    # Add category title
    ax.set_title('DIFFERENCE (TOTAL)', fontsize=16, fontweight='bold', pad=5, color='#333333')
    
    # Add model name labels below the figure
    for j, model in enumerate(models):
        if model == 'gpt':
            model_name = 'GPT'
        else:
            model_name = model.capitalize()
        
        ax.text(x[j], -0.3, model_name, ha='center', va='top', 
               fontsize=18, fontweight='bold', color='black')
    
    # Adjust layout and save
    plt.tight_layout()
    plt.subplots_adjust(top=0.85, hspace=0.4, wspace=0.2)
    
    # Save chart
    chart_path = RESULTS_DIR / f"personalization_results_{eval_model}_improved.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Improved personalization chart saved to {chart_path}")

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
        print(f"Llama4 results file not found at {llama_json_path}")
    
    # Read GPT-5 results from JSON
    print("\nReading GPT-5 personalization results...")
    gpt_json_path = RESULTS_DIR / "personalization_results_gpt5.json"
    try:
        with open(gpt_json_path, 'r', encoding='utf-8') as f:
            gpt_results = json.load(f)
        print("Creating improved plots for GPT-5 personalization evaluations...")
        create_improved_personalization_plots(gpt_results, "gpt-5")
    except FileNotFoundError:
        print(f"GPT-5 results file not found at {gpt_json_path}")
    
    print(f"\nImproved personalization plots generated! Results saved in {RESULTS_DIR}")

if __name__ == "__main__":
    main()