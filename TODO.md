# TODO - Maize Yield Prediction Web App

- [ ] Scaffold backend (Flask) with routes: `/`, `/signup`, `/login`, `/logout`, `/predict` (GET/POST)
- [ ] Build frontend pages in `frontend/` using HTML/CSS/JS + Bootstrap
  - [ ] Home page describing the project
  - [ ] Signup page
  - [ ] Login page
  - [ ] Prediction page with input fields (rainfall, temperature, soil, fertilizer, planting date)
- [ ] Add authentication (simple session-based) for protected prediction route
- [ ] Create ML training pipeline in `backend/ml/`
  - [ ] Provide `data/` folder for dataset placement
  - [ ] Implement training script that trains models and saves artifacts
  - [ ] Implement inference code that loads saved model artifacts
- [ ] Implement prediction endpoint to call ML inference
- [ ] Add basic client-side validation + UX improvements
- [ ] Provide run instructions (create venv, install deps, run backend)
