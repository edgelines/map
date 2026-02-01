import argparse
import sys
from pathlib import Path

from crawler.config import SearchConfig, ApiConfig, ExportConfig
from crawler.client import KakaoLocalClient
from crawler.search import search_all
from crawler.export import save_csv, save_excel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="유성온천역 인근 부동산 공인중개사무소 크롤러"
    )
    parser.add_argument(
        "--radius",
        type=int,
        default=5000,
        help="검색 반경 (미터, 기본값: 5000)",
    )
    parser.add_argument(
        "--format",
        choices=["csv", "excel", "both"],
        default="both",
        help="출력 형식 (기본값: both)",
    )
    parser.add_argument(
        "--grid-size",
        type=int,
        default=3,
        help="격자 크기 (기본값: 3x3, 675건 초과 시 자동 적용)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="출력 디렉토리 (기본값: output/)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    api_config = ApiConfig()
    if not api_config.api_key or api_config.api_key == "your_api_key_here":
        print("오류: KAKAO_REST_API_KEY가 설정되지 않았습니다.")
        print()
        print("1. https://developers.kakao.com 에서 앱을 생성하세요.")
        print("2. REST API 키를 복사하세요.")
        print("3. .env 파일에 다음과 같이 입력하세요:")
        print("   KAKAO_REST_API_KEY=your_actual_api_key")
        sys.exit(1)

    search_config = SearchConfig(radius=args.radius)
    export_config = ExportConfig(output_dir=args.output_dir)

    print("=" * 50)
    print("유성온천역 인근 부동산 공인중개사무소 검색")
    print("=" * 50)

    try:
        with KakaoLocalClient(api_config) as client:
            offices = search_all(
                client, search_config, grid_size=args.grid_size
            )
    except RuntimeError as e:
        print(f"\n오류: {e}")
        sys.exit(1)

    if not offices:
        print("검색 결과가 없습니다.")
        sys.exit(0)

    phone_count = sum(1 for o in offices if o.phone)

    print()
    print("검색 결과 요약:")
    print(f"  총 {len(offices)}건")
    print(f"  전화번호 보유: {phone_count}건")
    print(f"  전화번호 없음: {len(offices) - phone_count}건")
    print()

    if args.format in ("csv", "both"):
        save_csv(offices, export_config)
    if args.format in ("excel", "both"):
        save_excel(offices, export_config)

    print()
    print("완료!")


if __name__ == "__main__":
    main()
