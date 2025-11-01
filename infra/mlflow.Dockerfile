# /infra/mlflow.Dockerfile

# Start from the official MLflow image
FROM ghcr.io/mlflow/mlflow:latest

# Install the Postgres driver
# We use -binary as it's lighter and doesn't require build tools
RUN pip install psycopg2-binary