<div align="center">
  <h1>🌍 POLKA (basic)</h1>
  <h3>Hybrid Early Warning System for Political Risk</h3>

  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.x" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/XGBoost-F37626?style=for-the-badge&logo=xgboost&logoColor=white" alt="XGBoost" />
  <img src="https://img.shields.io/badge/Machine%20Learning-Data%20Science-success?style=for-the-badge" alt="Machine Learning" />

  <p><em>An analytical and engineering project integrating Data Science, API development (Backend), and Machine Learning to predict the political and economic stability indicators of countries.</em></p>
</div>

---
## 🎯 Project Overview
The primary goal of the project is to build a hybrid decision-making system capable of early warning regarding the risk of political destabilization. The system forecasts the exact score of a political regime indicator, categorizes the country into an official regime type, and warns about the direction of its transformation (democratic development, stability, or authoritarian regress).

The Machine Learning task is formalized as a two-stage approach (Regression + Rule-based Classification):
* **Predictive Layer (ML Regression):** Predicts the exact value of the target variable (*EIU Democracy Index* on a 0-10 scale) for the year t+1 based on multidimensional historical data. The main predictive engine is the ensemble XGBoost algorithm. Equation: `Y_{t+1}=f(X_t, X_{t-1},...)`.
* **Strategic Layer (Expert System):** Calculates the predicted dynamic of change (ΔY) and assigns the country to one of three risk classes based on hard cutoff thresholds:
  * 🔴 **Class 1 (Crisis / Authoritarian Regress):** `ΔY ≤ -0.5` (Significant regime collapse).
  * 🟢 **Class 0 (Stability):** `-0.5 < ΔY < 0.5` (No drastic changes).
  * 🔵 **Class 2 (Democratic Development):** `ΔY ≥ 0.5` (Positive transformation).
* **Regime Classification:** The system assigns the predicted score to global EIU categories: *Full democracies (8-10)*, *Flawed democracies (6-8)*, *Hybrid regimes (4-6)*, and *Authoritarian regimes (0-4)*.
* To prove its value, the ML model's performance is strictly compared against a Naive Baseline model.

## 🏗️ System Architecture (Data Pipeline)
The project features a fully automated, modern data flow:
* 📥 **Data Collection & Cleaning:** Fetching raw data from 8 different sources (including GDP, press freedom, and corruption indicators). Data merging and standardization are handled using `pandas` (`reduce` and `outer pd.merge`).
* ⚙️ **Backend & Data Storage (FastAPI + SQL):** An automated Python "Robot" batches the cleaned data and sends it via HTTP `POST` requests to a custom API. The API calculates a custom indicator, creates a backup in the cloud/Data Lake (Azurite), and loads the data into a relational SQL database.
* 🧠 **Machine Learning Model:** The ML script strictly bypasses local CSV files, fetching the latest integrated data directly from the SQL database via API `GET` requests. JSON payloads are dynamically converted into NumPy matrices for model training.

## 📊 Dataset & Features
Data is ingested directly from the automated pipeline, guaranteeing consistency.
* **Volume:** Spans 220 countries. The ML model utilizes data from approx. 2000–2025, resulting in ~20,000 complete training records.
* **Target Variable:** *EIU Democracy Index*.
* **9 Selected Indicators:**
  * 💵 **Economic:** Gross Domestic Product (GDP).
  * 🤝 **Social:** World Press Freedom Index, Absence of Violence Index, Civil Liberties Index, Human Rights Index.
  * 🏛️ **Political:** Corruption Perception Index, Electoral Integrity Index, Democracy Index.
* **Preprocessing:** Compressed using the SymLog algorithm and Min-Max scaling (0-1).
* **Note:** Noise and outliers are intentionally preserved, as economic spikes often represent real-world crises.

## 🛠️ Technologies (Tech Stack)
* **Language:** Python 3.x
* **Data Processing:** Pandas, NumPy, functools
* **Backend:** FastAPI, Uvicorn, Pydantic
* **Database / Storage:** SQL (SQLite/PostgreSQL), Azure Blob Storage (Azurite)
* **Machine Learning:** Scikit-Learn, XGBoost

## 📁 Repository Structure

| File | Description |
| :--- | :--- |
| 🧹 `data_analysis.py` | Data cleaning scripts and Exploratory Data Analysis (EDA). |
| 🤖 `api_download.py` | Automated robot sending data to the API. |
| ⚡ `main.py` | Main FastAPI server file. |
| 🗄️ `sql.py` | SQL database model definitions (SQLAlchemy). |
| ☁️ `blob_service.py` | Local data upload (Azure Blob Storage integration). |
| 🛠️ `setup.py` | Creating local server (Azurite). |
| ⚙️ `config.py` | Configuration file containing XGBoost hyperparameters, feature lists, and thresholds. |
| 🧠 `model_pipeline.py` | Main Machine Learning script (XGBoost training, prediction, and evaluation). |

## 🚀 How to run the project locally?

### 1. Start the API Server
In the terminal, navigate to the project folder and run the local server:
```bash
python -m uvicorn main:app --reload
```

The API will be available at http://127.0.0.1:8000. Interactive Swagger documentation can be found at /docs.

### 2. Data Ingestion
Open the data_analysis.ipynb notebook and run all cells. At the end, the script will automatically connect to the API, send the cleaned historical data for all countries, and load it into the SQL database.

### 3. Run the Prediction Model
Execute the main prediction script:

```
python model_pipeline.py
```

The script will load parameters from the config file, fetch the integrated data directly from the API (/countries endpoint), train the XGBoost model, and print the evaluation reports to the console.

## 📈 Evaluation Metrics
1. Due to the hybrid nature of the system, performance is evaluated on multiple layers to ensure strict business alignment:

2. Numerical Precision: Evaluated using MAE (Mean Absolute Error) to check regression accuracy against a naive persistence baseline.

3. Strategic Effectiveness: Because missing a crisis is significantly more costly than a false alarm, the ultimate metric for the system is Recall (Sensitivity) for the "Crisis" class.

4. Confusion Matrix: Used for visual assessment of systemic errors.

5. Explainable AI (XAI): Generates Feature Importance charts to identify which macro-indicators drive model decisions.





