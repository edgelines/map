from dataclasses import dataclass


@dataclass
class RealEstateOffice:
    place_name: str
    phone: str
    address_name: str
    road_address_name: str
    x: str
    y: str
    distance: str
    place_url: str
    category_name: str

    @classmethod
    def from_api_response(cls, data: dict) -> "RealEstateOffice":
        return cls(
            place_name=data.get("place_name", ""),
            phone=data.get("phone", ""),
            address_name=data.get("address_name", ""),
            road_address_name=data.get("road_address_name", ""),
            x=data.get("x", ""),
            y=data.get("y", ""),
            distance=data.get("distance", ""),
            place_url=data.get("place_url", ""),
            category_name=data.get("category_name", ""),
        )

    @property
    def address(self) -> str:
        return self.road_address_name or self.address_name

    def dedup_key(self) -> tuple[str, str]:
        return (self.place_name, self.phone)
