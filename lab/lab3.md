Question 1:
A run's logged model artifact is just a file saved inside a specific experiment run — it's tied to that run and has no identity of its own. A registered model is a named, versioned entry in the Model Registry that exists independently of any run. It lets you track lineage (which run produced it), assign aliases like champion, and manage it across its lifecycle without caring about the underlying run details.

Question 2:
The model was given version 1.
Aliases like champion replaced the old Staging/Production stages. Versioning a model separately from its run lets you manage the model lifecycle independently — the run is a historical record, while the registered model is what gets served. Aliases are more flexible because they can be named freely and reassigned to any version at any time, so the serving code always references @champion without needing to know the version number.

Question 3:
Loading the model through models:/food11@champion decouples the serving code from the physical file location. The code always fetches whichever version is currently aliased as champion, so deploying a newer model only requires reassigning the alias — no code change needed. Pointing directly at a .pth file would hardcode a path that breaks the moment the file moves or a new version is trained.

Question 4:
Docker caches each layer. By copying the dependency files first and running uv sync before copying source code, the dependency install layer is only rebuilt when pyproject.toml or uv.lock changes. If you only modify serve.py, Docker reuses the cached dependency layer and only rebuilds the last two layers — making rebuilds much faster.

Question 5:
A single-stage image includes build tools, the full uv cache, and intermediate files — easily 1–2 GB. The multi-stage image only keeps the final .venv and source code, typically 200–400 MB. The biggest layers are usually the Python base image and the installed packages inside .venv.

Question 6:
Without .dockerignore, Docker sends the entire project to the daemon on every build, including data/, mlruns/, and .git/. This slows down the build significantly. The data/ folder would not break the build but would bloat the image unnecessarily. The .venv/ folder could conflict with the one built inside the image and cause subtle runtime errors.
