import csv

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

from query import Query


class ResalePriceData:
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
            "resale_price": ResalePrice(),  # Querying
        }

    def add_data(self, row):
        for i, col in enumerate(self.columns.keys()):
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

    def area_query(self, rows_scanned, col_idx):
        area_position_match = []
        for i, area in enumerate(self.columns["floor_area_sqm"].data):
            rows_scanned[col_idx] += 1
            if area >= 80:
                area_position_match.append(i)
        return area_position_match, rows_scanned

    def year_query(self, area_position_match, row_scanned, col_idx, year):
        year_position_match = []
        for i in area_position_match:
            row_scanned[col_idx] += 1
            if self.columns["month"].data[i]["year"] == year:
                year_position_match.append(i)
        return year_position_match, row_scanned

    def month_query(self, year_position_match, row_scanned, col_idx, month):
        month_position_match = []
        for i in year_position_match:
            row_scanned[col_idx] += 1
            if (
                self.columns["month"].data[i]["month"] == month
                or self.columns["month"].data[i]["month"] == month + 1
            ):
                month_position_match.append(i)
        return month_position_match, row_scanned

    def town_query(self, month_position_match, row_scanned, col_idx, town):
        town_position_match = []
        for i in month_position_match:
            row_scanned[col_idx] += 1
            if self.columns["town"].data[i] == town:
                town_position_match.append(i)
        return town_position_match, row_scanned

    def min_price_query(self, town_position_match):
        min_price = float("inf")
        for i in town_position_match:
            if self.columns["resale_price"].data[i] == "#NULL":
                continue
            elif self.columns["resale_price"].data[i] < min_price:
                min_price = self.columns["resale_price"].data[i]
        return min_price

    # Minimum Price
    def min_price(self, year, month, town, log_query=False):
        return Query.query(
            year,
            month,
            town,
            self.area_query,
            self.month_query,
            self.year_query,
            self.town_query,
            self.min_price_query,
            log_query=log_query,
        )

    def sd_price_query(self, town_position_match):
        prices = [
            self.columns["resale_price"].data[i]
            for i in town_position_match
            if self.columns["resale_price"].data[i] != "#NULL"
        ]

        if not prices:
            query_res = "No Results"
            row_used = 0
            mean_price = "No Results"
        else:
            mean_price = sum(prices) / len(prices)
            variance = sum((price - mean_price) ** 2 for price in prices) / (
                len(prices) - 1
            )
            query_res = round(variance**0.5, 2)
            row_used = len(prices)
        return query_res, row_used, mean_price

    # Standard Deviation of Price
    def sd_price(self, year, month, town, log_query=False):
        # price
        return Query.query(
            year,
            month,
            town,
            self.area_query,
            self.month_query,
            self.year_query,
            self.town_query,
            self.sd_price_query,
            log_query=log_query,
        )

    def avg_price_query(self, town_position_match):
        # price
        prices = [
            self.columns["resale_price"].data[i]
            for i in town_position_match
            if self.columns["resale_price"].data[i] != "#NULL"
        ]

        if not prices:
            query_res = "No Results"
            row_used = 0
        else:
            mean_price = sum(prices) / len(prices)
            query_res = round(mean_price, 2)
            row_used = len(prices)
        return query_res, row_used

    # Average Price
    def avg_price(self, year, month, town, log_query=False):
        return Query.query(
            year,
            month,
            town,
            self.area_query,
            self.month_query,
            self.year_query,
            self.town_query,
            self.avg_price_query,
            log_query=log_query,
        )

    def min_price_per_sqm_query(self, town_position_match):
        min_price_per_sqm = float("inf")
        for i in town_position_match:
            if (
                self.columns["resale_price"].data[i] == "#NULL"
                or self.columns["floor_area_sqm"].data[i] == "#NULL"
            ):
                continue
            price_per_sqm = (
                self.columns["resale_price"].data[i]
                / self.columns["floor_area_sqm"].data[i]
            )
            if price_per_sqm < min_price_per_sqm:
                min_price_per_sqm = price_per_sqm

        if min_price_per_sqm == float("inf"):
            query_res = "No Results"
        else:
            query_res = round(min_price_per_sqm, 2)
        return query_res

    # Minimum Price per Square Meter
    def min_price_per_sqm(self, year, month, town, log_query=False):
        return Query.query(
            year,
            month,
            town,
            self.area_query,
            self.month_query,
            self.year_query,
            self.town_query,
            self.min_price_per_sqm_query,
            log_query=log_query,
        )

    def shared_scan_query(self, town_position_match):
        min_price = float("inf")
        min_price_per_sqm = float("inf")

        # price for all 4 metrics
        prices = [self.columns["resale_price"].data[i] for i in town_position_match]

        # sd & avg price
        if not prices:
            sd_price = "No Results"
            avg_price = "No Results"
        else:
            mean_price = sum(prices) / len(prices)
            variance = sum((price - mean_price) ** 2 for price in prices) / (
                len(prices) - 1
            )

            # metrics to return
            sd_price = round(variance**0.5, 2)
            avg_price = round(mean_price, 2)

        for i in town_position_match:
            # min price
            if self.columns["resale_price"].data[i] < min_price:
                min_price = self.columns["resale_price"].data[i]

            # min price per sqm
            price_per_sqm = (
                self.columns["resale_price"].data[i]
                / self.columns["floor_area_sqm"].data[i]
            )
            if price_per_sqm < min_price_per_sqm:
                min_price_per_sqm = price_per_sqm

        if min_price_per_sqm == float("inf"):
            min_price_per_sqm = "No Results"
        else:
            min_price_per_sqm = round(min_price_per_sqm, 2)

        if min_price == float("inf"):
            min_price = "No Results"
        else:
            min_price = round(min_price, 2)

        return min_price, sd_price, avg_price, min_price_per_sqm

    # shared scan to obtain all 4 metrics
    def shared_scan(self, year, month, town, log_query=False):
        return Query.query(
            year,
            month,
            town,
            self.area_query,
            self.month_query,
            self.year_query,
            self.town_query,
            self.shared_scan_query,
            log_query=log_query,
        )


def column_store():
    file_path = "ResalePricesSingapore.csv"
    resale_data = ResalePriceData()
    with open(file_path, mode="r") as file:
        csv_reader = csv.reader(file)
        _ = next(csv_reader)
        for row in csv_reader:
            resale_data.add_data(row)
    return resale_data


if __name__ == "__main__":
    Query.column_store_query(column_store())
