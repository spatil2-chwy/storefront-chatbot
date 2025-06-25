````markdown
## Setup

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
````

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Load initial data into the database:**

   ```bash
   # from the project root (where `src/` lives)
   python -m src.scripts.load_data
   ```

## Running the Server

```bash
uvicorn src.main:app --reload --host localhost --port 8000
```

...

````

Load the data:

```bash
python -m src.scripts.load_data
````
