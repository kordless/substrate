import argparse
from substrate import Substrate
from substrate import ComputeText, sb
import os
import logging
import json
import random
import traceback
import time
from collections import defaultdict
import itertools

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CONFIG_DIR = os.path.expanduser('~/.config/substrate')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

def load_or_create_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            logging.info(f"Config loaded from {CONFIG_FILE}")
            return config
        else:
            api_key = input("Please enter your Substrate API key: ")
            config = {'api_key': api_key}
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
            logging.info(f"Config file created at {CONFIG_FILE}")
            return config
    except Exception as e:
        logging.error(f"Error loading or creating config: {str(e)}")
        return None

config = load_or_create_config()
if not config:
    logging.error("Failed to load or create config. Exiting.")
    exit(1)

api_key = config.get('api_key')
if not api_key:
    logging.error("API key not found in config. Exiting.")
    exit(1)

substrate = Substrate(api_key=api_key, timeout=60 * 5)

AVAILABLE_MODELS = [
    "Mistral7BInstruct",
    "Mixtral8x7BInstruct",
    "Llama3Instruct8B",
    "Llama3Instruct70B",
    "Llama3Instruct405B",
    "gpt-4o",
    "gpt-4o-mini",
    "claude-3-5-sonnet-20240620"
]

prompt = "write me a python function that displays a mandelbrot set image using matplotlib"

def run_comparison(selected_models):
    logging.info(f"Selected models: {', '.join(selected_models)}")

    start_time = time.time()
    try:
        compute_texts = [ComputeText(prompt=prompt, model=model) for model in selected_models]

        reasoning = ComputeText(
            prompt=sb.concat(
                "Reason about the strengths and weaknesses of each response. Explain which elements from each response are superior.",
                "\nPROMPT: ", prompt,
                "\nCANDIDATE RESPONSES:",
                *[f"\n{i+1}) {ct.future.text}" for i, ct in enumerate(compute_texts)]
            )
        )

        promptit = sb.concat(
                "Come up with one detailed, comprehensive, unified response using the best parts of the candidate responses, based on the evaluation. Return only the response, do not reveal the process (do not say candidate response or evaluation).",
                "\nPROMPT: ", prompt,
                "\nCANDIDATE RESPONSES:",
                *[f"\n{i+1}) {ct.future.text}" for i, ct in enumerate(compute_texts)],
                "\nEVALUATION: ", reasoning.future.text
            )
        print(promptit)
        answer = ComputeText(
            prompt=promptit
        )

        res = substrate.run(answer)
        execution_time = time.time() - start_time
        logging.info(f"Run completed successfully in {execution_time:.2f} seconds. Answer: {res.get(answer).text[:100]}...")
        return True, execution_time, tuple(selected_models)
    except Exception as e:
        execution_time = time.time() - start_time
        logging.error(f"Error occurred during run: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        logging.error(f"Models that were running: {', '.join(selected_models)}")
        return False, execution_time, tuple(selected_models)


def main():
    parser = argparse.ArgumentParser(description="Run model comparisons with Substrate.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--randomize", action="store_true", help="Randomize model selection")
    group.add_argument("--all", action="store_true", help="Use all combinations of models in order")
    group.add_argument("--models", nargs='+', choices=AVAILABLE_MODELS, help="Specify models to use (3 required)")
    parser.add_argument("--runs", type=int, default=50, help="Number of runs to perform (default: 50)")
    args = parser.parse_args()

    if args.models and len(args.models) != 3:
        parser.error("You must specify exactly 3 models when using --models")

    model_times = defaultdict(list)
    model_scores = defaultdict(float)

    NUM_RUNS = args.runs

    if args.randomize:
        model_selector = lambda: random.sample(AVAILABLE_MODELS, 3)
    elif args.all:
        all_combinations = list(itertools.combinations(AVAILABLE_MODELS, 3))
        model_selector = itertools.cycle(all_combinations).__next__
    else:  # args.models
        model_selector = lambda: args.models

    for i in range(NUM_RUNS):
        logging.info(f"Starting run {i+1}")
        start_time = time.time()
        success, execution_time, models_used = run_comparison(model_selector())
        model_times[models_used].append(execution_time)
        if not success:
            logging.warning(f"Run {i+1} failed")
        end_time = time.time()
        total_run_time = end_time - start_time
        logging.info(f"Completed run {i+1} in {total_run_time:.2f} seconds (Execution time: {execution_time:.2f} seconds)")

    logging.info("All runs completed")

    # Calculate average execution time and success rate for each combination
    combo_stats = {}
    for combo, times in model_times.items():
        avg_time = sum(times) / len(times)
        success_rate = len(times) / sum(1 for run_combo in model_times.keys() if set(run_combo) == set(combo))
        combo_stats[combo] = (avg_time, success_rate, len(times))

    # Sort combinations by average time
    sorted_combos = sorted(combo_stats.items(), key=lambda x: x[1][0])

    print("\nAll Model Combinations Performance:")
    for i, (combo, (avg_time, success_rate, num_runs)) in enumerate(sorted_combos, 1):
        print(f"{i}. Models: {', '.join(combo)}")
        print(f"   Average Time: {avg_time:.2f} seconds")
        print(f"   Success Rate: {success_rate:.2%}")
        print(f"   Number of Successful Runs: {num_runs}")
        print()

        # Award points to models based on their rank
        for model in combo:
            model_scores[model] += (len(sorted_combos) - i + 1)

    # Calculate success rate and average time for each model
    model_stats = {}
    for model in AVAILABLE_MODELS:
        participations = sum(1 for combo in model_times.keys() if model in combo)
        successful_runs = sum(len(times) for combo, times in model_times.items() if model in combo)
        total_time = sum(sum(times) for combo, times in model_times.items() if model in combo)
        
        if participations > 0:
            success_rate = successful_runs / (participations * NUM_RUNS / 3)  # Divide by 3 as each run uses 3 models
            avg_time = total_time / successful_runs if successful_runs > 0 else float('inf')
            model_stats[model] = (success_rate, avg_time)

    # Normalize scores based on success rate and average time
    max_score = max(model_scores.values())
    for model in AVAILABLE_MODELS:
        if model in model_stats:
            success_rate, avg_time = model_stats[model]
            normalized_score = (model_scores[model] / max_score) if max_score > 0 else 0
            model_scores[model] = normalized_score * 0.5 + success_rate * 0.3 + (1 / avg_time) * 0.2

    # Rank models
    ranked_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)

    print("\nIndividual Model Rankings:")
    for i, (model, score) in enumerate(ranked_models, 1):
        success_rate, avg_time = model_stats.get(model, (0, float('inf')))
        print(f"{i}. {model}")
        print(f"   Score: {score:.2f}")
        print(f"   Success Rate: {success_rate:.2%}")
        print(f"   Average Time: {avg_time:.2f} seconds")
        print()

if __name__ == "__main__":
    main()