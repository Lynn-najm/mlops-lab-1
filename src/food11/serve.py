import os
import io
import mlflow.pyfunc
import numpy as np
from PIL import Image
from fastapi import FastAPI, UploadFile, File

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