import argparse
import json
import os
from datetime import datetime
import sys
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
import requests

# ----------------------------------------------------
# 1. 환경변수 로드 및 API 키 검증
# ----------------------------------------------------
load_dotenv(override=True)
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
KAKAO_KEY = os.getenv("KAKAO_REST_KEY")

# API 키 뒤 4자리 출력 테스트
# key_check = os.getenv("OPENAI_API_KEY", "")
# print(f"👉 [현재 읽어온 OpenAI 키 뒤 4자리]: ...{key_check[-4:]}")

# key_check = os.getenv("KAKAO_REST_KEY", "")
# print(f"👉 [현재 읽어온 카카오 키 뒤 4자리]: ...{key_check[-4:]}")

if not OPENAI_KEY or not KAKAO_KEY:
    print("[ERROR] API 키가 설정되지 않았습니다.")
    print("프로젝트 루트의 .env 파일에 OPENAI_API_KEY와 KAKAO_REST_KEY를 설정해야 합니다.")
    print("예시:")
    print('  OPENAI_API_KEY="sk..어쭈구"')
    print('  KAKAO_REST_KEY="f8..어쭈구"')
    exit(1)

openai_client = OpenAI(api_key=OPENAI_KEY)
errors_log = []


# ----------------------------------------------------
# 2. 1차 추천용 Pydantic 스키마 정의
# ----------------------------------------------------
class TravelRecommendation(BaseModel):
    recommended_city: str
    weather: str
    events: list[str]
    reason: str


# ----------------------------------------------------
# 3. 입력값(날짜) 검증 함수
# ----------------------------------------------------
def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False
def main():
    parser = argparse.ArgumentParser(
        description="AI 기반 국내 여행 추천 CLI 프로그램"
    )
    parser.add_argument(
        "-date",
        "--date",
        type=str,
        required=True,
        help="여행 날짜 (YYYY-MM-DD)",
    )

    args = parser.parse_args()

    if not validate_date(args.date):
        print(
            "\n[오류] 날짜 형식이 올바르지 않습니다. 'YYYY-MM-DD' 형태로 입력해 주세요.\n"
        )
        parser.print_help()  # 사용법 출력
        sys.exit(1)  # 종료

    target_date = args.date
    print(f"[{target_date}] 날짜 입력 확인 완료. 여행 추천을 시작합니다...")


# ----------------------------------------------------
# 4. Step 1: OpenAI 1차 추천 (Structured Output & 재시도 1회)
# ----------------------------------------------------
def get_llm_recommendation(
    travel_date: str, retry: bool = False
) -> dict | None:
    prompt = f"""
    당신은 대한민국 여행 전문가입니다.
    사용자가 입력한 여행 날짜({travel_date})에 방문하기 가장 좋은 국내 도시 1 곳을 추천해주세요.
    지정한 시기에 어울리는 날씨 요약, 축제/행사 후보(1~3개), 추천 근거(2~4문장)를 작성하세요.
    """
    if retry:
        prompt += "\n[주의] 이전 응답 파싱에 실패했습니다. 반드시 주어진 JSON 스키마 규격에 맞춰 출력하세요."

    try:
        # OpenAI Structured Outputs 기능 사용
        completion = openai_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "사용자의 요청에 맞춰 정확한 JSON 형식을 출력하는 여행 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            response_format=TravelRecommendation,
            temperature=0.7,
        )
        parsed_data = completion.choices[0].message.parsed
        return parsed_data.model_dump()

    except Exception as e:
        print(f"  [DEBUG 에러 내용]: {e}")
        if not retry:
            print("  [WARN] OpenAI JSON 생성/파싱 실패. 1회 재시도합니다...")
            return get_llm_recommendation(travel_date, retry=True)
        else:
            errors_log.append(
                {
                    "step": "llm_recommendation",
                    "type": "PARSE_ERROR",
                    "message": str(e),
                }
            )
            return None


# ----------------------------------------------------
# 5. Step 2: Kakao Local API 맛집 검색 (예외 발생 시 Fallback)
# ----------------------------------------------------
def search_places_kakao(city: str) -> list[dict]:
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_KEY}"}
    params = {"query": f"{city} 맛집", "size": 5}

    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)

        # 인증 오류(401, 403) 처리
        if res.status_code in (401, 403):
            print(f"  [DEBUG 카카오 에러 상세]: {res.text}")
            errors_log.append(
                {
                    "step": "place_search",
                    "type": "AUTH_ERROR",
                    "message": f"HTTP {res.status_code}",
                }
            )
            print(
                f"  [WARN] 카카오 API 인증 실패({res.status_code}). 맛집 섹션을 '데이터 없음'으로 처리하고 진행합니다."
            )
            return []

        res.raise_for_status()
        data = res.json()
        documents = data.get("documents", [])

        # 검색 결과 0건 처리
        if not documents:
            errors_log.append(
                {
                    "step": "place_search",
                    "type": "EMPTY_RESULT",
                    "message": f"0 results for query={city} 맛집",
                }
            )
            return []

        places = []
        for doc in documents:
            places.append(
                {
                    "name": doc.get("place_name"),
                    "address": doc.get("road_address_name")
                    or doc.get("address_name"),
                    "category": doc.get("category_name"),
                    "url": doc.get("place_url"),
                    "x": float(doc.get("x")) if doc.get("x") else None,
                    "y": float(doc.get("y")) if doc.get("y") else None,
                }
            )
        return places

    except Exception as e:
        errors_log.append(
            {"step": "place_search", "type": "NETWORK_ERROR", "message": str(e)}
        )
        print("  [WARN] 카카오 장소 검색 네트워크/기타 오류 발생. 진행을 계속합니다.")
        return []


