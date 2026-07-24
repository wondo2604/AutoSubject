import json
import os
import random
import re
import urllib.request
import urllib.parse
from typing import List, Dict, Tuple, Optional

try:
    from backend.config import OPENAI_API_KEY, GEMINI_API_KEY
    from backend.renderer_service import renderer
except ImportError:
    from config import OPENAI_API_KEY, GEMINI_API_KEY
    from renderer_service import renderer

class DynamicPromptBuilder:
    """
    학교급, 학년, 학기, 단원 정보를 기반으로
    AI가 정형화된 문제를 피하고 다채로운 10가지 출제 스타일로 문제집 세트를 생성하도록
    프롬프트를 구축하는 엔진
    """
    STYLING_TEMPLATES = [
        {
            "type": "실생활 활용 응용형",
            "instruction": "건축물, 지도, 자율주행, 스마트폰 통신, 스포츠 경기, 금융 이자 등 풍부한 실생활 상황 맥락을 도식화하여 실용적 문제를 만드시오."
        },
        {
            "type": "개념 명제 판별형",
            "instruction": "<보기> 항목 (ㄱ, ㄴ, ㄷ, ㄹ) 중 '옳은 것만을 있는 대로 고른 것'을 묻는 5지 선다형 개념 판별 문제를 만드시오."
        },
        {
            "type": "시각 이미지 연계 계산형",
            "instruction": "제시된 기하 도형/그래프/수직선의 변의 길이, 각도, 좌표, 부피 등 시각적 정보를 분석하여 계산하는 문제를 만드시오."
        },
        {
            "type": "빈칸 증명 추론형",
            "instruction": "수학적 정리의 증명 과정이나 다단계 연산 풀이 과정 중 빈칸 (가), (나)에 들어갈 알맞은 수식이나 값을 추론하는 문제를 만드시오."
        },
        {
            "type": "두 개념 융합 고난도 심화형",
            "instruction": "서로 다른 두 가지 이상의 수학적 개념이나 조건(예: 피타고라스와 비례식, 함수와 도형의 넓이 등)을 융합한 고난도 문제를 만드시오."
        },
        {
            "type": "오류 탐색 및 교정형",
            "instruction": "학생이 문제를 푸는 과정에서 범한 오류가 발생하는 단계를 찾거나 올바른 답으로 수정하는 풀이 교정형 문제를 만드시오."
        },
        {
            "type": "조건부 경우가 나누어지는 경우 탐구형",
            "instruction": "변수나 미지수의 조건 범위에 따라 해의 개수나 결과가 다르게 나누어지는 탐구형 문제를 만드시오."
        },
        {
            "type": "그래프 방정식/함수 영역 분석형",
            "instruction": "좌표평면 상의 함수 그래프 교점, 절편, 기울기, 둘러싸인 도형의 넓이를 구하는 분석 문제를 만드시오."
        },
        {
            "type": "3D 공간 입체 도형 단면 해석형",
            "instruction": "정육면체, 직육면체, 원뿔 등 입체도형의 대각선, 단면적, 겉넓이, 부피를 구하는 공간 감각 문제를 만드시오."
        },
        {
            "type": "다단계 문장제 구체 해결형",
            "instruction": "복잡한 서술형 지문 조건을 단계별 수식으로 전환하여 최후의 미지수 값을 구하는 융합 문장제 문제를 만드시오."
        }
    ]

    @classmethod
    def build_system_prompt(cls, school_level: str, grade: str, semester: str) -> str:
        return f"""당신은 대한민국 교육과정 평가원 수석 수학 출제위원입니다.
대상: [{school_level} {grade} {semester}]

[출제 원칙]
1. 문항마다 지문 내용, 숫자, 변수, 실생활 소재가 중복되지 않도록 독창적으로 만드시오.
2. 모든 수식은 LaTeX 포맷($a^2+b^2=c^2$)을 엄격히 사용하시오.
3. 보기(1~5번)는 명확히 서로 구분되는 수식 또는 값으로 구성하시오.
4. 모든 문항은 정답(1~5)과 꼼꼼한 step-by-step 상세 해설을 포함하시오.
5. 도형이나 그래프가 필요한 문항인 경우 'diagram_spec' 객체에 시각 메타데이터를 함께 제공하시오.

[응답 포맷]
반드시 다음 구조의 JSON 배열 형식으로만 응답해야 하며, Markdown 코드 블록 없이 순수 JSON만 반환하시오:
[
  {{
    "question": "지문 내용 (LaTeX 수식 사용)",
    "choices": ["1. 보기1", "2. 보기2", "3. 보기3", "4. 보기4", "5. 보기5"],
    "answer": 3,
    "solution": "상세한 풀이 과정...",
    "diagram_spec": {{
      "type": "right_triangle | circle_sector | cube_3d | coordinate_graph | number_line",
      "label_a": "3", "label_b": "4", "label_c": "x",
      "angle": 60, "radius_label": "r",
      "slope": 2.0, "intercept": -1.0,
      "points": [[-2, "A"], [3, "B"]]
    }}
  }}
]
"""

