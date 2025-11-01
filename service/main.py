# --- Imports ---
import os
import mlflow
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from celery.result import AsyncResult
from .celery_config import celery_app
from .tasks import process_batch

# --- Settings ---
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

# This is the "lazy loading" placeholder.
# The model is NOT loaded on startup. It's loaded on the first request.
model = None

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"status": "NimbusAPI is running."}

@app.post("/v1/predict", response_model=ModelOutput)
def predict_sync(data: ModelInput):
    """Synchronous prediction for a single data point."""
    global model  # We are modifying the global 'model' variable

    # --- LAZY LOADING BLOCK ---
    # Check if the model is already loaded in memory.
    if model is None:
        print("Model is not loaded. Attempting to load...")
        try:
            # This is the line that connects to MLflow.
            # It only runs ONCE on the first API call.
            model = mlflow.pyfunc.load_model(model_uri=f"models:/{MODEL_NAME}@{MODEL_ALIAS}")
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            # If it fails (e.g., model not trained), send an error.
            # The server will stay running.
            return {"error": "Model is not ready or not found. Please train and promote a model."}
    # --- END LAZY LOADING ---

    # If we are here, the 'model' variable is loaded.
    # Convert Pydantic model to DataFrame
    input_df = pd.DataFrame([data.model_dump()])
    prediction = model.predict(input_df)

    return {"prediction": int(prediction[0])}

@app.post("/v1/batch")
def start_batch_job(data: List[ModelInput]):
    """Asynchronously process a batch of predictions."""
    data_dicts = [item.model_dump() for item in data]
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
