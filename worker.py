from celery import Celery
from crew_logic import run_crew
from database import SessionLocal
import models

# Configure Celery
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    task_track_started=True,
)

@celery_app.task(bind=True)
def run_analysis_task(self, query: str, file_path: str):
    """
    Celery task to run the blood test analysis crew and save the result to the database.
    """
    db = SessionLocal()
    try:
        result = run_crew(query=query, file_path=file_path)
        db_result = db.query(models.AnalysisResult).filter(models.AnalysisResult.id == self.request.id).first()
        if db_result:
            db_result.status = "completed"
            db_result.result = str(result)
            db.commit()
        return str(result)
    except Exception as e:
        db_result = db.query(models.AnalysisResult).filter(models.AnalysisResult.id == self.request.id).first()
        if db_result:
            db_result.status = "failed"
            db_result.error = str(e)
            db.commit()
        raise e
    finally:
        db.close()
