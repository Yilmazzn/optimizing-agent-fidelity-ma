import json
import os
from pathlib import Path


RESULT_BASE_DIR = r"D:\Projects\OSWorld-MA\results\pyautogui\screenshot"

def get_tasks(model: str):
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
