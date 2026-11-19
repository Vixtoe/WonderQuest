import asyncio
import json
from pathlib import Path
from engine import agent_graph


EXPECTED_SOLVED = {
    "correct": True,
    "incorrect": False,
    "partial": False,
}


def build_initial_state(goal: str, attempt: str) -> dict:
    return {
        "task_goal": goal,
        "user_attempt": attempt,
        "hint_level": 0,
        "is_solved": False,
        "responses": [],
        "tool_log": [],
    }


async def run_evaluation(puzzles_path: str = "puzzles.json") -> None:
    data = json.loads(Path(puzzles_path).read_text(encoding="utf-8"))

    total_cases = 0
    matched_cases = 0
    wrong_predictions = 0
    errors = 0

    by_type = {
        "correct": {"total": 0, "matched": 0, "wrong": 0, "errors": 0},
        "incorrect": {"total": 0, "matched": 0, "wrong": 0, "errors": 0},
        "partial": {"total": 0, "matched": 0, "wrong": 0, "errors": 0},
    }

    for puzzle in data:
        puzzle_id = puzzle["id"]
        goal = puzzle["goal"]
        attempts = puzzle["attempts"]

        for label, attempt_text in attempts.items():
            expected = EXPECTED_SOLVED[label]
            total_cases += 1
            by_type[label]["total"] += 1

            state_in = build_initial_state(goal=goal, attempt=attempt_text)

            try:
                result = await agent_graph.ainvoke(state_in)
                actual = bool(result.get("is_solved"))

                if actual == expected:
                    matched_cases += 1
                    by_type[label]["matched"] += 1
                else:
                    wrong_predictions += 1
                    by_type[label]["wrong"] += 1
                    print(
                        f"[MISMATCH] {puzzle_id} ({label}): "
                        f"attempt={attempt_text!r} | expected={expected} | got={actual}"
                    )
            except Exception as exc:
                errors += 1
                by_type[label]["errors"] += 1
                print(
                    f"[ERROR] {puzzle_id} ({label}): "
                    f"attempt={attempt_text!r} | {type(exc).__name__}: {exc}"
                )

    evaluated_without_error = total_cases - errors
    accuracy = (matched_cases / evaluated_without_error * 100) if evaluated_without_error else 0.0
    overall_rate = (matched_cases / total_cases * 100) if total_cases else 0.0

    print("\n--- Evaluation Summary ---")
    print(f"Total test cases:    {total_cases}")
    print(f"Matched expected:    {matched_cases}")
    print(f"Wrong predictions:   {wrong_predictions}")
    print(f"Errors (caught):     {errors}")
    print(f"Accuracy (non-err):  {accuracy:.1f}% ({matched_cases}/{evaluated_without_error})")
    print(f"Pass rate (all):     {overall_rate:.1f}% ({matched_cases}/{total_cases})")

    print("\n--- Breakdown by Attempt Type ---")
    for label, stats in by_type.items():
        non_err = stats["total"] - stats["errors"]
        acc = (stats["matched"] / non_err * 100) if non_err else 0.0
        print(
            f"{label:10s} | matched={stats['matched']:2d}/{stats['total']:2d} "
            f"| wrong={stats['wrong']:2d} | errors={stats['errors']:2d} | acc={acc:5.1f}%"
        )


if __name__ == "__main__":
    asyncio.run(run_evaluation())