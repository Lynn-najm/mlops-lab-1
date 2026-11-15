Question 1:
A unit test should check my code, not the infrastructure around it. Loading the real model from the MLflow server can fail even when my code is correct: (1) the MLflow server is down or unreachable — on a CI runner there is no server at all, so load_model crashes before any assertion runs; (2) the champion alias was moved or the model version deleted, so the test loads a different model or none; (3) it's slow, because downloading and loading torch weights takes far longer than a unit test should. A fake model avoids all of this: the test is fast, offline and reproducible, and it checks what is actually mine (decoding the image, building the JSON).

Question 2:
It proves that my API code works end to end around the model: the image upload is decoded and resized, the prediction array is read correctly (argmax, max), the class id is mapped to the right name, and the JSON has the expected fields with a confidence between 0 and 1. It does not prove the model is any good: the fake always answers "Bread", so the test would pass even if the real model predicted randomly. It also doesn't prove the real model loads from MLflow, that it accepts the input shape my code builds, or that its output format matches what the fake returns.

Question 3:
The check "no image appears in two splits" caught it (the content hash of the copied file matched a training file). A train/test duplicate is more dangerous because it fails silently: a corrupted image crashes the training script, so I notice and fix it immediately, while a duplicate lets everything run normally. The model is then tested on a photo it already saw in training, so the test accuracy is inflated and I believe the model is better than it really is, and I might promote and ship it based on a wrong number. This dataset actually has this problem already: 35 identical images across splits in the mini set (611 in the full set).

Question 4:
(1) In the CI workflow, after pulling the data onto the runner with dvc pull from a remote the runner can reach (DagsHub or cloud storage, not a local folder), or run it on a small sample dataset committed to the repo, so it still runs without the full data. (2) In the data preparation / training pipeline on the machine that has the data, right after data.py produces the dataset and before train.py starts (for example as a DVC stage or a pre-train step), so bad data stops the pipeline before any training time is wasted.

Question 5:
With needs: test, if a unit test fails the smoke job is skipped (not run at all), so no time is wasted building a Docker image for code that is already known to be broken, and the run stops at the first red step. Without needs, both jobs would start at the same time on separate runners; smoke would still build and probe the container even though tests failed, and the run would show one job red and one green, which is confusing. Jobs run in parallel by default, and needs is what turns them into an ordered pipeline.

Question 6:
The first run took 2m 08s (test 23s, smoke 1m 37s) and the second run 2m 07s (test 20s, smoke 1m 41s). Only the test job got a little faster: setup-uv with enable-cache saves the downloaded packages after the first run, so the second run restores them from the cache instead of downloading them again (uv sync is the step that benefits). The smoke job did not get faster because docker build starts from scratch on a new runner each time, with no layer cache, so it reinstalls everything including torch. Since smoke is most of the total time, the whole run barely changed.

Question 7:
The commit SHA identifies exactly which code is inside an image, so any running container can be traced back to one commit, and the tag never changes meaning. "latest" is a moving label: it points to whatever was pushed last. Example: on Monday both the server and my laptop pull latest and get the same code; on Tuesday I push a fix, and a machine that pulls now gets the new code while the server, which still has the Monday image cached, keeps running the old one. Same tag, different code, and I can't tell which is which. With SHA tags I can also roll back by redeploying an older SHA.

Question 8:
The default permissions of GITHUB_TOKEN can be broad (write access to the repo contents and more). Declaring permissions explicitly follows least privilege: the push job only needs to read the code and write packages, nothing else. If a step were compromised (a malicious third-party action or a dependency running in the job), a token with write access to everything could push commits or modify workflows and code, tamper with releases, or delete or overwrite packages. With only contents: read and packages: write, the damage is limited to what the job legitimately needs.

Question 9:
The pull request page shows the checks as failing: ci / test is red, smoke and push are skipped, and the checks are marked "Required". The Merge pull request button is greyed out, so I could not merge, even though I own the repository. For a team this changes a lot compared to "everybody runs the tests on their laptop before pushing": the rule no longer depends on people remembering or being honest, the tests run in the same clean environment every time (not "works on my machine"), and broken code physically cannot reach main. Everyone also sees the result on the pull request, so reviews start from a known-good state.

Question 10:
v1 (accuracy 0.5046) was the first model, so there was no champion to compare with and it was promoted automatically. v2 (lr 0.000001, accuracy 0.1141) was rejected: the champion v1 had 0.5046 and the required margin was 2 x se = 0.0302, so v2 needed at least 0.5348; it got the challenger alias and champion stayed on v1. v3 (lr 0.0003, 8 epochs, accuracy 0.6615) was promoted because 0.6615 >= 0.5046 + 0.0302; champion now points to v3. My test split (mini evaluation) has 1096 images, so se = sqrt(0.5046 x 0.4954 / 1096) = 0.0151 and 2 x se = 0.0302, i.e. about 3 accuracy points: a candidate must be about 3 points better than the champion to replace it, because a smaller difference could be pure chance on a test set of this size.

Question 11:
(1) Host MLflow somewhere the runner can reach, for example the hosted MLflow server that DagsHub provides for the repository, put its URL and token in GitHub secrets, and run promote.py in a GitHub Actions job, triggered after training (a workflow_dispatch button, a schedule, or a workflow that runs when training finishes). (2) Keep MLflow on my machine and run promote.py automatically at the end of the training pipeline there, for example as the last step of a script or a DVC stage after train.py, or through a self-hosted GitHub runner installed on my laptop so that the workflow can reach localhost.

Question 12:

CODE PATH (decides the CODE VERSION = git commit SHA)

    [human]  edit code on a branch, git push the branch, open a pull request
        |
        v
    [auto]   GitHub Actions on the pull request:
             test job  : ruff + pytest (unit tests with a fake model)
             smoke job : docker build, start container with SKIP_MODEL=1, curl /health
        |
        v
    [auto]   branch protection: merge button is blocked unless test and smoke are green
        |
        v
    [human]  clicks "Merge pull request" into main
        |
        v
    [auto]   push job (main only): build image, push ghcr.io/lynn-najm/mlops-lab-1:<commit SHA>
        |
        v
    [human]  pulls that image (or docker compose up) -> running container

MODEL PATH (decides the MODEL VERSION = the `champion` alias)

    [human]  runs train.py on my laptop (GPU/MPS), MLflow logs the run and test_accuracy
        |
        v
    [human]  registers the model in the MLflow UI -> new version n
        |
        v
    [human runs the command, auto decision]  promote.py --version n
             gate: accuracy >= champion + 2 x se  -> alias `champion` moves, else `challenger`
             the decision and both accuracies are written as tags on the version
        |
        v
    [human]  docker compose restart inference -> the container re-reads models:/food11@champion

Where each version is decided:
- code version: the commit SHA, set by git and used by CI as the image tag (automatic).
- model version: the `champion` alias, moved only by the gate in promote.py.

Still manual / not covered: training, registering the model, running promote.py, restarting the container, and the data check (validate_data.py), which CI cannot run because the data lives in DVC, not in GitHub.

