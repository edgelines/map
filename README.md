# kakaomap-crawler

카카오맵 API를 이용한 부동산 공인중개사무소 크롤러.
지정 좌표 주변의 부동산 중개사무소를 검색하고 CSV/Excel로 저장합니다.

## 요구사항

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) 패키지 매니저
- 카카오 REST API 키 ([developers.kakao.com](https://developers.kakao.com))

## 설치

```bash
uv sync
```

## 설정

프로젝트 루트에 `.env` 파일을 생성하고 API 키를 입력합니다.

```
KAKAO_REST_API_KEY=your_api_key_here
```

## 사용법

```bash
# 기본 실행 (반경 5km, CSV + Excel 출력)
uv run python main.py

# 반경 지정
uv run python main.py --radius 3000

# 출력 형식 선택
uv run python main.py --format csv
uv run python main.py --format excel

# 격자 크기 지정 (결과가 많을 때 정밀도 향상)
uv run python main.py --grid-size 5

# 출력 디렉토리 변경
uv run python main.py --output-dir results/
```

## 프로젝트 구조

```
main.py              # CLI 진입점
crawler/
  config.py          # API, 검색, 출력 설정
  client.py          # 카카오 로컬 API 클라이언트
  search.py          # 검색 로직 (단건/격자 검색)
  models.py          # 데이터 모델
  export.py          # CSV/Excel 내보내기
output/              # 기본 출력 디렉토리
```

## 격자 검색

카카오 API는 한 쿼리당 최대 45건까지만 페이지네이션을 지원합니다.
검색 결과가 이 제한을 초과하면 자동으로 영역을 NxN 격자로 분할하여 재검색합니다.
