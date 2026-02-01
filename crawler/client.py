import time
import httpx

from crawler.config import ApiConfig


class KakaoLocalClient:
    def __init__(self, config: ApiConfig | None = None):
        self.config = config or ApiConfig()
        self._client: httpx.Client | None = None

    def __enter__(self) -> "KakaoLocalClient":
        self._client = httpx.Client(
            headers={"Authorization": f"KakaoAK {self.config.api_key}"},
            timeout=10.0,
        )
        return self

    def __exit__(self, *args) -> None:
        if self._client:
            self._client.close()
            self._client = None

    def search_category(
        self,
        category_group_code: str,
        x: str,
        y: str,
        radius: int,
        page: int = 1,
    ) -> dict:
        if not self._client:
            raise RuntimeError(
                "클라이언트가 초기화되지 않았습니다. with 문을 사용하세요."
            )

        params = {
            "category_group_code": category_group_code,
            "x": x,
            "y": y,
            "radius": radius,
            "page": page,
            "size": self.config.page_size,
            "sort": "distance",
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self._client.get(self.config.base_url, params=params)

                if response.status_code == 429:
                    wait = 2 ** (attempt + 1)
                    print(f"  요청 제한 (429). {wait}초 후 재시도...")
                    time.sleep(wait)
                    continue

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise RuntimeError(
                        "API 인증 실패 (401). KAKAO_REST_API_KEY를 확인하세요."
                    ) from e
                if e.response.status_code == 403:
                    raise RuntimeError(
                        "API 접근 거부 (403). 카카오 개발자센터에서 REST API 키와 플랫폼 설정을 확인하세요."
                    ) from e
                raise
            except httpx.HTTPError as e:
                if attempt < max_retries - 1:
                    wait = 2**attempt
                    print(
                        f"  네트워크 오류: {e}. {wait}초 후 재시도 ({attempt + 1}/{max_retries})..."
                    )
                    time.sleep(wait)
                else:
                    raise

        raise RuntimeError("최대 재시도 횟수를 초과했습니다.")

    def search_all_pages(
        self,
        category_group_code: str,
        x: str,
        y: str,
        radius: int,
    ) -> tuple[list[dict], int]:
        all_documents: list[dict] = []
        total_count = 0

        for page in range(1, self.config.max_page + 1):
            result = self.search_category(
                category_group_code=category_group_code,
                x=x,
                y=y,
                radius=radius,
                page=page,
            )

            documents = result.get("documents", [])
            all_documents.extend(documents)

            meta = result.get("meta", {})
            is_end = meta.get("is_end", True)
            total_count = meta.get("total_count", 0)

            if page == 1:
                print(f"  총 {total_count}건 발견 (반경 {radius}m)")

            if is_end:
                break

            time.sleep(self.config.request_delay)

        return all_documents, total_count
