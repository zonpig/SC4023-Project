# import csv
# import time

import csv
import operator
import time

from column_store import ResalePriceData
from multiprocess import parallel_processing


class ResalePriceDataMP(ResalePriceData):
    # Minimum Price
    def min_price(self, year, month, town):
        min_price = float("inf")

        # STEP: Get floor_area_sqm
        area_position_match = parallel_processing(
            self.columns["floor_area_sqm"].data, criterions={"uni": [(operator.ge, 80)]}
        )
        months = [
            self.columns["month"].data[i]["month"]
            for i in range(len(self.columns["month"].data))
        ]
        years = [
            self.columns["month"].data[i]["year"]
            for i in range(len(self.columns["month"].data))
        ]

        # STEP: Get year
        year_position_match = parallel_processing(
            years,
            matched_idxs=area_position_match,
            criterions={"uni": [(operator.eq, year)]},
        )
        # STEP: Get month
        month_position_match = parallel_processing(
            months,
            matched_idxs=year_position_match,
            criterions={
                "or": [
                    (operator.eq, month),
                    (operator.eq, month + 1),
                ]
            },
        )

        # STEP: Get town
        town_position_match = parallel_processing(
            self.columns["town"].data,
            matched_idxs=month_position_match,
            criterions={"uni": [(operator.eq, town)]},
        )

        # price
        for i in town_position_match:
            if self.columns["resale_price"].data[i] < min_price:
                min_price = self.columns["resale_price"].data[i]

        return min_price if min_price != float("inf") else "No result"

    # Standard Deviation of Price
    def sd_price(self, year, month, town, log_query=False):
        # STEP: Get area
        area_position_match = parallel_processing(
            self.columns["floor_area_sqm"].data, criterions={"uni": [(operator.ge, 80)]}
        )
        months = [
            self.columns["month"].data[i]["month"]
            for i in range(len(self.columns["month"].data))
        ]
        years = [
            self.columns["month"].data[i]["year"]
            for i in range(len(self.columns["month"].data))
        ]

        # STEP: Get year
        year_position_match = parallel_processing(
            years,
            matched_idxs=area_position_match,
            criterions={"uni": [(operator.eq, year)]},
        )
        # STEP: Get month
        month_position_match = parallel_processing(
            months,
            matched_idxs=year_position_match,
            criterions={
                "or": [
                    (operator.eq, month),
                    (operator.eq, month + 1),
                ]
            },
        )

        # STEP: Get town
        town_position_match = parallel_processing(
            self.columns["town"].data,
            matched_idxs=month_position_match,
            criterions={"uni": [(operator.eq, town)]},
        )

        # STEP: Get price
        prices = [self.columns["resale_price"].data[i] for i in town_position_match]

        if not prices:
            query_res = "No Results"
            mean_price = 0
        else:
            mean_price = sum(prices) / len(prices)
            variance = sum((price - mean_price) ** 2 for price in prices) / (
                len(prices) - 1
            )
            query_res = round(variance**0.5, 2)

        return query_res, len(prices), mean_price

    # Average Price
    def avg_price(self, year, month, town, log_query=False):
        # STEP: Get area
        area_position_match = parallel_processing(
            self.columns["floor_area_sqm"].data, criterions={"uni": [(operator.ge, 80)]}
        )
        months = [
            self.columns["month"].data[i]["month"]
            for i in range(len(self.columns["month"].data))
        ]
        years = [
            self.columns["month"].data[i]["year"]
            for i in range(len(self.columns["month"].data))
        ]

        # STEP: Get year
        year_position_match = parallel_processing(
            years,
            matched_idxs=area_position_match,
            criterions={"uni": [(operator.eq, year)]},
        )
        # STEP: Get month
        month_position_match = parallel_processing(
            months,
            matched_idxs=year_position_match,
            criterions={
                "or": [
                    (operator.eq, month),
                    (operator.eq, month + 1),
                ]
            },
        )

        # STEP: Get town
        town_position_match = parallel_processing(
            self.columns["town"].data,
            matched_idxs=month_position_match,
            criterions={"uni": [(operator.eq, town)]},
        )

        # STEP: Get price
        prices = [self.columns["resale_price"].data[i] for i in town_position_match]

        if not prices:
            query_res = "No Results"
        else:
            mean_price = sum(prices) / len(prices)
            query_res = round(mean_price, 2)

        return query_res, len(prices)

    # Minimum Price per Square Meter
    def min_price_per_sqm(self, year, month, town, log_query=False):
        min_price_per_sqm = float("inf")

        # STEP: Get area
        area_position_match = parallel_processing(
            self.columns["floor_area_sqm"].data, criterions={"uni": [(operator.ge, 80)]}
        )
        months = [
            self.columns["month"].data[i]["month"]
            for i in range(len(self.columns["month"].data))
        ]
        years = [
            self.columns["month"].data[i]["year"]
            for i in range(len(self.columns["month"].data))
        ]

        # STEP: Get year
        year_position_match = parallel_processing(
            years,
            matched_idxs=area_position_match,
            criterions={"uni": [(operator.eq, year)]},
        )
        # STEP: Get month
        month_position_match = parallel_processing(
            months,
            matched_idxs=year_position_match,
            criterions={
                "or": [
                    (operator.eq, month),
                    (operator.eq, month + 1),
                ]
            },
        )

        # STEP: Get town
        town_position_match = parallel_processing(
            self.columns["town"].data,
            matched_idxs=month_position_match,
            criterions={"uni": [(operator.eq, town)]},
        )

        # price
        for i in town_position_match:
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

    def shared_scan(self, year, month, town, log_query=False):
        # STEP: Get area
        area_position_match = parallel_processing(
            self.columns["floor_area_sqm"].data, criterions={"uni": [(operator.ge, 80)]}
        )
        months = [
            self.columns["month"].data[i]["month"]
            for i in range(len(self.columns["month"].data))
        ]
        years = [
            self.columns["month"].data[i]["year"]
            for i in range(len(self.columns["month"].data))
        ]

        # STEP: Get year
        year_position_match = parallel_processing(
            years,
            matched_idxs=area_position_match,
            criterions={"uni": [(operator.eq, year)]},
        )
        # STEP: Get month
        month_position_match = parallel_processing(
            months,
            matched_idxs=year_position_match,
            criterions={
                "or": [
                    (operator.eq, month),
                    (operator.eq, month + 1),
                ]
            },
        )

        # STEP: Get town
        town_position_match = parallel_processing(
            self.columns["town"].data,
            matched_idxs=month_position_match,
            criterions={"uni": [(operator.eq, town)]},
        )

        query_res = self.shared_scan_query(town_position_match)

        return query_res


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
    resale_data = ResalePriceDataMP()
    with open(file_path, mode="r") as file:
        csv_reader = csv.reader(file)
        _ = next(csv_reader)
        for row in csv_reader:
            resale_data.add_data(row)

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
    print("StdDev price: ", sd_price[0])
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
