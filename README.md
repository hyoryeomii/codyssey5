# 1. 프로젝트 개요 및 목적

## 1.1 프로젝트 개요

- 본 프로젝트는 사용자가 입력한 여행 날짜(YYYY-MM-DD)를 기반으로 LLM API(OpenAI)와 지도/장소 API(Kakao Local)를 연쇄적으로 조합(API Chaining)하여 자동 추천 여행 리포트를 생성하는 CLI 기반 파이썬 프로그램
- LLM이 특정 시기에 적합한 국내 여행지와 날씨·축제 정보를 구조화된 JSON 데이터로 생성하면, 지도 API가 해당 도시의 실시간 맛집 정보를 검색하여 최종 마크다운 리포트와 원본 JSON 데이터로 저장

## 1.2 개발 목적

1. 복수 API 연동 파이프라인 구축: 단일 API 호출을 넘어, LLM의 Output(JSON)을 지도 API의 Input으로 넘겨주는 연계 흐름 실습
2. 구조화된 데이터 추출: 비정형 데이터(자연어)를 출력하는 LLM에 프롬프트를 적용하여 규격화된 JSON Schema 형태의 데이터를 안정적으로 추출
3. 실무형 예외 처리 및 예외 복구력 확보: API 키 미설정, 네트워크 타임아웃, Kakao API 인증 오류(401/403), JSON 파싱 실패 등 다양한 장애 상황에서도 프로그램이 중단되지 않고 대안 데이터로 작업을 끝까지 완성하는 에러 핸들링을 구현
4. 보안 및 환경변수 관리 체계화: API 키 하드코딩 방지 및 .env, .gitignore 활용을 통해 보안 사고를 예방하는 개발 스타일을 익힘

# 2. 프로젝트 파일 구조 및 설명

## 2.1 파일 구조

```
travel_project/
├── travel_planner.py      # CLI 실행, API 연동 및 전체 로직 제어 파이썬 메인 코드
├── README.md              # 프로젝트 안내 및 과제 수행 학습 보고서(+ 주의사항)
├── requirements.txt       # 의존성 라이브러리 목록
├── .gitignore             # API 키(.env) 및 가상환경(venv) Git 추적 제외 설정 파일
└── results/               # 실행 결과 데이터 저장 폴더
    ├── 2026-08-07_data.json       # 원본 데이터 (1차 추천 + 맛집 검색 + 오류 기록)
    └── 2026-08-07_travel_plan.md  # 최종 마크다운 여행 리포트
```

## 2.2 각 파일 및 역할

- travel_planner.py: CLI 명령어를 수신(argparse)하고 OpenAI API와 Kakao Local API를 차례로 호출한 뒤, 파싱된 데이터와 오류를 모아 결과 파일로 저장하는 메인 프로그램
- README.md: 제출용 종합 보고서로 프로젝트 개요, 실행 가이드, 핵심 기술 개념 답변 및 회고를 작성한 파일(+ API 키 보안 및 유출 주의사항)
- requirements.txt: 프로젝트 실행에 필요한 외부 라이브러리 명세 파일입니다. 평가자가 동일 환경을 쉽게 구축할 수 있도록 지원
- .gitignore: API 키가 포함된 .env 파일과 대용량 가상환경 venv/ 폴더가 실수로 Git/제출물에 포함되는 것을 방지
- results/: 프로그램 실행 결과물이 날짜별(YYYY-MM-DD)로 차곡차곡 저장되는 출력 디렉토리

# 3. 주요 기능

### **3.1 CLI 날짜 입력 및 검증: argparse를 활용하여 YYYY-MM-DD 형식 검증 후 처리, 입력값 날짜 형식이 올바르지 않으면 사용법 출력하고 종료**

<img width="844" height="754" alt="image" src="https://github.com/user-attachments/assets/c55d0c57-6289-41ea-b4f2-77ec5aff3da2" />


▲ 입력값 검증 함수 코드(+사용법)

<img width="862" height="75" alt="image" src="https://github.com/user-attachments/assets/79b7ae79-c2f9-469c-846c-af9387cf078b" />

▲ 입력값 날짜 형식이 올바르지 않을 경우

### **3.2 1차 AI 여행 추천: OpenAI API를 통해 추천 도시, 날씨, 축제 정보, 추천 근거를 JSON 구조화 데이터로 추출**

<img width="1070" height="934" alt="image" src="https://github.com/user-attachments/assets/b705e277-b50e-4d7c-92f5-6ddaabdd82d4" />


▲ OpenAI 1차 추천 (Structured Output & 재시도 1회)

