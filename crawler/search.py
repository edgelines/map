import math

from crawler.config import SearchConfig
from crawler.client import KakaoLocalClient
from crawler.models import RealEstateOffice


def _deduplicate(offices: list[RealEstateOffice]) -> list[RealEstateOffice]:
    seen: set[tuple[str, str]] = set()
    result: list[RealEstateOffice] = []
    for office in offices:
        key = office.dedup_key()
        if key not in seen:
            seen.add(key)
            result.append(office)
    return result


def search_nearby(
    client: KakaoLocalClient,
    config: SearchConfig,
) -> list[RealEstateOffice]:
    print(f"[검색] 중심 ({config.x}, {config.y}), 반경 {config.radius}m")

    documents, _ = client.search_all_pages(
        category_group_code=config.category_group_code,
        x=config.x,
        y=config.y,
        radius=config.radius,
    )

    offices = [RealEstateOffice.from_api_response(doc) for doc in documents]
    offices = _deduplicate(offices)

    print(f"  중복 제거 후 {len(offices)}건")
    return offices


MAX_PER_QUERY = 45  # 카카오 API pageable_count 제한


def search_all(
    client: KakaoLocalClient,
    config: SearchConfig,
    grid_size: int = 3,
) -> list[RealEstateOffice]:
    print(f"[검색] 중심 ({config.x}, {config.y}), 반경 {config.radius}m")

    documents, total_count = client.search_all_pages(
        category_group_code=config.category_group_code,
        x=config.x,
        y=config.y,
        radius=config.radius,
    )

    if total_count > len(documents):
        print(
            f"  API 페이지 제한: {total_count}건 중 {len(documents)}건만 조회 가능 → 격자 검색 전환"
        )
        return search_with_grid(client, config, grid_size=grid_size)

    offices = [RealEstateOffice.from_api_response(doc) for doc in documents]
    offices = _deduplicate(offices)

    print(f"  중복 제거 후 {len(offices)}건")
    return offices


def search_with_grid(
    client: KakaoLocalClient,
    config: SearchConfig,
    grid_size: int = 3,
) -> list[RealEstateOffice]:
    print(f"[격자 검색] {grid_size}x{grid_size} 격자, 반경 {config.radius}m")

    center_x = float(config.x)
    center_y = float(config.y)

    # 1도 ≈ 111km (위도 기준), 경도는 위도에 따라 보정
    lat_per_meter = 1.0 / 111_000
    lon_per_meter = 1.0 / (111_000 * math.cos(math.radians(center_y)))

    cell_radius = config.radius // grid_size
    step_lat = (config.radius * 2 / grid_size) * lat_per_meter
    step_lon = (config.radius * 2 / grid_size) * lon_per_meter

    all_offices: list[RealEstateOffice] = []
    cell_count = 0

    start_y = center_y - config.radius * lat_per_meter + step_lat / 2
    start_x = center_x - config.radius * lon_per_meter + step_lon / 2

    for row in range(grid_size):
        for col in range(grid_size):
            cell_count += 1
            cx = start_x + col * step_lon
            cy = start_y + row * step_lat

            print(f"  셀 {cell_count}/{grid_size * grid_size} ({cx:.6f}, {cy:.6f})")

            documents, total_count = client.search_all_pages(
                category_group_code=config.category_group_code,
                x=str(cx),
                y=str(cy),
                radius=cell_radius,
            )

            if total_count > len(documents):
                print(
                    f"    ⚠ 셀 결과 잘림: {total_count}건 중 {len(documents)}건만 조회됨"
                )

            offices = [RealEstateOffice.from_api_response(doc) for doc in documents]
            all_offices.extend(offices)

    all_offices = _deduplicate(all_offices)
    print(f"[격자 검색 완료] 중복 제거 후 총 {len(all_offices)}건")
    return all_offices
