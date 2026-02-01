import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.utils import get_column_letter

from crawler.config import ExportConfig
from crawler.models import RealEstateOffice

HEADERS = [
    "업소명",
    "전화번호",
    "주소",
]


def _to_row(office: RealEstateOffice) -> list[str]:
    return [
        office.place_name,
        office.phone,
        office.address,
    ]


def save_csv(
    offices: list[RealEstateOffice],
    config: ExportConfig | None = None,
) -> Path:
    config = config or ExportConfig()
    config.output_dir.mkdir(parents=True, exist_ok=True)

    filepath = config.output_dir / f"{config.filename}.csv"

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        for office in offices:
            writer.writerow(_to_row(office))

    print(f"CSV 저장 완료: {filepath} ({len(offices)}건)")
    return filepath


def save_excel(
    offices: list[RealEstateOffice],
    config: ExportConfig | None = None,
) -> Path:
    config = config or ExportConfig()
    config.output_dir.mkdir(parents=True, exist_ok=True)

    filepath = config.output_dir / f"{config.filename}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "부동산 중개사무소"

    ws.append(HEADERS)

    for office in offices:
        ws.append(_to_row(office))

    # 컬럼 너비 자동 조정
    for col_idx, header in enumerate(HEADERS, 1):
        max_len = len(header)
        for row in ws.iter_rows(min_row=2, min_col=col_idx, max_col=col_idx):
            for cell in row:
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
        # 한글은 약 2배 너비 차지, 여유분 추가
        adjusted = min(max_len + 4, 50)
        ws.column_dimensions[get_column_letter(col_idx)].width = adjusted

    wb.save(filepath)
    print(f"Excel 저장 완료: {filepath} ({len(offices)}건)")
    return filepath
