# API 활용 국내 여행지 추천 프로그램

Open ai API와 Kakao Local 장소 검색 API를 연동하여 특정 날짜에 어울리는 국내 여행지와 맛집 정보를 추천하고, Markdown 리포트를 자동 생성해주는 CLI 프로그램

## 주요 기능
- **CLI 입력 지원**: `-date YYYY-MM-DD` 형식으로 지정된 날짜 입력 및 검증
- **LLM 구조화 출력**: open ai API를 활용해 JSON 형식으로 도시, 날씨, 축제, 추천 이유 추출
- **장소 검색 및 맛집 추출**: Kakao Local 키워드 검색 API로 해당 도시 맛집 5곳 정보(이름, 주소, 카테고리, 좌표, URL) 조회
- **예외 및 안정성 처리**: API 키 미설정 시 즉시 종료, 지도 API 실패/검색 결과 0건 발생 시 리포트 연속 생성, LLM 파싱 재시도 및 오류 파이프라인 관리
- **결과 자동 파일화**: `results/` 폴더에 원본 데이터 JSON 및 최종 Markdown 리포트 저장

## 개발 환경
- **Python**: 3.10 이상
- **주요 라이브러리**: `Open ai`, `requests`, `python-dotenv`, `pydantic`

## API 키 발급 및 설정 방법

### 1. open ai API 키 발급
1. [Open ai API](https://platform.openai.com/) 접속 후 로그인
2. `Get API key` 메뉴에서 새 키 생성 및 복사

### 2. Kakao Local API 키 발급
1. [Kakao Developers](https://developers.kakao.com/) 접속 후 로그인
2. `내 애플리케이션` > `애플리케이션 추가하기` (앱 이름/회사명은 자유 작성)
3. 생성된 앱의 `앱 키` 중 **`REST API 키`** 복사

### 3. `.env` 파일 설정
프로젝트 최상위 디렉토리에 `.env` 파일을 생성하고 발급받은 키 작성


### ⚠️ API 키 보안 및 유출 주의사항 (필독)

1. **`.env` 파일 Git 추적 제외 (`.gitignore` 설정)**:
   API 키가 포함된 `.env` 파일이 GitHub 등의 공개 저장소에 올려지지 않도록 `.gitignore` 파일에 반드시 `.env`를 추가해야 합니다.
2. **소스코드 내 키 하드코딩 금지**:
   파이썬 코드(`travel_planner.py`) 내에 API 키를 직접 문자열로 작성하면 소스코드 공유 시 키가 그대로 유출되므로, 항상 `python-dotenv`를 통해 환경변수로 불러와야 합니다.
3. **유출 시 위험성**:
   API 키가 외부에 노출될 경우 타인에 의해 무단 사용되어 **예상치 못한 과금(OpenAI)**이 발생하거나, **일일 사용량 쿼터 초과(Kakao)**로 서비스가 마비될 수 있습니다. 유출이 의심될 경우 즉시 해당 플랫폼 콘솔에서 키를 재발급/삭제해야 합니다.

```env
OPENAI_API_KEY="your_openai_api_key"
KAKAO_REST_KEY="your_kakao_rest_api_key"