# Catan-Engine

We take inspiration from https://github.com/bcollazo/catanatron to make a Catan UI where you can play against our handmade AI agents. 

# Motivation:

When looking through current implementations, we found many areas of improvement which we hope to address in this repo.

# Completed Features:

# In Progress:

# To-do:
- Working Catan UI
- Catan Gym Environment
- Catan AIs

## Development

### Run tests

Option A: Using a virtual environment (recommended)

1. Create venv
   - Windows PowerShell:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\python -m pip install -U pip
     .\.venv\Scripts\python -m pip install -r requirements.txt
     .\.venv\Scripts\python -m pytest -q
     ```

2. Unix/macOS:
   ```bash
   python -m venv .venv
   . ./.venv/bin/activate
   python -m pip install -U pip
   python -m pip install -r requirements.txt
   python -m pytest -q
   ```

Option B: Without venv (not recommended)

```bash
python -m pip install -U pip
python -m pip install -r requirements.txt
python -m pytest -q
```

The tests live under `tests/` and currently cover:
- Board generation basics (tile count, desert tile, ports)
- Start-phase flow (settlement then road for same player)
- Road placement rules (connected vs. disconnected)

### Run backend (Flask API)

- Windows PowerShell:
  - Create venv and install deps (if not done):
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -U pip
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe -m pip install -e .[web]
    ```
  - Run server:
    ```powershell
    set FLASK_APP=catanatron.web
    set FLASK_RUN_HOST=0.0.0.0
    set FLASK_RUN_PORT=5001
    .\.venv\Scripts\python.exe -m flask run
    ```

- macOS/Linux:
  ```bash
  python -m venv .venv
  . ./.venv/bin/activate
  python -m pip install -U pip
  python -m pip install -r requirements.txt
  python -m pip install -e .[web]
  FLASK_APP=catanatron.web FLASK_RUN_HOST=0.0.0.0 FLASK_RUN_PORT=5001 python -m flask run
  ```

### Run UI (Vite React app)

```bash
cd ui
npm install
npm run start
```

Visit http://localhost:3000, create a game, and place initial settlements and roads using the highlighted nodes/edges. After initial placements, use the toolbar to ROLL and END your turn.