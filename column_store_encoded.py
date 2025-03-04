from columns import (
    Month,
    TownEncoded,
    FlatType,
    Block,
    StreetName,
    StoreyRange,
    FloorAreaSqm,
    FlatModel,
    LeaseCommenceDate,
    ResalePrice,
)

from column_preprocess import CategoricalEncoder


class ResalePriceDataEncoded:
    def __init__(self):
        self.columns = {
            "month": Month(),  # Querying
            "town": Town(),  # Querying
            "flat_type": FlatType(),
            "block": Block(),
            "street_name": StreetName(),
            "storey_range": StoreyRange(),
            "floor_area_sqm": FloorAreaSqm(),  # Querying
            "flat_model": FlatModel(),
            "lease_commence_date": LeaseCommenceDate(),
            "resale_price": ResalePrice()  # Querying
        }

    # Jinyang's
    def add_data(self,row):
        for i,col in enumerate(self.columns.keys()):
            self.columns[col].add_data(row[i])

    def __str__(self):
        return (
            f"Months: {self.columns['month'].data}\n"
            f"Towns: {self.columns['town'].data}\n"
            f"Flat Types: {self.columns['flat_type'].data}\n"
            f"Blocks: {self.columns['block'].data}\n"
            f"Street Names: {self.columns['street_name'].data}\n"
            f"Storey Ranges: {self.columns['storey_range'].data}\n"
            f"Floor Areas (sqm): {self.columns['floor_area_sqm'].data}\n"
            f"Flat Models: {self.columns['flat_model'].data}\n"
            f"Lease Commence Dates: {self.columns['lease_commence_date'].data}\n"
            f"Resale Prices: {self.columns['resale_price'].data}\n"
        )
        
    def encode_town(self):
        self.town_encoder = CategoricalEncoder("town", self.town.towns)
        self.town.towns = self.town_encoder.transform(self.town.towns)

    # Minimum Price
    def min_price(self, year, month, town):
        min_price = float("inf")

        # start with area
        area_position_match = []
        for i, area in enumerate(self.floor_area_sqm.areas):
            if area >= 80:
                area_position_match.append(i)

        # month
        month_position_match = []
        for i in area_position_match:
            if (
                self.month.months[i]["month"] == month
                or self.month.months[i]["month"] == month + 1
            ):
                month_position_match.append(i)

        # year
        year_position_match = []
        for i in month_position_match:
            if self.month.months[i]["year"] == year:
                year_position_match.append(i)

        # town
        town_position_match = []
        for i in year_position_match:
            if self.town.towns[i] == self.town_encoder.transform(town):
                town_position_match.append(i)

        # price
        for i in town_position_match:
            if self.resale_price.prices[i] < min_price:
                min_price = self.resale_price.prices[i]

        return min_price if min_price != float("inf") else "No result"

    # Standard Deviation of Price
    def sd_price(self, year, month, town):
        # start with area
        area_position_match = []
        for i, area in enumerate(self.floor_area_sqm.areas):
            if area >= 80:
                area_position_match.append(i)

        # month
        month_position_match = []
        for i in area_position_match:
            if (
                self.month.months[i]["month"] == month
                or self.month.months[i]["month"] == month + 1
            ):
                month_position_match.append(i)

        # year
        year_position_match = []
        for i in month_position_match:
            if self.month.months[i]["year"] == year:
                year_position_match.append(i)

        # town
        town_position_match = []
        for i in year_position_match:
            if self.town.towns[i] == self.town_encoder.transform(town):
                town_position_match.append(i)

        # price
        prices = [self.resale_price.prices[i] for i in town_position_match]
        if not prices:
            return "No result"
        mean_price = sum(prices) / len(prices)
        variance = sum((price - mean_price) ** 2 for price in prices) / (
            len(prices) - 1
        )        
        return round(variance**0.5, 2)

    # Average Price
    def avg_price(self, year, month, town):
        # start with area
        area_position_match = []
        for i, area in enumerate(self.floor_area_sqm.areas):
            if area >= 80:
                area_position_match.append(i)

        # month
        month_position_match = []
        for i in area_position_match:
            if (
                self.month.months[i]["month"] == month
                or self.month.months[i]["month"] == month + 1
            ):
                month_position_match.append(i)

        # year
        year_position_match = []
        for i in month_position_match:
            if self.month.months[i]["year"] == year:
                year_position_match.append(i)

        # town
        town_position_match = []
        for i in year_position_match:
            if self.town.towns[i] == self.town_encoder.transform(town):
                town_position_match.append(i)

        # price
        prices = [self.resale_price.prices[i] for i in town_position_match]
        if not prices:
            return "No Results"
        mean_price = sum(prices) / len(prices)
        return round(mean_price, 2)

    # Minimum Price per Square Meter
    def min_price_per_sqm(self, year, month, town):
        min_price_per_sqm = float("inf")

        # start with area
        area_position_match = []
        for i, area in enumerate(self.floor_area_sqm.areas):
            if area >= 80:
                area_position_match.append(i)

        # month
        month_position_match = []
        for i in area_position_match:
            if (
                self.month.months[i]["month"] == month
                or self.month.months[i]["month"] == month + 1
            ):
                month_position_match.append(i)

        # year
        year_position_match = []
        for i in month_position_match:
            if self.month.months[i]["year"] == year:
                year_position_match.append(i)

        # town
        town_position_match = []
        for i in year_position_match:
            if self.town.towns[i] == self.town_encoder.transform(town):
                town_position_match.append(i)

        # price
        for i in town_position_match:
            price_per_sqm = self.resale_price.prices[i] / self.floor_area_sqm.areas[i]
            if price_per_sqm < min_price_per_sqm:
                min_price_per_sqm = price_per_sqm

        return (
            round(min_price_per_sqm, 2)
            if min_price_per_sqm != float("inf")
            else "No result"
        )