### **3.3 2차 장소 API 연동: 추천된 도시를 기반으로 Kakao Local API를 호출하여 맛집 5곳 데이터 실시간 검색**

<img width="1076" height="961" alt="image" src="https://github.com/user-attachments/assets/0314d96b-bd38-4b79-b76b-206c8322e297" />


▲ Kakao Local API 맛집 검색 (예외 발생 시 Fallback)

### **3.4 결과 리포트 자동 생성: 원본 데이터(results/YYYY-MM-DD_data.json) 및 최종 마크다운 리포트(results/YYYY-MM-DD_travel_plan.md) 저장**

<img width="937" height="916" alt="image" src="https://github.com/user-attachments/assets/e213c0ef-03bd-45fc-82cb-1b3b4a46e905" />


▲ OpenAI 최종 Markdown 리포트 생성

### **3.5 에러 처리: 외부 API 인증 실패, 네트워크 오류, JSON 파싱 오류 발생 시에도 프로그램 중단 없이 errors 로그 기록 후 "데이터 없음"으로 진행**

<img width="854" height="250" alt="image" src="https://github.com/user-attachments/assets/54f63d93-dcda-4f43-a519-54ac52a6fb83" />


▲ API 키 미설정: 즉시 종료 + 설정 방법 안내 출력

<img width="1012" height="343" alt="image" src="https://github.com/user-attachments/assets/32e761fb-60d1-451a-a9fe-02c4899cde60" />


▲ 지도/장소 API 실패: 맛집 섹션 '데이터 없음' 처리 & 계속 진행

<img width="1027" height="753" alt="image" src="https://github.com/user-attachments/assets/8edf7f4a-19a4-4878-ac45-11b3ceb59dce" />


▲ LLM JSON 파싱 실패: 재시도 1회 수행

<img width="658" height="34" alt="image" src="https://github.com/user-attachments/assets/351ac360-cad7-4417-b163-2f8f8e68dfc1" />


▲ errors 섹션 요약 관리: 리포트에 오류 목록 기록 (빈 리스트 포함)

- 마크다운에 ## 오류 요약(errors) 섹션 작성

# 4. 개발 및 실행 환경

- Language: Python 3.14.6 (최신 버전)

<img width="627" height="45" alt="image" src="https://github.com/user-attachments/assets/6e0e48bd-d48a-48b8-99e5-c5b09b303a07" />


- LLM API: OpenAI API (gpt-4o-mini)
    - 선택 이유:
        - 높은 가성비 및 빠른 응답 속도: 기존 모델 대비 비용이 저렴하면서도 추천 문맥을 정확하게 이해함
        - 안정적인 구조화 출력 지원: Pydantic 스키마와 연동되어 LLM의 출력을 JSON 형태로 깨짐 없이 추출하는 데 가장 최적화되어 있음
- Map API: Kakao Local REST API
    - 선택 이유:
        - 풍부하고 정확한 국내 장소 데이터: 국내 맛집, 상세 주소, 카테고리, 지도 URL, 좌표 정보 검색 시 가장 높은 정확도를 제공함
        - REST API의 용이성: 별도의 거대한 SDK 설치 없이 requests 라이브러리만으로 손쉽게 호출 및 파싱 가능
- 설치한 외부 파이썬 라이브러리
    - openai
        - OpenAI의 LLM 모델을 파이썬에서 손쉽게 호출하기 위한 공식 SDK 라이브러리
        - 1차 여행지 추천 및 최종 마크다운 리포트 생성에 사용
    - requests
        - 외부 서버와 HTTP 통신(데이터 요청 및 응답 수신)
        - Kakao Local API나 OpenAI API에 요청을 보내고 JSON 결과를 받아오기 위해
    - python-dotenv
        - 프로젝트 폴더 내 .env 파일에 적어둔 API 키 정보를 읽어와 파이썬 환경변수로 불러옴
        - 코드 안에 API 키를 직접 적지 않고 보안을 지키며 키를 불러오기 위해 사용
    - pydantic
        - 데이터 입력값의 타입 검증 및 구조화를 담당하는 라이브러리
        - LLM 응답 데이터가 지정한 JSON 형식을 잘 지켰는지 검증할 때 사용

# 5. 설치 및 실행 방법

### 5.1 가상환경 구축 및 패키지 설치

