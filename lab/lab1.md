# Lab 1 - Git, DVC and Data Preparation

## Question 1: Observe the files created, what do you think they contain?

After running `uv init`, the project contains files such as `.python-version`, `pyproject.toml`, `README.md`, and the `src` folder.

- `.python-version` specifies the Python version used by the project.
- `pyproject.toml` contains the project configuration, metadata, and dependencies.
- `README.md` is used to document the project.
- `src` is where the Python source code will be placed.

---

## Question 2: What are the created files? What do you think they are used for? And which ones should be pushed to git?

Running `dvc init` creates the `.dvc` folder and the `.dvcignore` file.

The `.dvc` folder contains DVC configuration and internal files. `.dvcignore` works similarly to `.gitignore` and tells DVC which files or folders it should ignore.

The DVC configuration files and `.dvcignore` should be pushed to Git because they are small configuration files needed to reproduce the project.

The actual dataset and DVC cache should not be pushed to Git.

---

## Question 3: Where are the credentials stored? and what are the options other than `--global`? Should the credentials be pushed to github?

When using `--global`, the DVC remote credentials are stored in the user's global DVC configuration, outside the project repository.

Other options include storing configuration at the project level or locally using `--local`.

Credentials should not be pushed to GitHub because they are private and could allow someone else to access the DVC remote.

---

## Question 4: Take a look at the `.gitignore` file. Explain what happened.

After running:

```bash
dvc add data 

DVC automatically added the data folder to .gitignore.

This is because Git should not track the actual dataset. The dataset is tracked by DVC instead.

Git will only track the small DVC pointer file that describes the dataset.

## Question 5: Do you see a .dvc file? What does it contain?

Yes. A file called data.dvc is created.

It contains metadata about the tracked data folder, such as its path, size, number of files, and a hash that identifies the version of the data.

It does not contain the dataset itself. It acts as a pointer that DVC uses to know which version of the data should be downloaded.

# Question 6: You can check your main branch on the github web UI. Is the code there? Is the data there? Do you have any file that points to the data location. And what about dagshub web UI do you see the data?

The code and project files are present on GitHub.

The actual dataset is not stored on GitHub because the `data` folder is ignored by Git. Instead, Git contains the `data.dvc` file.

The `data.dvc` file contains metadata about the tracked dataset, such as its path, size, number of files and hash. DVC uses this information to identify which version of the dataset belongs to the current Git commit.

The actual dataset is supposed to be uploaded to the DVC remote on DagsHub using:

```bash
dvc push

In my case, the DagsHub upload did not complete successfully because of repeated connection timeouts and server disconnections.

##Question 7: In a completely new temporary folder clone your github repo. Do you see the data folder? What dvc command is needed to get the data folder?

After cloning the GitHub repository into a new folder, the actual data folder is not present.

This is because Git does not track the dataset itself. The repository only contains the data.dvc pointer file.

To retrieve the dataset from the DVC remote, the following command is used:

dvc pull

Since DVC is installed inside the uv environment in this project, it can also be run as:

uv run dvc pull

DVC reads the information from data.dvc and restores the correct version of the data folder from the remote storage.

Python script to prepare the image files

The raw Food-11 dataset contains three folders:

training
evaluation
validation

The category of each image is represented by the first part of its filename.

The preparation script creates two new datasets:

food11_processed
food11_processed_mini

The processed datasets are different from the raw dataset in the following ways:

The images are resized to 128x128.
The images are placed inside folders that represent their category.
The mini dataset contains at most 100 images for each category.

The resulting structure is similar to:

data/
├── food11_raw/
│   ├── training/
│   ├── evaluation/
│   └── validation/
│
├── food11_processed/
│   ├── training/
│   │   ├── Bread/
│   │   ├── Dairy product/
│   │   ├── Dessert/
│   │   ├── Egg/
│   │   ├── Fried food/
│   │   ├── Meat/
│   │   ├── Noodles-Pasta/
│   │   ├── Rice/
│   │   ├── Seafood/
│   │   ├── Soup/
│   │   └── Vegetable-Fruit/
│   ├── evaluation/
│   └── validation/
│
└── food11_processed_mini/
    ├── training/
    ├── evaluation/
    └── validation/

Pillow is added to the project using:

uv add pillow

The data preparation script is run using:

uv run python ./src/food11/data.py

After the processed datasets are created, the updated data folder is tracked again with DVC:

dvc add data

Then the new DVC pointer is committed to Git:

git add data.dvc
git commit -m "Add food11_processed and food11_processed_mini"
git push

The actual updated data would then be uploaded to the DVC remote using:

dvc push

##Question 8: Do you still see the new folders you created? food11_processed and food11_processed_mini?

After checking out an older Git commit with:

git checkout <old-commit-hash>

the data.dvc file changes to the version stored in that commit.

Then, after running:

dvc checkout

DVC updates the local dataset so that it matches the version referenced by that older data.dvc file.

If the selected commit was created before food11_processed and food11_processed_mini were added, these two folders are no longer present.

When switching back to the main branch:

git checkout main
dvc checkout

the current version of data.dvc is restored and DVC restores the newer version of the dataset, which includes food11_processed and food11_processed_mini.