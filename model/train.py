import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
import os

# Get the MLflow server address from the environment variable
# Inside Docker, this will be "http://mlflow:5000"
tracking_uri = os.environ["MLFLOW_TRACKING_URI"]
mlflow.set_tracking_uri(tracking_uri)
print(f"Connecting to MLflow at {tracking_uri}") # <-- Good logging

MODEL_NAME = "nimbus-classifier"

print("Training model...")
with mlflow.start_run() as run:
    X, y = load_iris(return_X_y=True)
    lr = LogisticRegression(max_iter=200)
    lr.fit(X, y)

    accuracy = lr.score(X, y)
    mlflow.log_metric("accuracy", accuracy)

    print(f"Accuracy: {accuracy}")

    # Log the model and register it
    mlflow.sklearn.log_model(
        sk_model=lr,
        artifact_path="model",
        registered_model_name=MODEL_NAME
    )

print(f"Model '{MODEL_NAME}' registered with run ID: {run.info.run_id}")