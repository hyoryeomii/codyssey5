# 🛫 AI 기반 국내 여행지 추천 CLI 프로그램

OpenAI API와 Kakao Local 장소 검색 API를 연동하여 특정 날짜에 어울리는 국내 여행지와 맛집 정보를 추천하고, Markdown 리포트를 자동 생성해주는 CLI 프로그램입니다.

- **GitHub Repository**: [https://github.com/hyoryeomii/codyssey5/tree/main](https://github.com/hyoryeomii/codyssey5/tree/main)

---

## 1. 주요 기능
- **CLI 입력 지원 및 검증**: `-date YYYY-MM-DD` 형식으로 지정된 날짜 입력 받음 및 형식 검증 (`argparse`)
- **LLM 구조화 출력**: OpenAI API (Structured Output)를 활용해 JSON 형식으로 도시, 날씨, 축제, 추천 이유 추출
- **장소 검색 및 맛집 추출**: Kakao Local 키워드 검색 API로 해당 도시 맛집 5곳 정보(이름, 주소, 카테고리, 좌표, URL) 조회
- **예외 및 파이프라인 관리**: API 키 미설정 시 즉시 종료, 지도 API 실패/검색 결과 0건 발생 시 리포트 연속 생성, LLM 파싱 실패 시 1회 재시도
- **결과 자동 파일화 및 캐싱**: `results/` 폴더에 원본 데이터 JSON 및 최종 Markdown 리포트 저장. 동일 날짜 재실행 시 파일 기반 캐싱 적용

---

## 2. 개발 환경
- **Python**: 3.10 이상
- **주요 라이브러리**: `openai`, `requests`, `python-dotenv`, `pydantic`

---

## 3. 프로그램 실행 가이드 및 CLI 사용법

### 올바른 실행 예시
```bash
python travel_planner.py -date "2026-08-07"
```

### 잘못된 입력 시 출력 스니펫 (예: 날짜 형식 오류)
```text
$ python travel_planner.py -date "20260807"

[ERROR] 올바르지 않은 날짜 형식입니다: '20260807'
사용법 예시: python travel_planner.py -date '2026-08-07'
```

---

## 4. API 키 발급 및 설정 방법

### 1. OpenAI API 키 발급
1. [OpenAI API](https://platform.openai.com/) 접속 후 로그인
2. `API Keys` 메뉴에서 새 API 키 생성 및 복사

### 2. Kakao Local API 키 발급
1. [Kakao Developers](https://developers.kakao.com/) 접속 후 로그인
2. `내 애플리케이션` > `애플리케이션 추가하기`
3. 생성된 앱의 `앱 키` 중 **`REST API 키`** 복사

### 3. `.env` 파일 설정
프로젝트 최상위 디렉토리에 `.env` 파일을 생성하고 발급받은 키를 설정합니다.

```env
OPENAI_API_KEY="sk-..."
KAKAO_REST_KEY="f8..."
```

---

## 5. 보안 및 API 키 관리 정책

- **API 키 하드코딩 금지**: `OPENAI_API_KEY` 및 `KAKAO_REST_KEY`는 소스코드에 절대 포함하지 않고 외부 `.env` 파일로 분리 관리합니다.
- **Git 추적 제외 증빙**: `.gitignore` 파일에 `.env` 및 `venv/` 경로를 등록하여 버전 관리 시스템에 실제 API 키가 유출되지 않도록 처리하였습니다.
  ```gitignore
  # .gitignore 설정 내용
  .env
  venv/
  results/
  ```
- **제출물 비노출 확인**: GitHub 저장소 및 제출물 내 코드/결과 샘플에 실제 API 키 값이 포함되어 있지 않음을 증명 및 확인하였습니다.

---

## 6. 함수 및 모듈 단위 분리 명세

프로그램은 단일 책임 원칙(SRP)에 따라 각 기능이 함수 단위로 독립 분리되어 있습니다.

| 함수명 | 입력 (Input) | 출력 (Output) | 주요 역할 및 책임 |
|---|---|---|---|
| `validate_date(date_str)` | `date_str: str` | `bool` | 입력된 날짜의 'YYYY-MM-DD' 포맷 유효성 검증 |
| `get_llm_recommendation(travel_date, retry)` | `travel_date: str`, `retry: bool` | `dict \| None` | OpenAI Structured Output 기반 1차 여행지 추천 및 파싱 실패 시 1회 재시도 |
| `search_places_kakao(city)` | `city: str` | `list[dict]` | Kakao Local API(HTTP GET)를 통한 맛집 5곳 검색 및 에러/EMPTY 예외 처리 |
| `generate_markdown_report(travel_date, rec_data, places_data)` | `travel_date: str`, `rec_data: dict`, `places_data: list` | `str` | 수집된 데이터와 오류 이력을 바탕으로 최종 Markdown 리포트 생성 (HTTP POST) |
| `main()` | CLI 입력 (`-date`) | 결과 파일 저장 및 로그 출력 | 전체 실행 흐름 제어, 파일 캐싱 여부 검사, 결과 파일 저장 |

---

## 7. Pydantic을 활용한 LLM 응답 검증 상세

OpenAI API 응답의 타입 안정성을 보장하기 위해 `pydantic.BaseModel`을 사용해 검증 스키마를 정의하였습니다.

```python
class TravelRecommendation(BaseModel):
    recommended_city: str  # 필수: 추천 도시명 (문자열)
    weather: str           # 필수: 해당 시기 날씨 요약 (문자열)
    events: list[str]      # 필수: 축제 및 행사 후보 목록 (문자열 리스트)
    reason: str            # 필수: 추천 이유 (문자열)
```

- **필수 키 검증**: LLM 응답이 위 4개 필드를 모두 정확히 포함하지 않거나 데이터 타입이 다를 경우 Pydantic `ValidationError`가 발생합니다.
- **실패 시 처리**: 검증 실패 시 `retry=True` 플래그와 함께 `get_llm_recommendation()`을 1회 재호출하여 규격을 재요청하며, 최종 실패 시 `errors_log`에 기록하고 종료합니다.

### 1차 추천 생성 결과 (JSON 스니펫 예시)
```json
{
  "recommended_city": "강릉",
  "weather": "맑고 선선한 바람이 부는 전형적인 가을 날씨입니다.",
  "events": ["강릉 바우길 걷기 행사", "경포호 야경 투어"],
  "reason": "8월 초순의 강릉은 바다와 산을 동시에 즐기기에 최적의 장소입니다."
}
```

---

## 8. 지도 API 교체 추상화 및 키워드 정규화 전략

### 지도 API 교체 추상화 설계 (Pluggable Architecture)
현재 구현체는 Kakao Local API를 사용하지만, 네이버 지도 API 또는 Google Places API로 쉽게 교체할 수 있도록 추상화 구조를 고려해 설계되었습니다.
- **결과 데이터 표준화**: API 변경 시에도 메인 로직이 영향을 받지 않도록 장소 데이터 구조를 아래와 같이 표준화하여 리턴합니다.
  ```json
  {
    "name": "장소명",
    "address": "도로명주소",
    "category": "카테고리",
    "url": "상세URL",
    "x": 128.899,
    "y": 37.751
  }
  ```

### 추천 도시 키워드 정규화 (Normalization) 전략
- **키값 정규화 추출**: `rec_data.get("recommended_city", "제주")` 방식으로 안전하게 도시 키워드를 추출합니다.
- **검색 키워드 보정**: LLM이 반환한 도시명 뒤에 `맛집` 키워드를 결합(`{city} 맛집`)하여 검색 성공률을 정규화합니다.
- **검색 실패(0건/오류) 시 Fallback**: 검색 결과가 없거나 API 오류(401/403 등)가 발생하면 `places`를 빈 리스트 `[]`로 처리하고, 리포트에 `- 데이터 없음 (장소 검색 결과 0건)`으로 명시하여 전체 파이프라인이 중단되지 않고 연속 동작합니다.

---

## 9. HTTP 메서드 및 네트워크 처리
- **GET 메서드 (Kakao Local API)**: 단순 데이터 조회 요청이며, 조회 조건이 URL 파라미터(`query`)로 전달되므로 GET을 사용합니다.
- **POST 메서드 (OpenAI Completions API)**: LLM 프롬프트 데이터 전송 및 구조화 응답 생성을 위한 요청이므로 POST를 사용합니다.

---

## 10. 결과 파일 저장 및 캐싱 (보너스 기능)

### 저장 구조 (`results/` 폴더)
- `results/{YYYY-MM-DD}_data.json`: 1차 추천 + 맛집 데이터 + 오류 이력 원본 JSON
- `results/{YYYY-MM-DD}_travel_plan.md`: 최종 렌더링된 마크다운 보고서

### 결과 JSON 구조 및 오류 이력 (Sample)
```json
{
  "recommendation": {
    "recommended_city": "강릉",
    "weather": "맑음",
    "events": ["축제1"],
    "reason": "추천이유"
  },
  "places": [
    {
      "name": "식당명",
      "address": "주소",
      "category": "음식점",
      "url": "http://...",
      "x": 128.89,
      "y": 37.75
    }
  ],
  "errors": [
    {
      "timestamp": "2026-08-07 01:15:00",
      "step": "place_search",
      "type": "EMPTY_RESULT",
      "message": "0 results for query=속초 맛집"
    }
  ]
}
```

### 캐싱 최적화 적용
동일한 `-date`로 재실행 시 이미 생성된 `results/{date}_data.json` 및 `.md` 파일이 존재하면 외부 API 추가 호출을 즉시 건너뛰고 기존 파일을 재활용합니다. 이를 통해 외부 API 과금 비용을 절감하고 응답 속도를 최적화하였습니다.
*(※ 현재는 파일 존재 여부 기반으로 캐싱되며, 향후 `--force` 옵션을 통한 강제 갱신 정책 확장이 가능하도록 설계되었습니다.)*