import time

import pandas as pd


class Query:
    @staticmethod
    def query(
        year,
        month,
        town,
        area_query,
        month_query,
        year_query,
        town_query,
        price_query,
        log_query=False,
    ):
        rows_scanned = [0] * 4
        col_idx = 0

        # start with area
        area_position_match, rows_scanned = area_query(rows_scanned, col_idx)
        col_idx += 1

        # year
        year_position_match, rows_scanned = year_query(
            area_position_match, rows_scanned, col_idx, year
        )
        col_idx += 1

        # month
        month_position_match, rows_scanned = month_query(
            year_position_match, rows_scanned, col_idx, month
        )
        col_idx += 1

        # town
        town_position_match, rows_scanned = town_query(
            month_position_match, rows_scanned, col_idx, town
        )
        col_idx += 1

        # price
        query_res = price_query(town_position_match)

        if log_query:
            col_string = ""
            query_lengths = {}
            col_string += "->floor_area_sqm"
            query_lengths[col_string] = rows_scanned[0]
            col_string += "->year"
            query_lengths[col_string] = rows_scanned[1]
            col_string += "->month"
            query_lengths[col_string] = rows_scanned[2]
            col_string += "->town"
            query_lengths[col_string] = rows_scanned[3]

            query_lengths_df = pd.DataFrame(
                {
                    "cols": list(query_lengths.keys()),
                    "lengths": list(query_lengths.values()),
                }
            )
            return query_res, query_lengths_df

        return query_res

    @staticmethod
    def column_store_query(resale_data):
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

        # if resale data has town_enncoding
        if hasattr(resale_data, "town_encoder"):
            town = resale_data.town_encoder.mappings[town]

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
