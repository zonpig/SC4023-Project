from columns import (
    Month,
    Town,
    FlatType,
    Block,
    StreetName,
    StoreyRange,
    FloorAreaSqm,
    FlatModel,
    LeaseCommenceDate,
    ResalePrice,
)


class ResalePriceData:
    def __init__(self):
        self.month = Month()  # Querying
        self.town = Town()  # Querying
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
            if self.town.towns[i] == town:
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
            if self.town.towns[i] == town:
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
            if self.town.towns[i] == town:
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
            if self.town.towns[i] == town:
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
