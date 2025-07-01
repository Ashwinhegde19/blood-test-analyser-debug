from crewai import Crew, Process
from agents import doctor, verifier, nutritionist, exercise_specialist
from task import help_patients, verification, nutrition_analysis, exercise_planning

def run_crew(query: str, file_path: str="data/sample.pdf"):
    """To run the whole crew"""
    medical_crew = Crew(
        agents=[verifier, doctor, nutritionist, exercise_specialist],
        tasks=[verification, help_patients, nutrition_analysis, exercise_planning],
        process=Process.sequential,
    )
    
    result = medical_crew.kickoff({'query': query, 'path': file_path})
    return result