# ----------------------------------------------------
# 6. Step 3: OpenAI 최종 Markdown 리포트 생성
# ----------------------------------------------------
def generate_markdown_report(
    travel_date: str, rec_data: dict, places_data: list[dict]
) -> str:
    prompt = f"""
    아래 수집된 여행 정보를 바탕으로 가독성 높은 Markdown 문서 리포트를 작성하세요.

    [1차 추천 정보]
    {json.dumps(rec_data, ensure_ascii=False, indent=2)}

    [맛집 데이터]
    {json.dumps(places_data, ensure_ascii=False, indent=2) if places_data else "데이터 없음"}

    [오류 이력]
    {json.dumps(errors_log, ensure_ascii=False, indent=2)}

    작성 규칙:
    1. 최상단에 `# {travel_date} 국내 여행 추천 리포트` 제목을 작성하세요.
    2. 아래 H2(`##`) 목차 구조를 반드시 유지하세요:
       - ## 추천 지역
       - ## 추천 이유
       - ## 날씨 요약
       - ## 행사/축제
       - ## 맛집 추천 (데이터가 없으면 '- 데이터 없음 (장소 검색 결과 0건)' 명시)
       - ## 1일 일정 제안 (오전, 오후, 저녁 코스 제안)
       - ## 오류 요약(errors) (발생한 오류가 있으면 정리하고, 없으면 '없음' 표시)
    """

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "마크다운 보고서 생성을 전담하는 어시스턴트입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        errors_log.append(
            {
                "step": "report_generation",
                "type": "LLM_ERROR",
                "message": str(e),
            }
        )
        return f"# {travel_date} 국내 여행 추천 리포트\n\n오류로 인해 리포트를 생성하지 못했습니다."


# ----------------------------------------------------
# 7. 메인 제어 흐름 (CLI 및 결과 저장)
# ----------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="OpenAI & Kakao API 기반 국내 여행지 추천 CLI"
    )
    parser.add_argument(
        "-date",
        "--date",
        required=True,
        help="여행 날짜 (YYYY-MM-DD 형식, 예: -date '2026-08-07')",
        type=str,
    )
    args = parser.parse_args()

    # 입력 검증
    if not validate_date(args.date):
        print(
            f"[ERROR] 올바르지 않은 날짜 형식입니다: '{args.date}'"
        )
        print("사용법 예시: python travel_planner.py -date '2026-08-07'")
        exit(1)

    print(f"[{args.date} 여행 추천 프로그램 실행]")

    # ----------------------------------------------------
    # [보너스 과제] 캐싱 체크: 기존 JSON 파일이 존재하면 API 호출 건너뛰기
    # ----------------------------------------------------
    json_path = f"results/{args.date}_data.json"
    md_path = f"results/{args.date}_travel_plan.md"

    if os.path.exists(json_path) and os.path.exists(md_path):
        print(f"\n⚡ [캐싱 적용] 이미 저장된 데이터가 존재합니다: {json_path}")
        print(" - 외부 API 호출을 건너뛰고 기존 결과 파일을 그대로 사용합니다.\n")
        print(f"완료! {md_path} 및 {json_path} 를 확인하세요.")
        return  # main() 함수 종료 (API 호출을 하지 않음)
    # ----------------------------------------------------

    # 1. LLM 1차 추천
    print("[1/3] 1차 추천 생성 중(OpenAI API)...")
    rec_data = get_llm_recommendation(args.date)

    if not rec_data:
        print("[ERROR] 1차 추천 생성 실패로 프로그램을 종료합니다.")
        exit(1)

    city = rec_data.get("recommended_city", "제주")
    print(f'  - recommended_city: "{city}"')

    # 2. 지도/장소 API 맛집 검색
    print("[2/3] 맛집 검색 중(Kakao Local API)...")
    places = search_places_kakao(city)
    print(f"  - 맛집 {len(places)}곳 검색 완료")

    # 3. 최종 리포트 생성
    print("[3/3] 최종 리포트 생성 중(OpenAI API)...")
    report_md = generate_markdown_report(args.date, rec_data, places)

    # 4. 결과 파일 저장
    os.makedirs("results", exist_ok=True)

    raw_json_data = {
        "recommendation": rec_data,
        "places": places,
        "errors": errors_log,
    }

    json_path = f"results/{args.date}_data.json"
    md_path = f"results/{args.date}_travel_plan.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(raw_json_data, f, ensure_ascii=False, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"\n완료! {md_path} 및 {json_path} 를 확인하세요.")


if __name__ == "__main__":
    main()