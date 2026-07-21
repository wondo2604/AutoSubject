import json
import os
import requests

try:
    from backend.config import OPENAI_API_KEY, GEMINI_API_KEY
    from backend.renderer_service import renderer
except ImportError:
    from config import OPENAI_API_KEY, GEMINI_API_KEY
    from renderer_service import renderer

class AIService:
    @staticmethod
    def generate_questions_for_topics(
        school_level: str,
        grade: str,
        semester: str,
        topic_list: list[dict],
        count_per_topic: int = 3,
        custom_prompt: str = ""
    ) -> list[dict]:
        """
        학교급, 학년, 학기 및 단원 리스트(대단원-중단원)에 맞춰 연속 문제집 문항 구성
        """
        all_questions = []
        global_index = 1

        for t_idx, topic_info in enumerate(topic_list, 1):
            major_topic = topic_info.get("major_topic", "기본 단원")
            sub_topic = topic_info.get("sub_topic", "기본 유형")
            selected_subtypes = topic_info.get("subtypes", [])

            for i in range(1, count_per_topic + 1):
                sub_type = selected_subtypes[(i - 1) % len(selected_subtypes)] if selected_subtypes else "기본 응용"
                img_name = f"prob_{school_level}_{grade}_{sub_topic}_{global_index:03d}.png"
                
                # 수식/도형 렌더링
                if "도형" in sub_type or "피타고라스" in major_topic or "기하" in major_topic or "삼각형" in sub_topic:
                    renderer.render_geometry_sample(f"{sub_topic} {i}", img_name)
                    stem_text = f"[{school_level} {grade} {semester}] 다음 {major_topic} - {sub_topic}의 도형에서 변 $c$의 길이를 구하시오."
                else:
                    renderer.render_latex(rf"a^2 + b^2 = c^2 \quad (a={i+1}, b={i+2})", img_name)
                    stem_text = f"[{school_level} {grade} {semester}] 다음 {major_topic} - {sub_topic} 수식의 해를 구하시오."
                
                choices = [
                    f"{i * 2 + 1}",
                    f"{i * 2 + 2}",
                    f"{i * 2 + 3}",
                    f"{i * 2 + 4}",
                    f"{i * 2 + 5}"
                ]
                
                all_questions.append({
                    "Index": global_index,
                    "School_Level": school_level,
                    "Grade": grade,
                    "Semester": semester,
                    "Section": f"[{major_topic}] {sub_topic}",
                    "Sub_type": sub_type,
                    "Question": stem_text,
                    "Choices": ", ".join([f"{idx+1}. {c}" for idx, c in enumerate(choices)]),
                    "Answer": "3",
                    "Solution": f"{school_level} {grade} {semester} 과정의 {sub_topic} 성질에 의하여 정답은 3번입니다.",
                    "Image_File": img_name
                })
                global_index += 1
                
        return all_questions

ai_service = AIService()
