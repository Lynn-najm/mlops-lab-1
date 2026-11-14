"""Quality gate: move the `champion` alias to a candidate only if it is clearly better."""
import argparse
import math
import os
import sys
from pathlib import Path

from mlflow.exceptions import MlflowException

from mlflow import MlflowClient

MODEL_NAME = "food11"
METRIC = "test_accuracy"
TEST_DIRS = {
    "mini": Path("data/food11_processed_mini/evaluation"),
    "full": Path("data/food11_processed/evaluation"),
}


def run_info(client, model_version):
    """Test accuracy and dataset name of the run that produced a model version."""
    run = client.get_run(model_version.run_id)
    return run.data.metrics[METRIC], run.data.params.get("dataset", "mini")


def count_test_images(dataset):
    return sum(1 for _ in TEST_DIRS[dataset].rglob("*.jpg"))


def standard_error(p, n):
    return math.sqrt(p * (1 - p) / n)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="candidate model version number")
    args = parser.parse_args()

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5001")
    client = MlflowClient(tracking_uri=tracking_uri)

    candidate = client.get_model_version(MODEL_NAME, args.version)
    acc_candidate, dataset_candidate = run_info(client, candidate)

    try:
        champion = client.get_model_version_by_alias(MODEL_NAME, "champion")
    except MlflowException:
        champion = None

    if champion is not None and champion.version == candidate.version:
        sys.exit(f"Version {candidate.version} is already the champion.")

    if champion is None:
        acc_champion, margin, promote = None, 0.0, True
    else:
        acc_champion, dataset_champion = run_info(client, champion)
        if dataset_candidate != dataset_champion:
            print(f"WARNING: candidate trained on '{dataset_candidate}', champion on '{dataset_champion}'")
        n = count_test_images(dataset_champion)
        margin = 2 * standard_error(acc_champion, n)
        promote = acc_candidate >= acc_champion + margin

    decision = "promoted" if promote else "rejected"
    tags = {
        "gate.decision": decision,
        "gate.candidate_accuracy": f"{acc_candidate:.4f}",
        "gate.champion_accuracy": "none" if acc_champion is None else f"{acc_champion:.4f}",
        "gate.required_margin": f"{margin:.4f}",
    }
    for key, value in tags.items():
        client.set_model_version_tag(MODEL_NAME, candidate.version, key, value)

    alias = "champion" if promote else "challenger"
    client.set_registered_model_alias(MODEL_NAME, alias, candidate.version)

    print(f"candidate v{candidate.version}: {acc_candidate:.4f}")
    print(f"champion: {'none' if acc_champion is None else f'{acc_champion:.4f}'}, required margin (2 x se): {margin:.4f}")
    print(f"decision: {decision} -> alias '{alias}' now points to v{candidate.version}")


if __name__ == "__main__":
    main()
    