class AIService:
    @staticmethod
    def generate_questions_for_topics(
        school_level: str,
        grade: str,
        semester: str,
        topic_list: List[dict],
        count_per_topic: int = 3,
        custom_prompt: str = "",
        model_name: str = "GPT-4o",
        temperature: float = 0.7,
        log_callback=None
    ) -> List[dict]:
        """
        AI API (OpenAI / Gemini) 연동 및 실시간 동적 무작위 생성 엔진을 통해
        다양한 문제와 도형 이미지를 일괄 생성
        """
        all_questions = []
        global_index = 1

        for topic_info in topic_list:
            major_topic = topic_info.get("major_topic", "수학")
            sub_topic = topic_info.get("sub_topic", "기본 단원")
            subtypes = topic_info.get("subtypes", [])

            # API 호출 시도
            ai_questions = AIService._try_generate_via_ai(
                school_level, grade, semester, major_topic, sub_topic, subtypes,
                count_per_topic, custom_prompt, model_name, temperature, log_callback
            )

            # API 호출 실패 또는 키가 없는 경우 -> 풍부한 동적 프로시저럴 생성 엔진 실행
            if not ai_questions or len(ai_questions) < count_per_topic:
                if log_callback and (not ai_questions):
                    log_callback(f"⚠️ [{sub_topic}] AI API 키 미입력 또는 연동 대기 -> 동적 무작위 수학 엔진으로 생성합니다.")
                
                needed = count_per_topic - len(ai_questions)
                procedural_qs = AIService._generate_procedural_set(
                    school_level, grade, semester, major_topic, sub_topic, subtypes,
                    needed, global_index + len(ai_questions)
                )
                ai_questions.extend(procedural_qs)

            # 각 질문에 대해 이미지 렌더링 및 항목 정리
            for q_data in ai_questions:
                img_name = f"prob_{school_level}_{grade}_{global_index:03d}.png"
                spec = q_data.get("diagram_spec", {})
                
                # 시각 이미지 동적 렌더링
                renderer.render_auto_by_topic(major_topic, sub_topic, global_index, img_name, spec=spec)

                choices_val = q_data.get("choices", [])
                if isinstance(choices_val, list):
                    choices_str = ", ".join(choices_val)
                else:
                    choices_str = str(choices_val)

                sub_type_label = q_data.get("sub_type", f"{sub_topic} 핵심 응용")

                all_questions.append({
                    "Index": global_index,
                    "School_Level": school_level,
                    "Grade": grade,
                    "Semester": semester,
                    "Section": f"[{major_topic}] {sub_topic}",
                    "Sub_type": sub_type_label,
                    "Question": q_data.get("question", ""),
                    "Choices": choices_str,
                    "Answer": str(q_data.get("answer", 1)),
                    "Solution": q_data.get("solution", ""),
                    "Image_File": img_name
                })
                global_index += 1

        return all_questions

    @staticmethod
    def _try_generate_via_ai(
        school: str, grade: str, sem: str, major: str, sub: str, subtypes: list,
        count: int, custom_prompt: str, model_name: str, temp: float, log_cb
    ) -> List[dict]:
        """OpenAI 또는 Gemini API 호출"""
        from backend.config import OPENAI_API_KEY, GEMINI_API_KEY

        sys_prompt = DynamicPromptBuilder.build_system_prompt(school, grade, sem)
        user_prompt = f"단원: [{major}] - {sub}\n세부 유형 참고: {', '.join(subtypes) if subtypes else '기본 및 응용'}\n생성할 문항 수: {count}개\n추가 요구사항: {custom_prompt}"

        # 1. OpenAI 모델 처리
        if any(m in model_name.lower() for m in ["gpt", "o3"]):
            if not OPENAI_API_KEY:
                return []
            if log_cb:
                log_cb(f"🤖 OpenAI API ({model_name}) 호출 중... 단원: {sub}")
            return AIService._call_openai(sys_prompt, user_prompt, model_name, temp, OPENAI_API_KEY)

        # 2. Gemini 모델 처리
        elif "gemini" in model_name.lower():
            if not GEMINI_API_KEY:
                return []
            if log_cb:
                log_cb(f"🤖 Google Gemini API ({model_name}) 호출 중... 단원: {sub}")
            return AIService._call_gemini(sys_prompt, user_prompt, model_name, temp, GEMINI_API_KEY)

        # 기타 (기본 OpenAI 시도)
        if OPENAI_API_KEY:
            return AIService._call_openai(sys_prompt, user_prompt, "gpt-4o-mini", temp, OPENAI_API_KEY)
        return []

    @staticmethod
    def _call_openai(sys_prompt: str, user_prompt: str, model: str, temp: float, api_key: str) -> List[dict]:
        try:
            target_model = "gpt-4o" if "gpt-4o" in model.lower() else "gpt-4o-mini"
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "AutoSubjectr/1.0"
            }
            payload = {
                "model": target_model,
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temp,
                "response_format": {"type": "json_object"}
            }
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=30) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                content = res_json["choices"][0]["message"]["content"]
                return AIService._parse_json_questions(content)
        except Exception as e:
            print(f"OpenAI API Error: {e}")
        return []

    @staticmethod
    def _call_gemini(sys_prompt: str, user_prompt: str, model: str, temp: float, api_key: str) -> List[dict]:
        try:
            model_id = "gemini-2.0-flash" if "2.0" in model else "gemini-1.5-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            prompt_full = f"{sys_prompt}\n\n[요청]\n{user_prompt}"
            payload = {
                "contents": [{"parts": [{"text": prompt_full}]}],
                "generationConfig": {"temperature": temp, "responseMimeType": "application/json"}
            }
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=30) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                text = res_json["candidates"][0]["content"]["parts"][0]["text"]
                return AIService._parse_json_questions(text)
        except Exception as e:
            print(f"Gemini API Error: {e}")
        return []

    @staticmethod
    def _parse_json_questions(raw_text: str) -> List[dict]:
        """LLM 반환 텍스트에서 JSON 배열 추출 및 파싱"""
        try:
            cleaned = re.sub(r"```json\s*", "", raw_text)
            cleaned = re.sub(r"```\s*$", "", cleaned).strip()
            
            data = json.loads(cleaned)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                if "questions" in data and isinstance(data["questions"], list):
                    return data["questions"]
                elif "items" in data and isinstance(data["items"], list):
                    return data["items"]
                else:
                    return [data]
        except Exception as e:
            print(f"JSON Parse Error: {e}")
        return []

    @staticmethod
    def _generate_procedural_set(
        school: str, grade: str, sem: str, major: str, sub: str, subtypes: list,
        count: int, start_idx: int
    ) -> List[dict]:
        """
        API 키가 없는 경우에도 절대 똑같은 문제가 나오지 않는
        무작위 프로시저럴 수학 문제 생성 엔진
        """
        questions = []
        contexts = [
            ("스마트 시티 건설 현장에서 건물", "거리"),
            ("자율주행 드론이 이동하는 경로에서 점", "위치 좌표"),
            ("해양 탐사선에서 음파를 쏘아 올린 해저 지점", "깊이"),
            ("신재생 에너지 태양광 패널의 각도와", "면적"),
            ("컴퓨터 그래픽스 3D 렌더링 화면의 객체", "대각선 길이"),
            ("스포츠 경기장의 중앙 전광판 위치와", "높이"),
            ("스마트폰 앱 통신 요금 요율 계산 시", "변동 비율")
        ]

        for idx in range(count):
            curr_q_num = start_idx + idx
            rnd = random.Random(curr_q_num * 997 + len(sub) * 31)
            
            style_info = DynamicPromptBuilder.STYLING_TEMPLATES[idx % len(DynamicPromptBuilder.STYLING_TEMPLATES)]
            style_name = style_info["type"]
            st_type = subtypes[idx % len(subtypes)] if subtypes else "핵심 개념"

            val_a = rnd.choice([3, 5, 6, 8, 9, 12, 15])
            val_b = rnd.choice([4, 12, 8, 15, 12, 16, 20])
            val_c_sq = val_a**2 + val_b**2
            val_c = int(val_c_sq**0.5) if int(val_c_sq**0.5)**2 == val_c_sq else f"\\sqrt{{{val_c_sq}}}"

            ctx_obj, ctx_prop = rnd.choice(contexts)

            if "피타고라스" in sub or "기하" in major or "도형" in sub:
                stem = f"[{school} {grade}] {ctx_obj} $A$와 $B$의 {ctx_prop}를 구하려고 한다. 직각삼각형 $ABC$에서 밑변의 길이가 ${val_a} \\text{{cm}}$, 높이가 ${val_b} \\text{{cm}}$일 때, 빗변 $x$의 길이는 얼마인가?"
                ans_idx = 3
                correct_val = val_c
                c_list = [
                    f"1. {val_a + 1} cm",
                    f"2. {val_b - 1} cm",
                    f"3. {correct_val} cm",
                    f"4. {val_a + val_b} cm",
                    f"5. {val_c_sq} cm"
                ]
                sol = f"피타고라스 정리에 의해 $x^2 = {val_a}^2 + {val_b}^2 = {val_a**2} + {val_b**2} = {val_c_sq}$ 이므로 $x = {val_c} \\text{{cm}}$입니다."
                spec = {"type": "right_triangle", "label_a": str(val_a), "label_b": str(val_b), "label_c": "x"}

            elif "함수" in sub or "방정식" in sub or "좌표" in sub:
                slope = rnd.choice([-2, -1, 2, 3])
                intercept = rnd.choice([-3, -1, 1, 4])
                test_x = rnd.choice([1, 2, 3])
                test_y = slope * test_x + intercept

                stem = f"[{school} {grade}] 좌표평면 위에 나타난 1차함수 $y = {slope}x + ({intercept})$ 의 그래프가 점 $({test_x}, k)$를 지날 때, 상수 $k$의 값을 구하시오."
                ans_idx = 2
                c_list = [
                    f"1. {test_y - 2}",
                    f"2. {test_y}",
                    f"3. {test_y + 1}",
                    f"4. {test_y + 3}",
                    f"5. {test_y * 2}"
                ]
                sol = f"함수 식에 $x = {test_x}$를 대입하면 $k = {slope} \\times {test_x} + ({intercept}) = {test_y}$ 가 됩니다. 정답은 2번입니다."
                spec = {"type": "coordinate_graph", "slope": slope, "intercept": intercept}

            elif "원" in sub or "부채꼴" in sub:
                r_val = rnd.choice([3, 4, 6, 8, 10])
                angle_val = rnd.choice([30, 45, 60, 90, 120])
                area_factor = (angle_val / 360) * (r_val**2)
                area_str = f"{int(area_factor)}\\pi" if area_factor.is_integer() else f"\\frac{{{int(area_factor*3)}}}{{3}}\\pi"

                stem = f"[{school} {grade}] 반지름의 길이가 ${r_val} \\text{{cm}}$이고 중심각의 크기가 ${angle_val}^\circ$인 부채꼴의 넓이를 구하시오."
                ans_idx = 1
                c_list = [
                    f"1. ${area_str} \\text{{ cm}}^2$",
                    f"2. ${r_val * 2}\\pi \\text{{ cm}}^2$",
                    f"3. ${r_val**2}\\pi \\text{{ cm}}^2$",
                    f"4. ${angle_val}\\pi \\text{{ cm}}^2$",
                    f"5. ${r_val + angle_val}\\pi \\text{{ cm}}^2$"
                ]
                sol = f"부채꼴의 넓이 공식 $S = \\pi r^2 \\times \\frac{{\\theta}}{{360^\circ}}$에 의하여 $S = \\pi \\times {r_val}^2 \\times \\frac{{{angle_val}}}{{360}} = {area_str} \\text{{cm}}^2$ 이므로 정답은 1번입니다."
                spec = {"type": "circle_sector", "radius_label": f"{r_val}", "angle": angle_val}

            else:  # 수와 연산, 확률, 기타
                val_p1 = rnd.randint(-4, -1)
                val_p2 = rnd.randint(1, 5)
                dist = val_p2 - val_p1

                stem = f"[{school} {grade}] 수직선 위의 두 점 $A({val_p1})$, $B({val_p2})$ 사이의 거리 $\\overline{{AB}}$를 구하시오."
                ans_idx = 4
                c_list = [
                    f"1. {dist - 3}",
                    f"2. {dist - 1}",
                    f"3. {dist + 1}",
                    f"4. {dist}",
                    f"5. {dist + 2}"
                ]
                sol = f"두 점 사이의 거리는 큰 값에서 작은 값을 뺀 차이이므로 $\\overline{{AB}} = {val_p2} - ({val_p1}) = {dist}$ 이므로 정답은 4번입니다."
                spec = {"type": "number_line", "points": [(val_p1, "A"), (val_p2, "B")]}

            questions.append({
                "sub_type": f"{st_type} ({style_name})",
                "question": stem,
                "choices": c_list,
                "answer": ans_idx,
                "solution": sol,
                "diagram_spec": spec
            })

        return questions

ai_service = AIService()
