import io
import os
from contextlib import asynccontextmanager

import mlflow.pyfunc
import numpy as np
import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image

from src.food11.data import CLASSES

# Force all torch.load calls to map tensors to CPU (model was saved on MPS)
_orig_torch_load = torch.load
def _cpu_torch_load(*args, **kwargs):
    kwargs.setdefault("map_location", torch.device("cpu"))
    return _orig_torch_load(*args, **kwargs)
torch.load = _cpu_torch_load

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Loaded at startup, unless SKIP_MODEL is set (tests, CI smoke test)
model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    if not os.environ.get("SKIP_MODEL"):
        model = mlflow.pyfunc.load_model("models:/food11@champion")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    image = Image.open(io.BytesIO(await file.read())).convert("RGB")
    image = image.resize((224, 224))
    array = np.array(image, dtype=np.float32) / 255.0
    array = np.transpose(array, (2, 0, 1))
    array = np.expand_dims(array, axis=0)
    prediction = model.predict(array)
    class_id = int(np.argmax(prediction))
    confidence = float(np.max(prediction))
    return {
        "class_id": class_id,
        "category": CLASSES[class_id],
        "confidence": confidence,
    }