import json
import os
from pathlib import Path
import shutil
from loguru import logger

EVALUATION_EXAMPLES = r"D:\Projects\OSWorld-MA\evaluation_examples\examples"
RESULT_BASE_DIR = r"D:\Projects\OSWorld-MA\results\pyautogui\screenshot"

with open(r"D:\Projects\OSWorld-MA\evaluation_examples\test_nogdrive.json", "r") as f:
    _ground_truth = json.load(f)

def get_tasks(model: str, remove_corrupted: bool = False):
    _results_dir = os.path.join(RESULT_BASE_DIR, model)
    tasks = []
    for domain_dir in Path(_results_dir).iterdir():
        if domain_dir.is_file():
            continue
        domain = domain_dir.name
        for task_dir in domain_dir.iterdir():
            task_id = task_dir.name
            
            # read results.json from summary/results.json
            results_file = task_dir / "summary" / "results.json"
            if not results_file.exists():
                if remove_corrupted:
                    shutil.rmtree(task_dir)
                    print(f"Removed corrupted task dir: {task_dir}")
                    continue
                raise ValueError(f"Results file not found in: {task_dir}")
            
            with open(results_file, "r") as f:
                results = json.load(f)
                results = results[0]

            score = results.get("score", -1)
            try:
                score_num = float(score)
            except (TypeError, ValueError):
                score_num = -1.0

            # read traj.jsonl
            with open(task_dir / "traj.jsonl", "r") as f:
                trajs = [json.loads(line) for line in f.readlines()]
            
            task_eval = {
                "domain": domain,
                "task_id": task_id,
                "success": score_num > 0.5,
                "score": score,
                "steps": len(trajs),
                "usage_input_tokens": results.get("usage", {}).get("input_tokens", 0),
                "usage_output_tokens": results.get("usage", {}).get("output_tokens", 0),
                "usage_cached_input_tokens": results.get("usage", {}).get("cached_input_tokens", 0),
                "error_reasons": results.get("error_reasons", []),
                "trajectories": trajs,
            }
            tasks.append(task_eval)

    for task in tasks:
        if task["domain"] not in _ground_truth:
            logger.warning(f"Warning: Domain {task['domain']} not found in ground truth.")
            continue   
        if task["task_id"] not in _ground_truth[task["domain"]]:
            logger.warning(f"Warning: Task ID {task['task_id']} in domain {task['domain']} not found in ground truth.")
            continue

    count_gt_tasks = sum(len(_ground_truth[domain]) for domain in _ground_truth)
    if len(tasks) < count_gt_tasks:
        logger.warning(f"Warning: Only {len(tasks)} tasks found, but {count_gt_tasks} expected from ground truth.")

    return tasks

def delete_run(model: str, task_id: str):
    _results_dir = os.path.join(RESULT_BASE_DIR, model)
    for domain_dir in Path(_results_dir).iterdir():
        if domain_dir.is_file():
            continue
        task_dir = domain_dir / task_id
        if task_dir.exists() and task_dir.is_dir():
            shutil.rmtree(task_dir)
            print(f"Deleted task run: {task_id} under model {model}")
            return
    print(f"Task run not found for deletion: {task_id} under model {model}")
