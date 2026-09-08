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

The actual dataset is not stored on GitHub because the data folders are ignored by Git. Instead, Git contains DVC pointer files such as:

```text
data.dvc
data_sample.dvc

These files contain metadata about the tracked data, including the path and hash used by DVC to identify the correct version.

The full Food-11 dataset was too large to upload successfully to DagsHub because of repeated connection timeouts. To still test the DVC workflow, I created a smaller data_sample folder containing one image and tracked it with DVC.

I then pushed only this sample using:

uv run dvc push data_sample.dvc

This worked successfully. The pointer file is stored on GitHub, while the actual image is stored in the DVC remote on DagsHub.

##Question 7: In a completely new temporary folder clone your github repo. Do you see the data folder? What dvc command is needed to get the data folder?

After cloning the GitHub repository into a new temporary folder, the actual data file was not present.

Git only cloned the repository files and the DVC pointer file data_sample.dvc.

To retrieve the tracked image from the DVC remote, I used:

uv run dvc pull data_sample.dvc

After running this command, the data_sample folder was created and the tracked image 0_0.jpg appeared inside it.

This shows that Git stores the DVC pointer file, while DVC retrieves the actual data from the remote storage.

## Question 8: Do you still see the new folders you created? food11_processed and food11_processed_mini?

After checking out the older commit and running:

```bash
dvc checkout

the food11_processed and food11_processed_mini folders were no longer present. Only the older food11_raw data remained.

This happened because the older Git commit contains an older version of data.dvc, and dvc checkout restores the local data to match that version.

After switching back to the main branch with:

git checkout main
dvc checkout

the newer data version was restored and the folders appeared again:

food11_raw
food11_processed
food11_processed_mini

This shows how Git versions the DVC pointer file, while DVC restores the corresponding version of the actual data.