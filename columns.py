from typing import List, Union
from abc import ABC, abstractmethod


class BaseColumn(ABC):
    @abstractmethod
    def add_data(self, val):
        pass


class Month(BaseColumn):
    def __init__(self):
        self.data: list[dict[str, int]] = []

    def add_data(self, val: str):
        if val:
            year, month = map(int, val.split("-"))
            self.data.append({"year": int(year), "month": int(month)})

        # null value
        else:
            self.data.append("#NULL")


class Town(BaseColumn):
    def __init__(self):
        self.data: List[str] = []

    def add_data(self, val: str):
        if val:
            self.data.append(val)

        # null value
        else:
            self.data.append("#NULL")


class TownEncoded(BaseColumn):
    def __init__(self):
        self.data: List[Union[str, int]] = []

    def add_data(self, val: Union[str, int]):
        if val:
            self.data.append(val)

        # null value
        else:
            self.data.append("#NULL")


class FlatType(BaseColumn):
    def __init__(self):
        self.data: List[str] = []

    def add_data(self, val: str):
        if val:
            self.data.append(val)

        # null value
        else:
            self.data.append("#NULL")


class Block(BaseColumn):
    def __init__(self):
        self.data: List[str] = []

    def add_data(self, val: str):
        if val:
            self.data.append(val)

        # null value
        else:
            self.data.append("#NULL")


class StreetName(BaseColumn):
    def __init__(self):
        self.data: List[str] = []

    def add_data(self, val: str):
        if val:
            self.data.append(val)

        # null value
        else:
            self.data.append("#NULL")


class StoreyRange(BaseColumn):
    def __init__(self):
        self.data: List[str] = []

    def add_data(self, val: str):
        if val:
            self.data.append(val)

        # null value
        else:
            self.data.append("#NULL")


class FloorAreaSqm(BaseColumn):
    def __init__(self):
        self.data: List[float] = []

    def add_data(self, val: float):
        if val:
            self.data.append(float(val))

        # null value
        else:
            self.data.append("#NULL")


class FlatModel(BaseColumn):
    def __init__(self):
        self.data: List[str] = []

    def add_data(self, val: str):
        if val:
            self.data.append(val)

        # null value
        else:
            self.data.append("#NULL")


class LeaseCommenceDate(BaseColumn):
    def __init__(self):
        self.data: List[int] = []

    def add_data(self, val: int):
        if val:
            self.data.append(int(val))

        # null value
        else:
            self.data.append("#NULL")


class ResalePrice(BaseColumn):
    def __init__(self):
        self.data: List[float] = []

    def add_data(self, val: float):
        if val:
            self.data.append(float(val))

        # null value
        else:
            self.data.append("#NULL")
