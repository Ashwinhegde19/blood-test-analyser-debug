## Importing libraries and files
import os
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

from crewai_tools import tool

## Creating custom pdf reader tool
class BloodTestReportTool():
    @tool
    def read_data_tool(path: str = 'data/sample.pdf') -> str:
        """Tool to read data from a pdf file from a path

        Args:
            path (str, optional): Path of the pdf file. Defaults to 'data/sample.pdf'.

        Returns:
            str: Full Blood Test report file
        """
        
        reader = PdfReader(path)
        full_report = ""
        for page in reader.pages:
            full_report += page.extract_text() + "\n"
            
        return full_report



