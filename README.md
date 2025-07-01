# Blood Test Report Analyser

This application provides a robust, asynchronous web API that uses a crew of AI agents to analyze blood test reports. It is built to handle concurrent requests efficiently using a task queue and to store results persistently in a database.

This document provides a summary of all bugs fixed, an overview of the system architecture, and detailed instructions for setup, usage, and API interaction.

---

## 1. Bugs Found and Fixed

The original codebase had several critical bugs that prevented it from running correctly. Here is a summary of the fixes implemented:

1.  **Dependency Conflicts:** The initial `requirements.txt` file had numerous version conflicts that made installation impossible. This was resolved by rebuilding the file with a minimal set of core dependencies and letting the `uv` package manager handle resolving the correct versions for all sub-dependencies.

2.  **Unimplemented Code:** The `tools.py` file contained placeholder classes (`NutritionTool`, `ExerciseTool`) that were not implemented. These were removed to prevent runtime errors and code confusion.

3.  **Deprecated PDF Loader:** The application used a `PDFLoader` from `langchain_community` that is no longer available, causing a crash on startup. This was fixed by replacing it with the `pypdf` library and updating the PDF reading logic.

4.  **Missing `python-multipart` Dependency:** The FastAPI server requires this library to handle file uploads, but it was missing from the requirements. It has been added, fixing server startup errors.

5.  **Missing API Key Handling:** The application would crash if the `GOOGLE_API_KEY` environment variable was not set. This was fixed by integrating `python-dotenv` to load the key from a `.env` file, which now includes a placeholder to guide the user.

6.  **Circular Import Error:** A critical bug was discovered where `main.py` and `worker.py` were trying to import from each other, causing a circular dependency that crashed the application. This was resolved by moving the core `run_crew` logic into a new, separate `crew_logic.py` file, breaking the import cycle.

---

## 2. Architecture Overview

The application has been upgraded to an asynchronous, task-based architecture to handle long-running AI analysis tasks without blocking the server.

*   **FastAPI Web Server:** Handles incoming HTTP requests. When a file is uploaded to `/analyze`, it no longer performs the analysis itself. Instead, it creates a task and sends it to the queue.
*   **Redis:** Acts as a high-speed message broker. It holds the tasks in a queue until a worker is ready to process them.
*   **Celery Worker:** This is a separate background process that listens for new tasks on the Redis queue. When a task appears, the worker picks it up and executes the time-consuming AI analysis.
*   **SQLite Database:** The results of the analysis (both successful and failed) are stored permanently in a local SQLite database file (`blood_test_analyser.db`).

This design makes the application highly scalable and responsive.

---

## 3. Setup and Usage Instructions

Follow these steps to set up the project and run all its components.

### Prerequisites
*   Python 3.8+
*   `uv` (install with `pip install uv`)
*   Docker (for running Redis)
*   `curl` (for testing the API)

### Step 1: Project Setup
1.  **Create and Activate Virtual Environment:**
    ```bash
    # Create the virtual environment in the project folder
    uv venv

    # Activate it (on Linux/macOS)
    source .venv/bin/activate
    ```

2.  **Install Dependencies:**
    ```bash
    uv pip install -r requirements.txt
    ```

3.  **Configure API Key:**
    Create a file named `.env` in the project root. Add your Google API key to it.
    ```
    GOOGLE_API_KEY="YOUR_ACTUAL_GOOGLE_API_KEY"
    ```

### Step 2: Running the Application
You need to run three services simultaneously in separate terminals.

#### Terminal 1: Start Redis
```bash
# This will start a Redis container in the background
docker run -d -p 6379:6379 --name blood-test-redis redis
```

#### Terminal 2: Start the Celery Worker
Make sure your virtual environment is activated (`source .venv/bin/activate`).
```bash
# The worker listens for tasks from the Redis queue
uv run celery -A worker.celery_app worker --loglevel=info
```
Keep this terminal open to monitor the worker logs.

#### Terminal 3: Start the FastAPI Server
Make sure your virtual environment is activated here as well.
```bash
# This starts the main web application
uvicorn main:app --host 0.0.0.0 --port 8000
```
The API is now live and ready for requests.

---

## 4. API Documentation

### Submit Analysis Task
This endpoint accepts a PDF file, creates an analysis task, and returns a task ID.

*   **Endpoint:** `/analyze`
*   **Method:** `POST`
*   **Request Body:** `multipart/form-data`
    *   `file` (file, **required**): The blood test report in PDF format.
    *   `query` (string, optional): A specific question for the AI. Defaults to "Summarise my Blood Test Report".

*   **Example `curl` Request:**
    ```bash
    curl -X POST \
      -F "file=@/path/to/your/report.pdf" \
      -F "query=Are there any abnormalities in my report?" \
      http://localhost:8000/analyze
    ```

*   **Success Response (200 OK):**
    ```json
    {
      "task_id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8"
    }
    ```

### Retrieve Analysis Result
This endpoint retrieves the status and result of a previously submitted task.

*   **Endpoint:** `/results/{task_id}`
*   **Method:** `GET`

*   **Example `curl` Request:**
    ```bash
    # Replace {task_id} with the ID you received from the /analyze endpoint
    curl http://localhost:8000/results/{task_id}
    ```

*   **Response While Pending:**
    ```json
    {
      "task_id": "...",
      "status": "pending",
      "result": null,
      "error": null
    }
    ```

*   **Response When Completed:**
    ```json
    {
      "task_id": "...",
      "status": "completed",
      "result": "(The full text of the AI's analysis will be here)",
      "error": null
    }
    ```
