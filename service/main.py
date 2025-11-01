# FASTPI

from typing import List
from .celery_config import celery_app
from .tasks import process_batch
from celery.result import AsyncResult

import os
import mlflow
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

# --- Settings ---
# Set the MLflow URI. In a real app, this comes from env vars.
# os.environ["MLFLOW_TRACKING_URI"] = "http://127.0.0.1:5000"
MODEL_NAME = "nimbus-classifier"
MODEL_ALIAS = "production"

# --- Pydantic Schemas for Validation ---
class ModelInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

class ModelOutput(BaseModel):
    prediction: int

# --- App and Model Loading ---
app = FastAPI(title="NimbusAPI MVP", version="1.0")

try:
    model = mlflow.pyfunc.load_model(model_uri=f"models:/{MODEL_NAME}@{MODEL_ALIAS}")
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"status": "NimbusAPI is running."}

@app.post("/v1/predict", response_model=ModelOutput)
def predict_sync(data: ModelInput):
    """Synchronous prediction for a single data point."""
    if model is None:
        return {"error": "Model is not loaded."}

    # Convert Pydantic model to DataFrame
    input_df = pd.DataFrame([data.model_dump()])
    prediction = model.predict(input_df)

    return {"prediction": int(prediction[0])}

@app.post("/v1/batch")
def start_batch_job(data: List[ModelInput]):
    """Asynchronously process a batch of predictions."""

    # Convert Pydantic models to dicts for Celery
    data_dicts = [item.model_dump() for item in data]

    # Start the background task
    task = process_batch.delay(data_dicts)
    return {"job_id": task.id, "status": "PENDING"}

@app.get("/v1/batch/{job_id}")
def get_batch_status(job_id: str):
    """Retrieve the status and result of a batch job."""
    task_result = AsyncResult(job_id, app=celery_app)

    response = {
        "job_id": job_id,
        "status": task_result.status,
        "result": task_result.result or None
    }
    return response