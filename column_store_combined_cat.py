import csv
import time


from column_store_zone_map_cat import ResalePriceDataZoneMapCat

from column_preprocess import ZoneMappingCat, CategoricalEncoder
from collections import defaultdict
import pandas as pd


class ResalePriceDataCombinedCat(ResalePriceDataZoneMapCat):
    def __init__(self):
        super().__init__()
        self.town_encoder = None

    def encode_town(self):
        self.town_encoder = CategoricalEncoder("town", self.rearranged_columns["town"])
        self.rearranged_columns["town"] = self.town_encoder.transform(
            self.rearranged_columns["town"]
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
    matric_number = "U2121223J"  # Darren
    # matric_number = "U2121763H" #Bryan
    # matric_number = "U2122055E" #Jin Yang

    last_digit_year = int(matric_number[-2])
    year = year_map[last_digit_year]
    month = int(matric_number[-3])
    town_index = int(matric_number[-4])
    town = town_map[town_index]

    file_path = "ResalePricesSingapore.csv"
    resale_data = ResalePriceDataCombinedCat()
    with open(file_path, mode="r") as file:
        csv_reader = csv.reader(file)
        _ = next(csv_reader)
        for row in csv_reader:
            resale_data.add_data(row)

    # Creating zone map on flat_type column
    resale_data.create_zone_map("flat_type")
    resale_data.encode_town()  # have to do this after zonemapping to encode town on the rearranged columns
    encoded_town = resale_data.town_encoder.mappings[town]

    # total time to keep track of cummulative timing for 4 individual queries
    total_time = 0

    start_time = time.time()
    min_price = resale_data.min_price(year, month, encoded_town)
    end_time = time.time()
    print("Minimum price: ", min_price)
    print(f"Time taken for min_price: {end_time - start_time} seconds")
    total_time += end_time - start_time
    print()

    start_time = time.time()
    sd_price = resale_data.sd_price(year, month, encoded_town)
    end_time = time.time()
    print("StdDev price: ", sd_price)
    print(f"Time taken for sd_price: {end_time - start_time} seconds")
    total_time += end_time - start_time
    print()

    start_time = time.time()
    avg_price = resale_data.avg_price(year, month, encoded_town)
    end_time = time.time()
    print("Average price: ", avg_price)
    print(f"Time taken for avg_price: {end_time - start_time} seconds")
    total_time += end_time - start_time
    print()

    start_time = time.time()
    min_price_per_sqm = resale_data.min_price_per_sqm(year, month, encoded_town)
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
        resale_data.shared_scan(year, month, encoded_town)
    )
    end_time = time.time()
    print("Shared Scan - Minimum price: ", ss_min_price)
    print("Shared Scan - Minimum price per sqm: ", ss_sd_price)
    print("Shared Scan - Minimum price per sqm: ", ss_avg_price)
    print("Shared Scan - Minimum price per sqm: ", ss_min_price_per_sqm)
    print(f"Time taken for Shared Scan: {end_time - start_time} seconds")


if __name__ == "__main__":
    main()
