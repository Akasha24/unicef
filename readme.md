## How to run locally

1. Open Visual Studio Code
2. Open any folder where you want the project
3. Open the terminal in VS Code
4. Run the following command:

   git clone https://github.com/Akasha24/projects.git

5. The scripts are in the `dev` branch
6. Run the following files (individual process)

- Clone & checkout:

   ```bash
   git clone https://github.com/Akasha24/projects.git
   cd projects/unicef
   git checkout dev
   ```

- Create and activate a Python environment, then install dependencies:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # PowerShell/CMD on Windows
   pip install -r website/backend/requirements.txt
   ```

- Train model (creates `models/` and `scalers/`):

   ```bash
   # from project root
   python -m website.backend.pipeline train --districts beed
   ```

- Run a single prediction from the CLI (no server):

   ```bash
   python -m website.backend.pipeline predict --district beed --date 2026-03-28
   ```

- Start the backend API only:

   ```bash
   python -m website.backend.app
   # or: python website/backend/app.py
   ```

- Combined start (batch / PowerShell scripts):

   - `START_SERVERS.bat` — runs training, starts backend and frontend, then POSTs a test prediction for today.
   - `START_SERVERS.ps1` — same behavior for PowerShell.

- Example request (uses today's date; replace with your shell):

   - Bash/WSL:

      ```bash
      DATA=$(date +%F)
      curl -s -X POST http://localhost:5000/predict \
         -H "Content-Type: application/json" \
         -d "{\"district\":\"beed\",\"date\":\"$DATA\"}"
      ```

   - PowerShell:

      ```powershell
      $d = (Get-Date).ToString('yyyy-MM-dd')
      Invoke-RestMethod -Uri http://localhost:5000/predict -Method Post -ContentType 'application/json' -Body (@{district='beed'; date=$d} | ConvertTo-Json)
      ```

   - Python (requests):

      ```python
      import requests, datetime
      payload = {"district": "beed", "date": datetime.date.today().isoformat()}
      r = requests.post("http://localhost:5000/predict", json=payload)
      print(r.status_code)
      print(r.json())
      ```

The API returns JSON with a `predictions` array of 15 records, for example:

```json
{"predictions":[{"Day":"Day 01","Date":"2026-03-29","Predicted_Tmax":36.97}, ... ]}
```

If something fails (missing model/scaler), run the `train` command first or point to correct `models/` and `scalers/` directories when calling `predict_for_district`.