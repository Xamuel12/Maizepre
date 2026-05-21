# ML Backend (Train + Predict)

## Dataset placement

Add your CSV here:

- `data/maize_yield.csv`

Expected columns (must match `backend/ml/config.py`):

- rainfall
- temperature
- soil_ph
- soil_n
- fertilizer_kg_ha
- planting_day_of_year
- yield (target column)

## Train

From project root:

```bat
python -m backend.ml.train
```

This will save artifacts under:

- `backend/ml/artifacts/`

## Predict

The web app calls `backend/ml/infer.py`.
Ensure artifacts exist by training first.
