from typing import List, Union
from abc import abstractmethod

class BaseColumn:

    @abstractmethod
    def add_data(self, val):
        pass
    
class Month(BaseColumn):
    def __init__(self):
        super().__init__()
        self.data: list[dict[str, int]] = []

    def add_data(self, val: str):
        year, month = map(int, val.split("-"))
        self.data.append({"year": year, "month": month})

class Town(BaseColumn):
    def __init__(self):
        super().__init__()
        self.data: List[str] = []

    def add_data(self, val: str):
        self.data.append(val)

class TownEncoded(BaseColumn):
    def __init__(self):
        super().__init__()
        self.data: List[Union[str, int]] = []

    def add_data(self, val: Union[str, int]):
        self.data.append(val)

class FlatType(BaseColumn):
    def __init__(self):
        super().__init__()
        self.data: List[str] = []

    def add_data(self, val: str):
        self.data.append(val)

class Block(BaseColumn):
    def __init__(self):
        super().__init__()
        self.data: List[str] = []

    def add_data(self, val: str):
        self.data.append(val)

class StreetName(BaseColumn):
    def __init__(self):
        super().__init__()
        self.data: List[str] = []

    def add_data(self, val: str):
        self.data.append(val)

class StoreyRange(BaseColumn):
    def __init__(self):
        super().__init__()
        self.data: List[str] = []

    def add_data(self, val: str):
        self.data.append(val)

class FloorAreaSqm(BaseColumn):
    def __init__(self):
        super().__init__()
        self.data: List[float] = []

    def add_data(self, val: float):
        self.data.append(val)

class FlatModel(BaseColumn):
    def __init__(self):
        super().__init__()
        self.data: List[str] = []

    def add_data(self, val: str):
        self.data.append(val)

class LeaseCommenceDate(BaseColumn):
    def __init__(self):
        super().__init__()
        self.data: List[int] = []

    def add_data(self, val: int):
        self.data.append(val)

class ResalePrice(BaseColumn):
    def __init__(self):
        super().__init__()
        self.data: List[float] = []

    def add_data(self, val: float):
        self.data.append(val)