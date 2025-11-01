import os
import mlflow
import pandas as pd
from .celery_config import celery_app

# --- Settings ---
MODEL_NAME = "nimbus-classifier"
MODEL_ALIAS = "production"

# NOTE: The model is NOT loaded here on startup anymore.
# This was the line that caused the worker to crash.

@celery_app.task(bind=True)
def process_batch(self, batch_data: list[dict]):
    """
    Asynchronous task to process a batch of predictions.
    The model is "lazy loaded" inside the task.
    """
    try:
        # --- LAZY LOADING BLOCK ---
        # Load the model from MLflow *inside* the task.
        # This ensures the task only runs if the model exists.
        print("Worker is loading model...")
        model = mlflow.pyfunc.load_model(model_uri=f"models:/{MODEL_NAME}@{MODEL_ALIAS}")
        print("Worker loaded model successfully.")
        # --- END LAZY LOADING ---

        self.update_state(state='PROGRESS', meta={'current': 0, 'total': len(batch_data)})

        # Convert list of dicts to DataFrame
        input_df = pd.DataFrame(batch_data)
        
        # Get predictions
        predictions = model.predict(input_df)
        
        results = predictions.tolist()
        return {"status": "Complete", "count": len(results), "results": results}

    except Exception as e:
        # If loading fails, the task will fail and report the error.
        print(f"Worker failed to load model or predict: {e}")
        self.update_state(state='FAILURE', meta={'exc': str(e)})
        return {"status": "Failed", "error": str(e)}
