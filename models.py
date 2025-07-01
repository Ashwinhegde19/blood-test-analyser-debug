from sqlalchemy import Column, String, Text
from database import Base

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, index=True)
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
