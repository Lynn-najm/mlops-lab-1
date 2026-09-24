import os
import io
import torch
import mlflow.pyfunc
import numpy as np
from PIL import Image
from fastapi import FastAPI, UploadFile, File

# Force all torch.load calls to map tensors to CPU (model was saved on MPS)
_orig_torch_load = torch.load
def _cpu_torch_load(*args, **kwargs):
    kwargs.setdefault("map_location", torch.device("cpu"))
    return _orig_torch_load(*args, **kwargs)
torch.load = _cpu_torch_load

app = FastAPI()

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

model = mlflow.pyfunc.load_model("models:/food11@champion")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image = Image.open(io.BytesIO(await file.read())).convert("RGB")
    image = image.resize((224, 224))
    array = np.array(image, dtype=np.float32) / 255.0
    array = np.transpose(array, (2, 0, 1))
    array = np.expand_dims(array, axis=0)
    prediction = model.predict(array)
    class_id = int(np.argmax(prediction))
    confidence = float(np.max(prediction))
    return {"class_id": class_id, "confidence": confidence}