import pandas as pd
from pathlib import Path
from backend.config import DATA_DIR

class ExportService:
    @staticmethod
    def export_questions(questions: list, filename_prefix: str) -> dict:
        """
        questions: list of dict [{Index, Section, Sub_type, Question, Choices, Answer, Solution, Image_File}]
        """
        df = pd.DataFrame(questions)
        
        csv_path = DATA_DIR / f"{filename_prefix}.csv"
        xlsx_path = DATA_DIR / f"{filename_prefix}.xlsx"
        
        # Raw Data 형태 (서식 배제, UTF-8-sig)
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        df.to_excel(xlsx_path, index=False)
        
        return {
            "csv_path": str(csv_path),
            "xlsx_path": str(xlsx_path)
        }

export_service = ExportService()
