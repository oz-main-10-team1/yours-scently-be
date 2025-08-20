import json
import os
import re
import uuid
from typing import Dict

import requests

CLOVA_MODEL = "HCX-003"
CLOVA_API_URL = "https://clovastudio.stream.ntruss.com/v1/chat-completions/" + CLOVA_MODEL
CLOVA_API_KEY = os.environ.get("CLOVA_API_KEY")
if not CLOVA_API_KEY:
    raise ValueError("CLOVA_API_KEY environment variable not set")


def call_clova_model(user_input: str) -> Dict:
    # 요청 ID (매 요청마다 고유해야 함)
    request_id = str(uuid.uuid4())

    # 프롬프트 정의
    system_prompt = (
        "다음 사용자 문장을 분석하여 향수 추천을 위한 JSON을 만들어줘.\n\n"
        "출력 형식:\n"
        "{\n"
        '  "description": "사용자의 감성 및 분위기를 인용하여 향수를 직접 추천하는 문장",\n'
        '  "keywords": ["musk", "vanilla", "powdery"],\n'
        '  "reason": "추천 배경 요약 (예: 감정 상태, 계절, 향 노트 등). 전체 문장이 아닌 구절 형태로 끝내기 (예: 계절감 고려, 따뜻한 분위기 반영)"\n'
        "}\n\n"
        "설명:\n"
        '- "description"은 반드시 사용자 문장 속 감성 키워드를 인용하여 추천 문장을 작성하세요.\n'
        "  예: \"당신이 선택한 '달콤하고 포근한' 분위기를 바탕으로 머스크와 바닐라 노트가 어우러진 이 향을 추천드려요.\"\n"
        '- "reason"은 전체 문장이 아닌, **간단한 명사형 구절**로 작성하세요.\n'
        '  예: "계절감 고려", "감성 키워드 기반", "따뜻한 분위기 반영"\n'
        '- 반드시 JSON 형식으로 출력하고, 문자열은 모두 큰따옴표(")를 사용하세요.\n\n'
        f'사용자 문장: "{user_input}"\n'
        "출력:"
    )

    messages = [{"role": "system", "content": system_prompt}]

    headers = {
        "Authorization": CLOVA_API_KEY,
        "X-NCP-CLOVASTUDIO-REQUEST-ID": request_id,
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
    }

    body = {
        "messages": messages,
        "topP": 0.8,
        "topK": 0,
        "maxTokens": 512,
        "temperature": 0.5,
        "repeatPenalty": 1.1,
        "stopBefore": ["\n\n"],
        "includeAiFilters": True,
    }

    resp = requests.post(CLOVA_API_URL, headers=headers, json=body)
    resp.raise_for_status()

    clova_text = resp.json()["result"]["message"]["content"].strip()

    # json 혹은 래핑 제거
    if clova_text.startswith("```"):
        clova_text = re.sub(r"^```(?:json)?\s*", "", clova_text)
        clova_text = re.sub(r"\s*```$", "", clova_text)

    try:
        return json.loads(clova_text)
    except json.JSONDecodeError:
        raise ValueError(f"Clova 응답 JSON 파싱 실패: {clova_text}")
