class Month:
    def __init__(self):
        self.months: list[dict[str, int]] = []

    def add_month(self, month: str):
        year, month = map(int, month.split("-"))
        self.months.append({"year": year, "month": month})


class Town:
    def __init__(self):
        self.towns: list[str] = []

    def add_town(self, name: str):
        self.towns.append(name)


class TownEncoded:
    def __init__(self):
        self.towns: list[str | int] = []

    def add_town(self, name: str | int):
        self.towns.append(name)


class FlatType:
    def __init__(self):
        self.types: list[str] = []

    def add_type(self, type: str):
        self.types.append(type)


class Block:
    def __init__(self):
        self.blocks: list[str] = []

    def add_block(self, block: str):
        self.blocks.append(block)


class StreetName:
    def __init__(self):
        self.streets: list[str] = []

    def add_street(self, street: str):
        self.streets.append(street)


class StoreyRange:
    def __init__(self):
        self.ranges: list[str] = []

    def add_range(self, range: str):
        self.ranges.append(range)


class FloorAreaSqm:
    def __init__(self):
        self.areas: list[float] = []

    def add_area(self, area: float):
        self.areas.append(area)


class FlatModel:
    def __init__(self):
        self.models: list[str] = []

    def add_model(self, model: str):
        self.models.append(model)


class LeaseCommenceDate:
    def __init__(self):
        self.dates: list[int] = []

    def add_date(self, date: int):
        self.dates.append(date)


class ResalePrice:
    def __init__(self):
        self.prices: list[float] = []

    def add_price(self, price: float):
        self.prices.append(price)
