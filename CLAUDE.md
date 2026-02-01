# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

카카오맵 부동산 정보 크롤러. 카카오맵 API/웹에서 부동산 매물 데이터를 수집하고 가공하는 Python 프로젝트.

## 개발 환경

- **Python**: 3.13+
- **패키지 매니저**: uv (pip/poetry 대신 uv 사용)

## 주요 명령어

```bash
# 의존성 설치
uv sync

# 의존성 추가
uv add <package-name>

# 개발 의존성 추가
uv add --dev <package-name>

# 스크립트 실행
uv run python main.py

# 단일 테스트 실행
uv run pytest tests/test_xxx.py::test_function_name

# 전체 테스트
uv run pytest

# 린트
uv run ruff check .

# 포맷팅
uv run ruff format .
```

## 아키텍처

(프로젝트 구조가 확정되면 업데이트 필요)

## 크롤링 관련 참고사항

- 카카오맵 요청 시 적절한 rate limiting 적용 필요
- User-Agent 등 헤더 설정 확인
- 응답 데이터는 JSON 형태로 저장
