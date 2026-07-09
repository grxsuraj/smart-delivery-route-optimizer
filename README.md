# Smart Delivery Route Optimizer

C++ Dijkstra engine + SQL delay history + Flask API + n8n automated alerts.

## Folder Structure
```
route_optimizer/
├── schema.sql              # SQL schema + sample data (10 Indian cities)
├── app.py                  # Flask entry point - just creates app, registers routes
├── routes.py               # ALL API endpoints (/api/cities, /api/find-route) - THIS is your API code
├── db.py                   # Database connection + query helper functions
├── route_engine_loader.py  # Loads C++ engine, falls back to Python Dijkstra if not built
├── cpp/
│   ├── dijkstra.cpp        # C++ Dijkstra module (pybind11)
│   └── setup.py            # Build script for the C++ module
├── templates/
│   └── index.html          # Frontend page structure only
├── static/
│   ├── style.css           # All CSS styling
│   └── script.js            # All frontend JS logic (fetch calls, graph drawing)
└── n8n_workflow.json        # Importable n8n workflow
```

### Where's the API code specifically?
`routes.py` — every `@api.route(...)` function in that file is one API endpoint.
`app.py` just wires it up; it has no endpoint logic itself anymore.

## Setup Steps (in order)

### 1. Install Python dependencies
```bash
pip install flask requests pybind11 --break-system-packages
```

### 2. Create the SQLite database from schema
```bash
sqlite3 route_optimizer.db < schema.sql
```

### 3. Build the C++ module (optional but recommended)
```bash
cd cpp
python setup.py build_ext --inplace
cd ..
```
> If this step fails or you skip it, `app.py` automatically falls back to a
> pure-Python Dijkstra implementation — the app still runs, just without the
> C++ engine. Good to know so a build issue doesn't block your demo.

### 4. Run n8n (separate terminal)
```bash
npx n8n
```
Open `http://localhost:5678` → Import `n8n_workflow.json` → Activate the workflow.
Confirm the webhook URL matches `N8N_WEBHOOK_URL` in `app.py` (default:
`http://localhost:5678/webhook/delay-alert`).

### 5. Run the Flask app
```bash
python app.py
```
Open `http://localhost:5000` in your browser.

## How It Works (for interview explanation)
1. User selects source + destination on the frontend, clicks "Check Route"
2. Flask builds the graph from SQL `routes` table and calls the C++ Dijkstra
   engine (via pybind11) to get the shortest time-path
3. Flask queries `delay_history` for each edge in that path and sums the
   average historical delay
4. If total predicted delay > threshold (20 min), Flask calls the n8n
   webhook automatically
5. n8n checks severity (>= 40 min = critical vs moderate) and routes to the
   appropriate email alert, while Flask logs the alert in the SQL `alerts`
   table regardless of whether n8n is reachable

## Notes
- Data is manually curated (not a live dataset) — kept intentionally small
  and scoped for a placement/internship project.
- If n8n isn't running, the app still works — alerts are logged in SQL with
  status `n8n_unreachable` instead of failing the whole request.
