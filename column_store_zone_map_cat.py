import csv

from column_preprocess import ZoneMappingCat
from column_store import ResalePriceData
from query import Query


class ResalePriceDataZoneMapCat(ResalePriceData):
    def __init__(self):
        super().__init__()
        self.zone_mapping = None
        self.rearranged_columns = None

    def create_zone_map(self, col_name):
        self.zone_mapping, self.rearranged_columns = ZoneMappingCat().fit(
            self, col_name
        )

    def area_query(self, rows_scanned, col_idx):
        # start with area
        area_position_match = []
        # iterate through area position zones\
        print(self.zone_mapping)
        for v in self.zone_mapping.values():
            zone_max_val = v["zone_max"]
            zone_start_idx = v["start_idx"]
            zone_end_idx = v["end_idx"]

            # skip zones whos max is < 80
            if zone_max_val < 80:
                continue

            else:
                for i in range(zone_start_idx, zone_end_idx + 1):
                    rows_scanned[col_idx] += 1
                    if self.rearranged_columns["floor_area_sqm"][i] >= 80:
                        area_position_match.append(i)
        return area_position_match, rows_scanned

    def year_query(self, area_position_match, rows_scanned, col_idx, year):
        year_position_match = []
        for i in area_position_match:
            rows_scanned[col_idx] += 1
            if self.rearranged_columns["month"][i]["year"] == year:
                year_position_match.append(i)
        return year_position_match, rows_scanned

    def month_query(self, year_position_match, rows_scanned, col_idx, month):
        month_position_match = []
        for i in year_position_match:
            rows_scanned[col_idx] += 1
            if (
                self.rearranged_columns["month"][i]["month"] == month
                or self.rearranged_columns["month"][i]["month"] == month + 1
            ):
                month_position_match.append(i)
        return month_position_match, rows_scanned

    def town_query(self, month_position_match, row_scanned, col_idx, town):
        town_position_match = []
        for i in month_position_match:
            row_scanned[col_idx] += 1
            if self.rearranged_columns["town"][i] == town:
                town_position_match.append(i)
        return town_position_match, row_scanned

    def min_price_query(self, town_position_match):
        min_price = float("inf")
        for i in town_position_match:
            if self.rearranged_columns["resale_price"][i] == "#NULL":
                continue
            elif self.rearranged_columns["resale_price"][i] < min_price:
                min_price = self.rearranged_columns["resale_price"][i]
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
            self.rearranged_columns["resale_price"][i]
            for i in town_position_match
            if self.rearranged_columns["resale_price"][i] != "#NULL"
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
        prices = [
            self.rearranged_columns["resale_price"][i]
            for i in town_position_match
            if self.rearranged_columns["resale_price"][i] != "#NULL"
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
        # price
        min_price_per_sqm = float("inf")

        for i in town_position_match:
            if (
                self.rearranged_columns["resale_price"][i] == "#NULL"
                or self.rearranged_columns["floor_area_sqm"][i] == "#NULL"
            ):
                continue
            price_per_sqm = (
                self.rearranged_columns["resale_price"][i]
                / self.rearranged_columns["floor_area_sqm"][i]
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
        prices = [
            self.rearranged_columns["resale_price"][i] for i in town_position_match
        ]

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
            if self.rearranged_columns["resale_price"][i] < min_price:
                min_price = self.rearranged_columns["resale_price"][i]

            # min price per sqm
            price_per_sqm = (
                self.rearranged_columns["resale_price"][i]
                / self.rearranged_columns["floor_area_sqm"][i]
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


def column_store_zone_map_cat():
    file_path = "ResalePricesSingapore.csv"
    resale_data = ResalePriceDataZoneMapCat()
    with open(file_path, mode="r") as file:
        csv_reader = csv.reader(file)
        _ = next(csv_reader)
        for row in csv_reader:
            resale_data.add_data(row)

    # Creating zone map on flat_type column
    resale_data.create_zone_map("flat_type")
    return resale_data


if __name__ == "__main__":
    Query.column_store_query(column_store_zone_map_cat())