```
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

- 가상환경(venv)을 사용하는 이유
    1. 프로젝트 간 패키지 충돌 방지: PC에 설치된 다른 파이썬 프로젝트들과 라이브러리 버전이 서로 꼬이거나 충돌하는 현상을 막아줌
    2. 시스템 파이썬 환경 보호: OS 기본 파이썬 환경을 더럽히지 않고 해당 프로젝트만을 위한 독립된 공간을 제공함
    3. 개발 환경의 재현성 확보: requirements.txt에 명시된 동일한 패키지 버전을 설치하여 평가자/협업자의 PC에서도 동일하게 실행되도록 보장함

### 5.2 환경변수(.env) 설정

프로젝트 루트 디렉토리에 .env 파일을 생성하고 발급받은 API 키 설정

<예시>

```
OPENAI_API_KEY="your_openai_api_key_here"
KAKAO_REST_KEY="your_kakao_rest_key_here"
```

- 카카오 API 이용 사전 설정 필수사항
    
<img width="1050" height="718" alt="image" src="https://github.com/user-attachments/assets/25510604-863b-44f1-9a2a-16aa5f2f00ee" />

    

▲ [앱 설정] ➔ [플랫폼] ➔ [Web]: http://localhost 등록

<img width="1333" height="536" alt="image" src="https://github.com/user-attachments/assets/d75d4689-f54d-4a6b-aa2a-7f94a224fe3d" />


▲ [카카오맵 API 사용 설정]: 상태 ON 전환

# 6. 실행 화면 및 결과

프로그램 실행 프롬프트: python travel_planner.py -date "2026-08-07” 

실행이 완료되면 results/ 폴더에 날짜별 파일이 저장됨

- results/2026-08-07_data.json: 1차 추천 결과, 맛집 검색 데이터, 오류 기록이 포함된 원본 JSON
- results/2026-08-07_travel_plan.md: 최종 완성된 마크다운 여행 리포트

## 6.1. CLI 정상 실행 로그 캡처

<img width="867" height="197" alt="image" src="https://github.com/user-attachments/assets/5c5bdb64-a08f-4cff-ab08-a0192fddaac3" />


▲ CLI 터미널에서 프로그램이 정상 실행되어 카카오 API 맛집 검색까지 에러 없이 완료된 화면

## 6.2 생성된 원본 데이터 JSON (results/2026-08-07_data.json)

<img width="1215" height="935" alt="image" src="https://github.com/user-attachments/assets/275a950b-9779-4c10-938f-513da8456a18" />


▲ 1차 추천 정보, Kakao 맛집 검색 결과(좌표, URL 포함), 에러 상태(errors: [])가 포함된 구조화 데이터

## 6.3 최종 여행 리포트 Markdown (results/2026-08-07_travel_plan.md)

<img width="1144" height="880" alt="image" src="https://github.com/user-attachments/assets/4eab05b0-860d-40c4-976a-ef2d1f3adaed" />


▲ 사용자 전달용 마크다운 형식 리포트로 일일 일정과 맛집 방문 링크 등 구성된 파일

# 7. 핵심 기술 개념 및 과제 회고

## 7.1 REST API 요청/응답 구조 및 HTTP 메서드(GET / POST)

- REST API 구조: 클라이언트와 서버가 HTTP 프로토콜을 통해 자원을 주고받는 아키텍처이며 요청은 URL, HTTP Method, Header(인증 키 등), Body/Query Parameter로 구성되며, 응답은 HTTP Status Code(200, 401, 403 등)와 JSON Data를 반환함
- GET 메서드: 서버의 데이터를 조회/요청할 때 사용하고 데이터가 URL 파라미터에 노출되며, 캐싱이 가능합니다. (예: Kakao Local 맛집 검색 API)
- POST 메서드: 서버에 데이터를 제출/생성하거나 복잡한 페이로드(본문 데이터)를 전달할 때 사용하며 데이터가 HTTP Request Body에 실려 전달되므로 URL에 노출되지 않으며 길이 제한이 없음 (예: OpenAI Chat Completion API)

## 7.2 LLM 출력을 구조화(JSON)하여 다음 API의 입력으로 연결하는 흐름

- Chaining 프로세스: LLM의 자연어 응답을 system_prompt로 제어하여 정확한 JSON Schema 형태만 출력하도록 강제함
- 연결 흐름:
    1. LLM Output: {"recommended_city": "부산", ...} 형태로 1차 데이터 생성
    2. Python Parsing: json.loads()를 통해 파이썬 Dictionary 객체로 변환
    3. Data Extraction: city = data["recommended_city"] 로 키값 추출
    4. Map API Input: 추출한 부산 파라미터를 Kakao API 요청 키워드로 대입하여 연쇄 파이프라인 형성

## 7.3 외부 API 호출 대표 오류 및 대응 원칙

- 인증 오류 (401 / 403): API 키 오타, 헤더명 불일치, 카카오 콘솔 내 도메인 미등록(http://localhost) 또는 카카오맵 서비스 미활성화(disabled OPEN_MAP_AND_LOCAL) 시 발생함
    - 대응 원칙: 오류 발생 시 프로그램 전체를 중단시키지 않고 errors 목록에 로그를 남긴 후 맛집 섹션을 '데이터 없음'으로 유연하게 처리하여 3단계 최종 리포트 생성 완성
- 쿼터 초과 (429): API 호출 제한 사용량을 초과한 경우
    - 대응 원칙: 지연 후 재시도를 수행하거나, 지체 없이 백업 데이터/기본값을 채워 전체 프로세스를 보장함
- 네트워크 오류 (Timeout / Connection Error): 외부 서버 응답 불능 시 발생함
    - 대응 원칙: try-except requests.exceptions.RequestException으로 예외를 포획함
- JSON 파싱 오류: LLM이 JSON 외에 설명글을 덧붙이거나 마크다운 블록(```json)을 포함하여 파싱에 실패하는 경우
    - 대응 원칙: 정규표현식으로 JSON 문맥만 추출하거나, 프롬프트를 보완하여 최대 1회 재시도를 수행함

