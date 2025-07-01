from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import uuid

from worker import run_analysis_task
import models, database

# Create the database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Blood Test Report Analyser")

# Dependency to get the database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Blood Test Report Analyser API is running"}

@app.post("/analyze")
async def analyze_blood_report(
    file: UploadFile = File(...),
    query: str = Form(default="Summarise my Blood Test Report"),
    db: Session = Depends(get_db)
):
    """
    Analyze blood test report and provide comprehensive health recommendations.
    This endpoint now returns a task ID for polling the result.
    """
    
    # Generate unique filename to avoid conflicts
    file_id = str(uuid.uuid4())
    file_path = f"data/blood_test_report_{file_id}.pdf"
    
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Validate query
        if query=="" or query is None:
            query = "Summarise my Blood Test Report"
            
        # Dispatch the analysis task to the Celery worker
        task = run_analysis_task.delay(query=query.strip(), file_path=file_path)

        # Save initial task state to the database
        db_result = models.AnalysisResult(id=task.id, status="pending")
        db.add(db_result)
        db.commit()
        
        return {"task_id": task.id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing blood report: {str(e)}")

@app.get("/results/{task_id}")
async def get_results(task_id: str, db: Session = Depends(get_db)):
    """
    Fetch the results of an analysis task from the database.
    """
    result = db.query(models.AnalysisResult).filter(models.AnalysisResult.id == task_id).first()
    if result:
        return {"task_id": result.id, "status": result.status, "result": result.result, "error": result.error}
    else:
        raise HTTPException(status_code=404, detail="Task not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
