import os
import mlflow
import pandas as pd
from .celery_config import celery_app

# IMPORTANT: The worker is a separate process.
# It must load its own copy of the model.
MODEL_NAME = "nimbus-classifier"
MODEL_ALIAS = "production"

# Pre-load the model when the worker starts
# Note: MLFLOW_TRACKING_URI must be set in the worker's environment!
os.environ["MLFLOW_TRACKING_URI"] = "http://127.0.0.1:5000"
model = mlflow.pyfunc.load_model(model_uri=f"models:/{MODEL_NAME}@{MODEL_ALIAS}")


@celery_app.task(bind=True)
def process_batch(self, batch_data: list[dict]):
    """
    Asynchronous task to process a batch of predictions.
    """
    try:
        self.update_state(state='PROGRESS', meta={'current': 0, 'total': len(batch_data)})

        input_df = pd.DataFrame(batch_data)
        predictions = model.predict(input_df)

        # In a real app, you'd save this to Postgres.
        # For the MVP, returning the result is fine.
        results = predictions.tolist()
        return {"status": "Complete", "count": len(results), "results": results}

    except Exception as e:
        self.update_state(state='FAILURE', meta={'exc': str(e)})
        return {"status": "Failed", "error": str(e)}