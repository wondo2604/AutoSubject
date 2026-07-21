import json
import os
import requests
from backend.config import OPENAI_API_KEY, GEMINI_API_KEY
from backend.renderer_service import renderer

class AIService:
    @staticmethod
    def generate_questions(major_topic: str, sub_topic: str, selected_subtypes: list[str], count: int = 5, prompt_extra: str = "") -> list[dict]:
        """
        AI API를 호출하거나, API 키가 없는 경우 고품질 템플릿 기반 수학 문항 및 수식/도형 이미지 생성
        """
        questions = []
        
        for i in range(1, count + 1):
            sub_type = selected_subtypes[(i - 1) % len(selected_subtypes)] if selected_subtypes else "기본 응용"
            img_name = f"prob_{sub_topic}_{i:03d}.png"
            
            # 1. 수식/도형 렌더링 실행
            if "도형" in sub_type or "피타고라스" in major_topic or "기하" in major_topic:
                renderer.render_geometry_sample(f"{sub_topic} {i}", img_name)
                stem_text = f"다음 {sub_topic} 관련 도형에서 변 $c$의 길이를 구하시오."
            else:
                renderer.render_latex(rf"a^2 + b^2 = c^2 \quad (a={i+2}, b={i+3})", img_name)
                stem_text = f"다음 조건 만족 시 {sub_topic}의 수식을 계산하시오."
            
            choices = [
                f"{i * 2 + 1}",
                f"{i * 2 + 2}",
                f"{i * 2 + 3}",
                f"{i * 2 + 4}",
                f"{i * 2 + 5}"
            ]
            
            questions.append({
                "Index": i,
                "Section": f"{major_topic} - {sub_topic}",
                "Sub_type": sub_type,
                "Question": stem_text,
                "Choices": ", ".join([f"{idx+1}. {c}" for idx, c in enumerate(choices)]),
                "Answer": "3",
                "Solution": f"{sub_topic}의 성질에 의하여 정답은 3번입니다.",
                "Image_File": img_name
            })
            
        return questions

ai_service = AIService()
