# 🌩️ Nimbus API — ML Model Serving on Google Cloud

This repository contains the complete implementation and deployment architecture for **Nimbus API**, a cloud‑native machine‑learning inference system deployed on **Google Cloud Run**, powered by **MLflow**, **Cloud SQL**, **Memorystore (Redis)**, and a **background worker VM**.

This README provides:

* 📌 Project Overview
* 🏗️ Full Architecture Diagram & Explanation
* 🧪 API Testing Guide (Predict + Batch Jobs)
* 📸 Reference Screenshots (from your provided images)

---

## 📌 1. Project Overview

Nimbus API is a **scalable model‑serving system** built using the following principles:

* Serverless public interface for synchronous predictions
* Dedicated background processors for async batch jobs
* Model registry & lifecycle tracking via MLflow
* Redis queue for reliable message passing
* GCS bucket for model artifacts
* Cloud SQL for MLflow metadata

Its purpose is to provide **reliable, production‑ready ML inference** while keeping compute costs optimized.

---

## 🏗️ 2. Architecture Overview

Below is the complete cloud architecture used in the Nimbus API deployment.

### 🔹 **High‑Level Components**

| Component                | Platform         | Purpose                                             |
| ------------------------ | ---------------- | --------------------------------------------------- |
| **Cloud Run API**        | Cloud Run        | Public inference service, handles /predict & /batch |
| **Background VM**        | Compute Engine   | Hosts MLflow + Celery Worker                        |
| **MLflow Server**        | Docker on VM     | Model Registry + Tracking Server                    |
| **Celery Worker**        | Docker on VM     | Executes async batch prediction jobs                |
| **Cloud SQL**            | Google Cloud SQL | Stores all MLflow metadata                          |
| **Memorystore Redis**    | Redis            | Broker + backend for async jobs                     |
| **Cloud Storage Bucket** | GCS              | Stores versioned model files                        |

---

## 🔄 3. System Data Flow

### **A. Synchronous Prediction Flow (/v1/predict)**

1. Client sends JSON input to Cloud Run.
2. Cloud Run queries MLflow for latest `@production` model.
3. Model is downloaded from GCS.
4. Cloud Run performs prediction.
5. Response is returned instantly.

### **B. Asynchronous Batch Flow (/v1/batch)**

1. Client submits multiple items.
2. Cloud Run creates a job and pushes it to Redis.
3. Returns a `job_id` immediately.
4. Celery Worker picks the job, loads model, processes predictions.
5. Worker stores results back in Redis.
6. Client fetches results using `GET /v1/batch/<job_id>`.

---

## 🖼️ 4. Sample Tests

### ✔️ MLflow Production Model

<img width="1917" height="854" alt="Screenshot 2025-11-13 235557" src="https://github.com/user-attachments/assets/dab07a8a-fedc-468e-aed0-731f3bb9c897" />

### ✔️ Example: Synchronous Prediction

<img width="1274" height="710" alt="Screenshot 2025-11-13 235430" src="https://github.com/user-attachments/assets/ef6c76c7-2d51-4691-82fb-98fbc7e71e81" />

### ✔️ Example: Batch Job Submit

<img width="1276" height="697" alt="Screenshot 2025-11-13 235508" src="https://github.com/user-attachments/assets/6689d3b3-bfcb-4bfc-a4cc-bc28630b257c" />

### ✔️ Example: Batch Job Result

<img width="1263" height="705" alt="Screenshot 2025-11-13 235540" src="https://github.com/user-attachments/assets/7dc56536-88d1-4d5b-9f74-fc300505495e" />

---

## 🧪 5. API Testing Guide (Postman)

Base URL:

```
https://api-<your-cloud-run-service>.run.app
```

---

### ✔️ A. Health Check

```
GET /
```

Response:

```json
{
  "status": "NimbusAPI is running."
}
```

---

### ✔️ B. Synchronous Prediction

```
POST /v1/predict
```

Body:

```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```

Response:

```json
{ "prediction": 0 }
```

---

### ✔️ C. Submit Batch Job

```
POST /v1/batch
```

Body:

```json
[
  {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  },
  {
    "sepal_length": 7.7,
    "sepal_width": 3.0,
    "petal_length": 6.1,
    "petal_width": 2.3
  }
]
```

Response:

```json
{
  "job_id": "<uuid>",
  "status": "PENDING"
}
```

---

### ✔️ D. Retrieve Batch Results

```
GET /v1/batch/<job_id>
```

Response:

```json
{
  "job_id": "<uuid>",
  "status": "SUCCESS",
  "result": [
    { "prediction": 0 },
    { "prediction": 2 }
  ]
}
```

---

## 📦 7. Repository Structure

````txt
NIMBUSAPI/
│
├── service/          # FastAPI API + Celery worker
├── model/            # ML models
├── mlflow/           # MLflow config
├── infra/            # Deployment scripts
├── docker-compose.yml
└── requirements.txt
````

---

## 🏁 Final Notes

* The system is fully modular and can scale independently.
* VM is used only for components that cannot be serverless (Celery, MLflow).
* Everything else is pay‑per‑use.

