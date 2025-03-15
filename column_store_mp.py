# import csv
# import time

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

from multiprocessing import Pool, cpu_count
from multiprocess import worker, parallel_processing
import pandas as pd
import operator
from concurrent.futures import ThreadPoolExecutor


class ResalePriceDataMP:
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

    # Jinyang's
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

    def _filter_column(self, args):
        """Helper function to filter a column in parallel."""
        column_data, condition, col_idx = args
        matches = []
        rows_scanned = 0

        for i, value in enumerate(column_data):
            rows_scanned += 1
            if condition(value, i):
                matches.append(i)

        return matches, rows_scanned

    def min_price(self, year, month, town, log_query=False):
        min_price = float("inf")

        rows_scanned = [0] * 4
        col_idx = 0

        # start with area
        area_position_match = []
        for i, area in enumerate(self.columns["floor_area_sqm"].data):
            rows_scanned[col_idx] += 1
            if area >= 80:
                area_position_match.append(i)
        col_idx += 1

        # month
        month_position_match = []
        for i in area_position_match:
            rows_scanned[col_idx] += 1
            if (
                self.columns["month"].data[i]["month"] == month
                or self.columns["month"].data[i]["month"] == month + 1
            ):
                month_position_match.append(i)
        col_idx += 1

        # year
        year_position_match = []
        for i in month_position_match:
            rows_scanned[col_idx] += 1
            if self.columns["month"].data[i]["year"] == year:
                year_position_match.append(i)
        col_idx += 1

        # town
        town_position_match = []
        for i in year_position_match:
            rows_scanned[col_idx] += 1
            if self.columns["town"].data[i] == town:
                town_position_match.append(i)
        col_idx += 1

        # price
        for i in town_position_match:
            if self.columns["resale_price"].data[i] < min_price:
                min_price = self.columns["resale_price"].data[i]

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
            return min_price if min_price != float(
                "inf"
            ) else "No result", query_lengths_df

        return min_price if min_price != float("inf") else "No result"

    def min_price_modified(self, year, month, town, log_query=False):
        min_price = float("inf")

        # Parallel processing setup
        num_workers = cpu_count()
        pool = Pool(processes=num_workers)

        # Step 1: Filter by floor area (>= 80 sqm)
        def area_condition(value, i):
            return value >= 80

        area_args = (self.columns["floor_area_sqm"].data, area_condition, 0)
        area_position_match, rows_scanned_area = self._filter_column(area_args)

        # Step 2: Filter by month
        def month_condition(value, i):
            return value["month"] == month or value["month"] == month + 1

        month_args = (self.columns["month"].data, month_condition, 1)
        month_position_match, rows_scanned_month = self._filter_column(month_args)

        # Step 3: Filter by year
        def year_condition(value, i):
            return value["year"] == year

        year_args = (self.columns["month"].data, year_condition, 2)
        year_position_match, rows_scanned_year = self._filter_column(year_args)

        # Step 4: Filter by town
        def town_condition(value, i):
            return value == town

        town_args = (self.columns["town"].data, town_condition, 3)
        town_position_match, rows_scanned_town = self._filter_column(town_args)

        # Compute intersection of matches
        final_matches = (
            set(area_position_match)
            & set(month_position_match)
            & set(year_position_match)
            & set(town_position_match)
        )

        # Step 5: Compute min price
        for i in final_matches:
            if self.columns["resale_price"].data[i] < min_price:
                min_price = self.columns["resale_price"].data[i]

        # Close the multiprocessing pool
        pool.close()
        pool.join()

        # Log Query Stats
        if log_query:
            query_lengths_df = pd.DataFrame(
                {
                    "cols": ["floor_area_sqm", "month", "year", "town"],
                    "lengths": [
                        rows_scanned_area,
                        rows_scanned_month,
                        rows_scanned_year,
                        rows_scanned_town,
                    ],
                }
            )
            return min_price if min_price != float(
                "inf"
            ) else "No result", query_lengths_df

        return min_price if min_price != float("inf") else "No result"

    def _filter_chunk(self, chunk):
        """Filters a chunk of data and returns the minimum price found in that chunk."""
        min_price = float("inf")

        ## Single method
        # for i in chunk:
        #     if (
        #         self.columns["floor_area_sqm"].data[i] >= 80
        #         and (
        #             self.columns["month"].data[i]["month"] == self.query_month
        #             or self.columns["month"].data[i]["month"] == self.query_month + 1
        #         )
        #         and self.columns["month"].data[i]["year"] == self.query_year
        #         and self.columns["town"].data[i] == self.query_town
        #     ):
        #         min_price = min(min_price, self.columns["resale_price"].data[i])

        ## Split up method
        # Step 1: Filter by floor area
        filtered_indices = [
            i for i in chunk if self.columns["floor_area_sqm"].data[i] >= 80
        ]

        # Step 2: Filter by month
        filtered_indices = [
            i
            for i in filtered_indices
            if self.columns["month"].data[i]["month"] == self.query_month
            or self.columns["month"].data[i]["month"] == self.query_month + 1
        ]

        # Step 3: Filter by year
        filtered_indices = [
            i
            for i in filtered_indices
            if self.columns["month"].data[i]["year"] == self.query_year
        ]

        # Step 4: Filter by town
        filtered_indices = [
            i
            for i in filtered_indices
            if self.columns["town"].data[i] == self.query_town
        ]

        # Step 5: Find min price
        for i in filtered_indices:
            min_price = min(min_price, self.columns["resale_price"].data[i])

        return min_price

    def min_price_chunk(self, year, month, town, log_query=False):
        """Parallelized function to find minimum price."""
        self.query_year = year
        self.query_month = month
        self.query_town = town

        num_workers = cpu_count()
        num_rows = len(self.columns["floor_area_sqm"].data)

        # Create chunks (split indices into equal parts)
        chunk_size = max(1, num_rows // num_workers)
        chunks = [
            list(range(i, min(i + chunk_size, num_rows)))
            for i in range(0, num_rows, chunk_size)
        ]

        # Multiprocessing to filter chunks in parallel
        with Pool(processes=num_workers) as pool:
            results = pool.map(self._filter_chunk, chunks)

        # Get the minimum price from all chunks
        min_price = min(results)

        return min_price if min_price != float("inf") else "No result"

    def _filter_column_thread(self, column_data, condition):
        """Helper function to filter a column using a condition."""
        matches = []
        rows_scanned = 0
        for i, value in enumerate(column_data):
            rows_scanned += 1
            if condition(value, i):
                matches.append(i)
        return matches, rows_scanned

    def min_price_thread(self, year, month, town, log_query=False):
        min_price = float("inf")

        with ThreadPoolExecutor(max_workers=4) as executor:
            # Step 1: Filter by floor area (>= 80 sqm)
            def area_condition(value, i):
                return value >= 80

            area_future = executor.submit(
                self._filter_column_thread,
                self.columns["floor_area_sqm"].data,
                area_condition,
            )

            # Step 2: Filter by month
            def month_condition(value, i):
                return value["month"] == month or value["month"] == month + 1

            month_future = executor.submit(
                self._filter_column_thread, self.columns["month"].data, month_condition
            )

            # Step 3: Filter by year
            def year_condition(value, i):
                return value["year"] == year

            year_future = executor.submit(
                self._filter_column_thread, self.columns["month"].data, year_condition
            )

            # Step 4: Filter by town
            def town_condition(value, i):
                return value == town

            town_future = executor.submit(
                self._filter_column_thread, self.columns["town"].data, town_condition
            )

            # Retrieve results
            area_position_match, rows_scanned_area = area_future.result()
            month_position_match, rows_scanned_month = month_future.result()
            year_position_match, rows_scanned_year = year_future.result()
            town_position_match, rows_scanned_town = town_future.result()

        # Compute intersection of matches
        final_matches = (
            set(area_position_match)
            & set(month_position_match)
            & set(year_position_match)
            & set(town_position_match)
        )

        # Step 5: Compute min price
        for i in final_matches:
            if self.columns["resale_price"].data[i] < min_price:
                min_price = self.columns["resale_price"].data[i]

        # Log Query Stats
        if log_query:
            query_lengths_df = pd.DataFrame(
                {
                    "cols": ["floor_area_sqm", "month", "year", "town"],
                    "lengths": [
                        rows_scanned_area,
                        rows_scanned_month,
                        rows_scanned_year,
                        rows_scanned_town,
                    ],
                }
            )
            return min_price if min_price != float(
                "inf"
            ) else "No result", query_lengths_df

        return min_price if min_price != float("inf") else "No result"

    # Minimum Price
    def min_price_year_first(self, year, month, town, log_query=False):
        min_price = float("inf")

        rows_scanned = [0] * 4
        col_idx = 0

        print(len(self.columns["floor_area_sqm"].data))

        # STEP: Get floor_area_sqm
        area_position_match = parallel_processing(
            self.columns["floor_area_sqm"].data, criterions={"uni": [(operator.ge, 80)]}
        )
        print("1: ", len(area_position_match))
        # TODO: to do year first instead of month; we keep this order first so that we can perform comparisons
        # STEP: Get month
        # TODO: Can we seperate the month and year instead and just reference them by self.columns["month"].data and self.columns["year"].data?
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
        print("2: ", len(year_position_match))

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
        print("3: ", len(month_position_match))

        # STEP: Get town
        town_position_match = parallel_processing(
            self.columns["town"].data,
            matched_idxs=month_position_match,
            criterions={"uni": [(operator.eq, town)]},
        )
        print("4: ", len(town_position_match))

        # price
        for i in town_position_match:
            if self.columns["resale_price"].data[i] < min_price:
                min_price = self.columns["resale_price"].data[i]

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
            return min_price if min_price != float(
                "inf"
            ) else "No result", query_lengths_df

        return min_price if min_price != float("inf") else "No result"

    def min_price_month_first(self, year, month, town, log_query=False):
        min_price = float("inf")

        rows_scanned = [0] * 4
        col_idx = 0

        print(len(self.columns["floor_area_sqm"].data))

        # STEP: Get floor_area_sqm
        area_position_match = parallel_processing(
            self.columns["floor_area_sqm"].data, criterions={"uni": [(operator.ge, 80)]}
        )
        print("1: ", len(area_position_match))
        # TODO: to do year first instead of month; we keep this order first so that we can perform comparisons
        # STEP: Get month
        # TODO: Can we seperate the month and year instead and just reference them by self.columns["month"].data and self.columns["year"].data?
        months = [
            self.columns["month"].data[i]["month"]
            for i in range(len(self.columns["month"].data))
        ]
        years = [
            self.columns["month"].data[i]["year"]
            for i in range(len(self.columns["month"].data))
        ]
        month_position_match = parallel_processing(
            months,
            matched_idxs=area_position_match,
            criterions={
                "or": [
                    (operator.eq, month),
                    (operator.eq, month + 1),
                ]
            },
        )
        print("2: ", len(month_position_match))

        # STEP: Get year
        year_position_match = parallel_processing(
            years,
            matched_idxs=month_position_match,
            criterions={"uni": [(operator.eq, year)]},
        )
        print("3: ", len(year_position_match))

        # STEP: Get town
        town_position_match = parallel_processing(
            self.columns["town"].data,
            matched_idxs=year_position_match,
            criterions={"uni": [(operator.eq, town)]},
        )
        print("4: ", len(town_position_match))

        # price
        for i in town_position_match:
            if self.columns["resale_price"].data[i] < min_price:
                min_price = self.columns["resale_price"].data[i]

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
            return min_price if min_price != float(
                "inf"
            ) else "No result", query_lengths_df

        return min_price if min_price != float("inf") else "No result"

    # Standard Deviation of Price
    def sd_price(self, year, month, town, log_query=False):
        rows_scanned = [0] * 4
        col_idx = 0

        # start with area
        area_position_match = []
        for i, area in enumerate(self.columns["floor_area_sqm"].data):
            rows_scanned[col_idx] += 1
            if area >= 80:
                area_position_match.append(i)
        col_idx += 1

        # month
        month_position_match = []
        for i in area_position_match:
            rows_scanned[col_idx] += 1
            if (
                self.columns["month"].data[i]["month"] == month
                or self.columns["month"].data[i]["month"] == month + 1
            ):
                month_position_match.append(i)
        col_idx += 1

        # year
        year_position_match = []
        for i in month_position_match:
            rows_scanned[col_idx] += 1
            if self.columns["month"].data[i]["year"] == year:
                year_position_match.append(i)
        col_idx += 1

        # town
        town_position_match = []
        for i in year_position_match:
            rows_scanned[col_idx] += 1
            if self.columns["town"].data[i] == town:
                town_position_match.append(i)
        col_idx += 1

        # price
        prices = [self.columns["resale_price"].data[i] for i in town_position_match]

        if not prices:
            query_res = "No Results"
        else:
            mean_price = sum(prices) / len(prices)
            variance = sum((price - mean_price) ** 2 for price in prices) / (
                len(prices) - 1
            )
            query_res = round(variance**0.5, 2)

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
            return query_res, query_lengths_df
        return query_res

    # Average Price
    def avg_price(self, year, month, town, log_query=False):
        rows_scanned = [0] * 4
        col_idx = 0

        # start with area
        area_position_match = []
        for i, area in enumerate(self.columns["floor_area_sqm"].data):
            rows_scanned[col_idx] += 1
            if area >= 80:
                area_position_match.append(i)
        col_idx += 1

        # month
        month_position_match = []
        for i in area_position_match:
            rows_scanned[col_idx] += 1
            if (
                self.columns["month"].data[i]["month"] == month
                or self.columns["month"].data[i]["month"] == month + 1
            ):
                month_position_match.append(i)
        col_idx += 1

        # year
        year_position_match = []
        for i in month_position_match:
            rows_scanned[col_idx] += 1
            if self.columns["month"].data[i]["year"] == year:
                year_position_match.append(i)
        col_idx += 1

        # town
        town_position_match = []
        for i in year_position_match:
            rows_scanned[col_idx] += 1
            if self.columns["town"].data[i] == town:
                town_position_match.append(i)
        col_idx += 1

        # price
        prices = [self.columns["resale_price"].data[i] for i in town_position_match]

        if not prices:
            query_res = "No Results"
        else:
            mean_price = sum(prices) / len(prices)
            query_res = round(mean_price, 2)

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
            return query_res, query_lengths_df
        return query_res

    # Minimum Price per Square Meter
    def min_price_per_sqm(self, year, month, town, log_query=False):
        min_price_per_sqm = float("inf")

        rows_scanned = [0] * 4
        col_idx = 0
        # start with area
        area_position_match = []
        for i, area in enumerate(self.columns["floor_area_sqm"].data):
            rows_scanned[col_idx] += 1
            if area >= 80:
                area_position_match.append(i)
        col_idx += 1

        # month
        month_position_match = []
        for i in area_position_match:
            rows_scanned[col_idx] += 1
            if (
                self.columns["month"].data[i]["month"] == month
                or self.columns["month"].data[i]["month"] == month + 1
            ):
                month_position_match.append(i)
        col_idx += 1

        # year
        year_position_match = []
        for i in month_position_match:
            rows_scanned[col_idx] += 1
            if self.columns["month"].data[i]["year"] == year:
                year_position_match.append(i)
        col_idx += 1

        # town
        town_position_match = []
        for i in year_position_match:
            rows_scanned[col_idx] += 1
            if self.columns["town"].data[i] == town:
                town_position_match.append(i)
        col_idx += 1

        # price
        for i in town_position_match:
            price_per_sqm = (
                self.columns["resale_price"].data[i]
                / self.columns["floor_area_sqm"].data[i]
            )
            if price_per_sqm < min_price_per_sqm:
                min_price_per_sqm = price_per_sqm

        if min_price_per_sqm != float("inf"):
            query_res = "No Results"
        else:
            query_res = round(min_price_per_sqm, 2)

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
            return query_res, query_lengths_df
        return query_res


# def main():
#     town_map = {
#     0: "BEDOK",
#     1: "BUKIT PANJANG",
#     2: "CLEMENTI",
#     3: "CHOA CHU KANG",
#     4: "HOUGANG",
#     5: "JURONG WEST",
#     6: "PASIR RIS",
#     7: "TAMPINES",
#     8: "WOODLANDS",
#     9: "YISHUN",
#     }

#     year_map = {
#         0: 2020,
#         1: 2021,
#         2: 2022,
#         3: 2023,
#         4: 2014,
#         5: 2015,
#         6: 2016,
#         7: 2017,
#         8: 2018,
#         9: 2019,
#     }

#     # matric number
#     matric_number = "U2121223J" #Darren
#     # matric_number = "U2121763H" #Bryan
#     # matric_number = "U2122055E" #Jin Yang

#     last_digit_year = int(matric_number[-2])
#     year = year_map[last_digit_year]
#     month = int(matric_number[-3])
#     town_index = int(matric_number[-4])
#     town = town_map[town_index]

#     file_path = "ResalePricesSingapore.csv"
#     resale_data = ResalePriceData()
#     with open(file_path, mode="r") as file:
#         csv_reader = csv.reader(file)
#         _ = next(csv_reader)
#         for row in csv_reader:
#             resale_data.add_data(row)


#     start_time = time.time()
#     min_price = resale_data.min_price(year,month,town)
#     end_time = time.time()
#     print("Minimum price: ", min_price)
#     print(f"Time taken for min_price: {end_time - start_time} seconds")


#     start_time = time.time()
#     sd_price = resale_data.sd_price(year, month, town)
#     end_time = time.time()
#     print("StdDev price: ", sd_price)
#     print(f"Time taken for sd_price: {end_time - start_time} seconds")


#     start_time = time.time()
#     avg_price = resale_data.avg_price(year,month,town)
#     end_time = time.time()
#     print("Average price: ", avg_price)
#     print(f"Time taken for avg_price: {end_time - start_time} seconds")

#     start_time = time.time()
#     min_price_per_sqm = resale_data.min_price_per_sqm(year,month,town)
#     end_time = time.time()
#     print("Minimum price per sqm: ", min_price_per_sqm)
#     print(f"Time taken for min_price_per_sqm: {end_time - start_time} seconds")


# if __name__ == "__main__":
#     main()
