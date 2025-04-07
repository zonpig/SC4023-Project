import csv
import time

from query import Query
from column_preprocess import ZoneMappingCat
from collections import defaultdict
import pandas as pd
from column_store import ResalePriceData


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
        # iterate through area position zones
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
            return "No Results"
        else:
            mean_price = sum(prices) / len(prices)
            variance = sum((price - mean_price) ** 2 for price in prices) / (
                len(prices) - 1
            )
            return round(variance**0.5, 2)

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
        else:
            mean_price = sum(prices) / len(prices)
            query_res = round(mean_price, 2)
        return query_res

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
                self.rearranged_columns["resale_price"][i] != "#NULL"
                or self.rearranged_columns["floor_area_sqm"][i] != "#NULL"
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

    # shared scan to obtain all 4 metrics
    def shared_scan(self, year, month, town, log_query=False):
        min_price = float("inf")
        min_price_per_sqm = float("inf")

        rows_scanned = [0] * 4
        col_idx = 0

        # start with area
        area_position_match = []
        # iterate through area position zones
        for k, v in self.zone_mapping.items():
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
        col_idx += 1

        # month
        month_position_match = []
        for i in area_position_match:
            rows_scanned[col_idx] += 1
            if (
                self.rearranged_columns["month"][i]["month"] == month
                or self.rearranged_columns["month"][i]["month"] == month + 1
            ):
                month_position_match.append(i)
        col_idx += 1

        # year
        year_position_match = []
        for i in month_position_match:
            rows_scanned[col_idx] += 1
            if self.rearranged_columns["month"][i]["year"] == year:
                year_position_match.append(i)
        col_idx += 1

        # town
        town_position_match = []
        for i in year_position_match:
            rows_scanned[col_idx] += 1
            if self.rearranged_columns["town"][i] == town:
                town_position_match.append(i)
        col_idx += 1

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

        if log_query:
            col_string = ""
            query_lengths = {}
            col_string += "->floor_area_sqm"
            query_lengths[col_string] = rows_scanned[0]
            col_string += "->month"
            query_lengths[col_string] = rows_scanned[1]
            col_string += "->year"
            query_lengths[col_string] = rows_scanned[2]
            col_string += "->town"
            query_lengths[col_string] = rows_scanned[3]
            query_lengths_df = pd.DataFrame(
                data={
                    "cols": [k for k in query_lengths.keys()],
                    "lengths": [v for _, v in query_lengths.items()],
                }
            )
            return min_price, sd_price, avg_price, min_price_per_sqm, query_lengths_df
        return min_price, sd_price, avg_price, min_price_per_sqm


def main():
    town_map = {
        0: "BEDOK",
        1: "BUKIT PANJANG",
        2: "CLEMENTI",
        3: "CHOA CHU KANG",
        4: "HOUGANG",
        5: "JURONG WEST",
        6: "PASIR RIS",
        7: "TAMPINES",
        8: "WOODLANDS",
        9: "YISHUN",
    }

    year_map = {
        0: 2020,
        1: 2021,
        2: 2022,
        3: 2023,
        4: 2014,
        5: 2015,
        6: 2016,
        7: 2017,
        8: 2018,
        9: 2019,
    }

    # matric number
    matric_number = "U2121223J"  # Darren
    # matric_number = "U2121763H" #Bryan
    # matric_number = "U2122055E" #Jin Yang

    last_digit_year = int(matric_number[-2])
    year = year_map[last_digit_year]
    month = int(matric_number[-3])
    town_index = int(matric_number[-4])
    town = town_map[town_index]

    file_path = "ResalePricesSingapore.csv"
    resale_data = ResalePriceDataZoneMapCat()
    with open(file_path, mode="r") as file:
        csv_reader = csv.reader(file)
        _ = next(csv_reader)
        for row in csv_reader:
            resale_data.add_data(row)

    # Creating zone map on flat_type column
    resale_data.create_zone_map("flat_type")

    # total time to keep track of cummulative timing for 4 individual queries
    total_time = 0

    start_time = time.time()
    min_price = resale_data.min_price(year, month, town)
    end_time = time.time()
    print("Minimum price: ", min_price)
    print(f"Time taken for min_price: {end_time - start_time} seconds")
    total_time += end_time - start_time
    print()

    start_time = time.time()
    sd_price = resale_data.sd_price(year, month, town)
    end_time = time.time()
    print("StdDev price: ", sd_price)
    print(f"Time taken for sd_price: {end_time - start_time} seconds")
    total_time += end_time - start_time
    print()

    start_time = time.time()
    avg_price = resale_data.avg_price(year, month, town)
    end_time = time.time()
    print("Average price: ", avg_price)
    print(f"Time taken for avg_price: {end_time - start_time} seconds")
    total_time += end_time - start_time
    print()

    start_time = time.time()
    min_price_per_sqm = resale_data.min_price_per_sqm(year, month, town)
    end_time = time.time()
    print("Minimum price per sqm: ", min_price_per_sqm)
    print(f"Time taken for min_price_per_sqm: {end_time - start_time} seconds")
    total_time += end_time - start_time
    print()

    # cummulative timing
    print(f"Total time taken for 4 individual queries: {total_time} seconds")
    print()

    # shared scan
    start_time = time.time()
    ss_min_price, ss_sd_price, ss_avg_price, ss_min_price_per_sqm = (
        resale_data.shared_scan(year, month, town)
    )
    end_time = time.time()
    print("Shared Scan - Minimum price: ", ss_min_price)
    print("Shared Scan - Minimum price per sqm: ", ss_sd_price)
    print("Shared Scan - Minimum price per sqm: ", ss_avg_price)
    print("Shared Scan - Minimum price per sqm: ", ss_min_price_per_sqm)
    print(f"Time taken for Shared Scan: {end_time - start_time} seconds")


if __name__ == "__main__":
    main()
