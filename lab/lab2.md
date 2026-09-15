# Lab 2 - Model Training and Experiment Tracking with MLflow

## Question 1: Look at `pyproject.toml` and `uv.lock`. What changed?

`pyproject.toml` now contains the new dependencies needed for this lab, such as MLflow, PyTorch, torchvision, and scikit-learn.

`uv.lock` was also updated with the exact versions of these packages and their dependencies.

---


## Question 2: What is `--backend-store-uri` used for? What is `--default-artifact-root` used for? What is the difference between the metadata MLflow stores and the artifacts it stores?

`--backend-store-uri` tells MLflow where to store information about the experiments and runs.


In this lab, that information is stored in:

```text
mlflow.db
--default-artifact-root tells MLflow where to store files produced by the runs.
In this lab, they are stored in:
mlruns/
Metadata is information about the run, such as parameters and metrics.

Artifacts are actual files, such as the trained model.

## Question 3: Why shouldn't `mlflow.db` and `mlruns/` be tracked by git, and why shouldn't they be tracked by dvc either?

`mlflow.db` and `mlruns/` are local outputs created by MLflow while running experiments.

They should not be tracked by Git because they are generated files, not source code.

They also should not be tracked by DVC because they are experiment results and metadata, not the dataset itself. MLflow already manages them.

## Question 4: What happens the first time you call `set_experiment` with a name that doesn't exist yet? Check the MLflow UI.

If the experiment does not exist, MLflow creates it automatically.

After running:

```python
mlflow.set_experiment("food11")
a new experiment called food11 appeared in the MLflow UI.


## Question 5: What is the difference between `mlflow.log_param` and `mlflow.log_metric`? Why does `log_metric` take a `step` argument and `log_param` doesn't?

`mlflow.log_param` stores a setting used for the run, such as the learning rate or batch size.

`mlflow.log_metric` stores a result produced during training, such as loss or accuracy.

Metrics can change during training, so `step` is used to show at which epoch the value was recorded. Parameters usually stay fixed for the whole run, so they do not need a step.

## Question 6: Open the run in the MLflow UI. Find the params, the metric charts, and the logged model artifact. Where does the model artifact actually live on disk?

The MLflow UI shows the parameters used for the run, the metrics produced during training, and the logged model.

The actual model is stored as a file inside the local `mlruns/` directory.

For my run, the model file was stored at:

```text
mlruns/1/models/m-48d0573ace0a4738b77619b4d244406e/artifacts/data/model.pth
So the MLflow UI only displays the run information, while the real model artifact is stored on disk inside mlruns/.

## Question 7: In the MLflow UI, open the `food11` experiment. Select these runs and click "Compare". Which learning rate gave the best `val_accuracy`? Is higher always better?

The best learning rate was `0.0001`, with a validation accuracy of about `0.715`.

A higher learning rate is not always better. In my runs, `0.01` performed much worse than the smaller learning rates.

## Question 8: Use the parallel coordinates plot on the compare page to look at `lr`, `batch_size` and `val_accuracy` together. What pattern do you see?

The best validation accuracy came from the smallest learning rate, `0.0001`.
The learning rate `0.01` performed much worse than the smaller learning rates.
For `lr = 0.001`, increasing the batch size from `32` to `64` improved the validation accuracy.

## Question 9: Sort the runs table by `val_accuracy` descending. Which run is the best one? Note its run ID, you'll need it in the next lab.

The best run was `blushing-pig-715`.

It used:

- `learning_rate = 0.0001`
- `batch_size = 32`

Its validation accuracy was about `0.715`.

The run ID is:

```text
1770b794037c4b299bfc2efc3b5314f2