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

from column_preprocess import ZoneMapping, CategoricalEncoder


class ResalePriceDataCombined:
    def __init__(self):
        self.month = Month()  # Querying
        self.town = TownEncoded()  # Querying
        self.flat_type = FlatType()
        self.block = Block()
        self.street_name = StreetName()
        self.storey_range = StoreyRange()
        self.floor_area_sqm = FloorAreaSqm()  # Querying
        self.flat_model = FlatModel()
        self.lease_commence_date = LeaseCommenceDate()
        self.resale_price = ResalePrice()  # Querying

    def add_data(
        self,
        month,
        town,
        flat_type,
        block,
        street_name,
        storey_range,
        floor_area_sqm,
        flat_model,
        lease_commence_date,
        resale_price,
    ):
        self.month.add_month(month)
        self.town.add_town(town)
        self.flat_type.add_type(flat_type)
        self.block.add_block(block)
        self.street_name.add_street(street_name)
        self.storey_range.add_range(storey_range)
        self.floor_area_sqm.add_area(floor_area_sqm)
        self.flat_model.add_model(flat_model)
        self.lease_commence_date.add_date(lease_commence_date)
        self.resale_price.add_price(resale_price)

    def encode_town(self):
        self.town_encoder = CategoricalEncoder("town", self.town.towns)
        self.town.towns = self.town_encoder.transform(self.town.towns)

    def create_zone_map(self, num_zones):
        self.floor_area_sqm_zone_map = ZoneMapping("floor_area_sqm", num_zones)
        self.floor_area_sqm_zone_map.fit(self.floor_area_sqm.areas)

    def __str__(self):
        return (
            f"Months: {self.month.months}\n"
            f"Towns: {self.town.towns}\n"
            f"Flat Types: {self.flat_type.types}\n"
            f"Blocks: {self.block.blocks}\n"
            f"Street Names: {self.street_name.streets}\n"
            f"Storey Ranges: {self.storey_range.ranges}\n"
            f"Floor Areas (sqm): {self.floor_area_sqm.areas}\n"
            f"Flat Models: {self.flat_model.models}\n"
            f"Lease Commence Dates: {self.lease_commence_date.dates}\n"
            f"Resale Prices: {self.resale_price.prices}\n"
        )

    # Minimum Price
    def min_price(self, year, month, town):
        min_price = float("inf")

        # start with area
        area_position_zones = []
        for i, j in self.floor_area_sqm_zone_map.zones.items():
            if j[1] >= 80:
                area_position_zones.append(i)

        area_position_match = []
        for i in area_position_zones:
            start_index = i * self.floor_area_sqm_zone_map.rows_per_zone
            end_index = min(
                (i + 1) * self.floor_area_sqm_zone_map.rows_per_zone,
                len(self.floor_area_sqm.areas),
            )
            for j in range(start_index, end_index):
                if self.floor_area_sqm.areas[j] >= 80:
                    area_position_match.append(j)
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
        area_position_zones = []
        for i, j in self.floor_area_sqm_zone_map.zones.items():
            if j[1] >= 80:
                area_position_zones.append(i)

        area_position_match = []
        for i in area_position_zones:
            start_index = i * self.floor_area_sqm_zone_map.rows_per_zone
            end_index = min(
                (i + 1) * self.floor_area_sqm_zone_map.rows_per_zone,
                len(self.floor_area_sqm.areas),
            )
            for j in range(start_index, end_index):
                if self.floor_area_sqm.areas[j] >= 80:
                    area_position_match.append(j)

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
        variance = sum((price - mean_price) ** 2 for price in prices) / len(prices)
        return round(variance**0.5, 2)

    # Average Price
    def avg_price(self, year, month, town):
        # start with area
        area_position_zones = []
        for i, j in self.floor_area_sqm_zone_map.zones.items():
            if j[1] >= 80:
                area_position_zones.append(i)

        area_position_match = []
        for i in area_position_zones:
            start_index = i * self.floor_area_sqm_zone_map.rows_per_zone
            end_index = min(
                (i + 1) * self.floor_area_sqm_zone_map.rows_per_zone,
                len(self.floor_area_sqm.areas),
            )
            for j in range(start_index, end_index):
                if self.floor_area_sqm.areas[j] >= 80:
                    area_position_match.append(j)

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
        area_position_zones = []
        for i, j in self.floor_area_sqm_zone_map.zones.items():
            if j[1] >= 80:
                area_position_zones.append(i)

        area_position_match = []
        for i in area_position_zones:
            start_index = i * self.floor_area_sqm_zone_map.rows_per_zone
            end_index = min(
                (i + 1) * self.floor_area_sqm_zone_map.rows_per_zone,
                len(self.floor_area_sqm.areas),
            )
            for j in range(start_index, end_index):
                if self.floor_area_sqm.areas[j] >= 80:
                    area_position_match.append(j)

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
