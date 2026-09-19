import argparse
import json
import sys
import urllib.request
from pathlib import Path

from week6.evaluations.scoring import answer_matches

QUESTIONS_PATH = Path(__file__).parent / "questions.json"


def ask(base_url: str, question: str, limit: int = 5) -> dict:
    """POST one question to /ask/ and return the parsed JSON reply."""

    request = urllib.request.Request(
        f"{base_url}/ask/",
        data=json.dumps({"question": question, "limit": limit}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def run(base_url: str, minimum_accuracy: float | None) -> int:
    """Ask every question, score retrieval and answer separately, print a report."""

    cases = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    retrieval_passes = 0
    answer_passes = 0
    end_to_end_passes = 0

    for case in cases:
        result = ask(base_url, case["question"])

        retrieved_ids = {citation["source_id"] for citation in result["citations"]}
        retrieval_ok = case["source_id"] in retrieved_ids
        answer_ok = result["supported"] and answer_matches(case, result["answer"])
        passed = retrieval_ok and answer_ok

        retrieval_passes += retrieval_ok
        answer_passes += answer_ok
        end_to_end_passes += passed

        status = "PASS" if passed else "FAIL"
        print(
            f"{status} {case['id']}: {result['answer']!r} "
            f"(retrieval: {retrieval_ok}, answer: {answer_ok})"
        )

    total = len(cases)
    print()
    print(f"Retrieval accuracy:  {retrieval_passes}/{total} = {retrieval_passes / total:.0%}")
    print(f"Answer accuracy:     {answer_passes}/{total} = {answer_passes / total:.0%}")
    print(f"End-to-end accuracy: {end_to_end_passes}/{total} = {end_to_end_passes / total:.0%}")

    if minimum_accuracy is not None and end_to_end_passes / total < minimum_accuracy:
        print(f"Below the minimum accuracy of {minimum_accuracy:.0%}.")
        return 1
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate the /ask/ endpoint.")
    parser.add_argument("--base-url", default="http://localhost:8001")
    parser.add_argument("--minimum-accuracy", type=float, default=None)
    args = parser.parse_args()
    sys.exit(run(args.base_url, args.minimum_accuracy))