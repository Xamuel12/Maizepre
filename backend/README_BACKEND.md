# Backend (Flask)

## Requirements

- Python 3.10+

## Setup

From project root (`MAIZE PREDICTION`):

### 1) Create virtual env

```bat
python -m venv .venv
```

### 2) Activate

```bat
.venv\Scripts\activate
```

### 3) Install dependencies

```bat
pip install -r requirements.txt
```

## Run server

```bat
python app.py
```

Server will run at: http://127.0.0.1:5000

## Dataset placement

Put your CSV dataset file into:

- `data/maize_yield.csv`

The training pipeline expects a header row.

## Training

Train and save artifacts:

```bat
python -m backend.ml.train
```
