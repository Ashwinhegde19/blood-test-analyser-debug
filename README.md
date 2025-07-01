# Blood Test Report Analyser

This application provides a web API that uses a crew of AI agents to analyze blood test reports. This document provides a summary of the fixes implemented, as well as instructions for setup and API usage.

---

## 1. Bugs Found and Fixed

Here is a detailed summary of the bugs that were identified and the corresponding changes made to the codebase to make it stable and runnable.

### Bug 1: Dependency and Installation Errors
*   **Problem:** The application could not be installed due to numerous package version conflicts in the `requirements.txt` file (e.g., `pydantic`, `opentelemetry`, `click`).
*   **Fix:** The `requirements.txt` file was completely rebuilt with a minimal set of essential, direct dependencies. The `uv` package manager is now used to correctly resolve and install all sub-dependencies, which fixed all installation errors.

### Bug 2: Unimplemented and Unused Code in `tools.py`
*   **Problem:** The `tools.py` file contained unimplemented placeholder classes (`NutritionTool`, `ExerciseTool`) and an unused `search_tool`. This could lead to runtime errors and made the code confusing.
*   **Fix:**
    *   The non-functional `NutritionTool` and `ExerciseTool` classes were removed.
    *   The unused `search_tool` was removed to clean up the codebase.

### Bug 3: Deprecated PDF Reading Logic
*   **Problem:** The code used `PDFLoader` from `langchain_community`, which is no longer available at that import path and caused the program to crash.
*   **Fix:** This was resolved by adding the `pypdf` library to `requirements.txt` and rewriting the `read_data_tool` to use `pypdf.PdfReader` for correctly reading PDF files.

### Bug 4: Missing `python-multipart` Dependency
*   **Problem:** The application would fail on startup because `python-multipart`
—a required library for FastAPI's file upload handling
—was not listed in the dependencies.
*   **Fix:** The `python-multipart` library was added to `requirements.txt`.

### Bug 5: Missing API Key Environment Variable
*   **Problem:** The application would crash if the `GOOGLE_API_KEY` was not set as an environment variable.
*   **Fix:** A `.env` file was created with a placeholder key. The application now loads this file, preventing the startup crash and guiding the user to add their own key.

---

## 2. Setup and Usage Instructions

Follow these steps to set up and run the application.

### Step 1: Install `uv`
If you don't have `uv`, you can install it via `pip`:
```bash
pip install uv
```

### Step 2: Create Virtual Environment and Install Dependencies
This will create a local virtual environment and install all required packages.
```bash
# Create the virtual environment
uv venv

# Activate the environment (on Linux/macOS)
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### Step 3: Add Your Google API Key
Create a file named `.env` in the project's root directory and add your API key like this:
```
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
```

### Step 4: Run the Application
Use `uvicorn` to start the web server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
The API will now be running and accessible at `http://localhost:8000`.

---

## 3. API Documentation

### Endpoint: `/analyze`

This endpoint analyzes a blood test report PDF and provides health recommendations based on the user's query.

*   **Method:** `POST`
*   **URL:** `http://localhost:8000/analyze`
*   **Content-Type:** `multipart/form-data`

#### Parameters:
*   `file` (file, **required**): The blood test report in PDF format.
*   `query` (string, optional): A specific question or instruction for the AI agents. If not provided, it defaults to "Summarise my Blood Test Report".

#### Example `curl` Request:
```bash
curl -X POST \
  http://localhost:8000/analyze \
  -F "file=@/path/to/your/blood_test_report.pdf" \
  -F "query=Are there any abnormalities in my report?"
```

#### Success Response (200 OK):
```json
{
  "status": "success",
  "query": "Are there any abnormalities in my report?",
  "analysis": "...",
  "file_processed": "blood_test_report.pdf"
}
```