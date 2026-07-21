import requests
from bs4 import BeautifulSoup
import urllib.parse

class ResearchCrawler:
    @staticmethod
    def search_subtypes(major_topic: str, sub_topic: str) -> list[str]:
        """
        입력된 단원 키워드로 세부 유형 10~15개 자동 리서치 추출
        """
        query = f"{major_topic} {sub_topic} 수학 문제 세부 유형 대표 문제"
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        
        extracted_subtypes = []
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                snippets = soup.find_all("a", class_="result__snippet")
                for snip in snippets:
                    text = snip.get_text()
                    if "유형" in text or "활용" in text or "구하기" in text or "성질" in text:
                        clean_text = text.strip()[:40]
                        if clean_text not in extracted_subtypes:
                            extracted_subtypes.append(clean_text)
        except Exception as e:
            print(f"Crawling error: {e}")

        # 기본 fallback 리스트
        if len(extracted_subtypes) < 5:
            extracted_subtypes = [
                f"{sub_topic}의 기본 개념과 정의",
                f"{sub_topic}의 실생활 응용 문제",
                f"{sub_topic} 관련 도형 및 연계 문제",
                f"{sub_topic} 난이도 상 (변별력 문항)",
                f"{sub_topic} 빈출 서술형 유형"
            ]

        return extracted_subtypes[:10]

research_crawler = ResearchCrawler()
