from dataclasses import dataclass, field
from pathlib import Path

import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class SearchConfig:
    x: str = "127.341529"
    y: str = "36.353698"
    radius: int = 5000
    category_group_code: str = "AG2"


@dataclass
class ApiConfig:
    base_url: str = "https://dapi.kakao.com/v2/local/search/category.json"
    api_key: str = field(default_factory=lambda: os.getenv("KAKAO_REST_API_KEY", ""))
    page_size: int = 15
    max_page: int = 45
    request_delay: float = 0.2


@dataclass
class ExportConfig:
    output_dir: Path = field(default_factory=lambda: Path("output"))
    filename: str = "유성온천역_부동산"