## 7.4 API 키를 .env / 환경변수로 관리하는 이유 및 필요성

- 협업 및 공개 저장소(Git) 실수로 인한 키 유출 방지:
GitHub 같은 오픈소스 저장소에 코드를 push할 때 .gitignore에 .env를 등록해 두면, 소스코드가 공개되어도 API 키는 안전하게 로컬 환경에만 남게 됨
- 운영 및 배포 환경의 유연성 (코드 수정 최소화):
개발, 테스트, 운영 서버 환경에 따라 사용하는 API 키가 다를 때 코드를 일일이 수정할 필요 없이 환경변수값만 바꿔서 적용할 수 있음. 키가 만료되어 교체할 때도 소스코드 재배포 없이 .env 파일만 수정하면 됨
- 무단 도용 및 과금/쿼터 관련 사고 예방:
OpenAI, Kakao 등 대다수의 API 서비스는 사용량에 따라 실제 비용이 청구되는데 키가 외부에 노출될 경우 제3자에 의해 무단 도용되어 막대한 경제적 피해가 발생하거나 Daily Quota가 소진되어 서비스가 마비되는 위험을 차단할 수 있음

# 8. 보너스 과제 - 2. 결과 캐싱

동일한 -date로 재실행 시, 이미 저장된 results/{date}_data.json 원본 데이터가 존재하면 외부 API 추가 호출 없이 저장된 데이터를 재활용하여 속도 최적화 및 API 비용을 절감하도록 설계됨

<img width="740" height="328" alt="image" src="https://github.com/user-attachments/assets/d96f67e6-64fe-4c90-9de4-41bed614ebb9" />


▲ 코드 추가

<img width="863" height="155" alt="image" src="https://github.com/user-attachments/assets/e82e936d-4374-4689-9ab7-cb57dfb241d5" />


▲ 동일 날짜 2회 실행 시 API 호출을 건너뛰는 캐싱 적용 CLI 화면 (1회는 이미 본 과제에서 실행)

성과: 동일한 날짜로 프로그램을 재실행할 경우, 이미 생성된 로컬 데이터(results/{date}_data.json)를 재활용하도록 구현하여 불필요한 외부 API 호출을 차단함. 이를 통해 API 과금 비용을 절감하고 프로그램 응답 속도를 극대화하는 캐싱 최적화의 기본 원리를 적용함

# 9. 결론 및 과제 소감

- 본 프로젝트를 진행하며 단순히 단일 API를 호출하는 수준을 넘어, LLM의 비정형 출력을 Pydantic 스키마 기반의 JSON 데이터로 구조화하고 이를 다시 외부 지도 API의 입력값으로 전달하는 API Chaining 파이프라인을 성공적으로 구축함
- 특히 실무 환경에서 빈번히 발생하는 네트워크 타임아웃, 외부 API 인증 실패(401/403), JSON 파싱 오류 등의 장애 상황에서도 프로그램 전체가 중단되지 않고, errors 로그 기록 및 Fallback(대안 데이터) 처리를 통해 최종 리포트 생성을 완료하는 유연한 기능 저하 방식의 에러 핸들링 설계 가치를 이해할 수 있었음
- .env 환경변수와 .gitignore를 활용한 API 키 보안 관리 및 가상환경 기반의 패키지 분리 설정을 통해, 오픈소스 협업 및 배포 환경에서 지켜야 할 기본적이고 핵심적인 보안 개발 습관을 체득함
