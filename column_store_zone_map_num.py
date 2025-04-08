import csv
import time
from collections import defaultdict

import pandas as pd

from query import Query

from column_preprocess import ZoneMappingNum
from column_store import ResalePriceData


class ResalePriceDataZoneMapNum(ResalePriceData):
    def __init__(self):
        super().__init__()
        self.floor_area_sqm_zone_map = None

    def create_zone_map(self, num_zones):
        self.floor_area_sqm_zone_map = ZoneMappingNum("floor_area_sqm", num_zones)
        self.floor_area_sqm_zone_map.fit(self.columns["floor_area_sqm"].data)

    def area_query(self, rows_scanned, col_idx):
        area_position_zones = []
        for i, j in self.floor_area_sqm_zone_map.zones.items():
            if j[1] >= 80:
                area_position_zones.append(i)

        area_position_match = []
        for i in area_position_zones:
            start_index = i * self.floor_area_sqm_zone_map.rows_per_zone
            end_index = min(
                (i + 1) * self.floor_area_sqm_zone_map.rows_per_zone,
                len(self.columns["floor_area_sqm"].data),
            )
            for j in range(start_index, end_index):
                if self.columns["floor_area_sqm"].data[j] >= 80:
                    area_position_match.append(j)

        return area_position_match, rows_scanned

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
    matric_number = "U2121223J"

    last_digit_year = int(matric_number[-2])
    year = year_map[last_digit_year]
    month = int(matric_number[-3])
    town_index = int(matric_number[-4])
    town = town_map[town_index]

    file_path = "ResalePricesSingapore.csv"
    resale_data = ResalePriceDataZoneMapNum()
    with open(file_path, mode="r") as file:
        csv_reader = csv.reader(file)
        _ = next(csv_reader)
        for row in csv_reader:
            resale_data.add_data(row)

    # Creating zone map on flat_type column
    resale_data.create_zone_map(16)

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
    print("Average price: ", avg_price[0])
    print(f"Time taken for avg_price: {end_time - start_time} seconds")
    total_time += end_time - start_time
    print()

    start_time = time.time()
    min_price_per_sqm = resale_data.min_price_per_sqm(year, month, town)
    end_time = time.time()
    print("Minimum price per sqm: ", min_price_per_sqm[0])
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
