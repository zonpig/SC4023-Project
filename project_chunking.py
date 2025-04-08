import csv
import time
import argparse
import numpy as np
from tqdm import tqdm
from column_store import ResalePriceData
from column_store_encoded import ResalePriceDataEncoded
from column_store_zone_map_cat import ResalePriceDataZoneMapCat
from column_store_zone_map_num import ResalePriceDataZoneMapNum
from column_store_mp import ResalePriceDataMP
from collections import defaultdict
import pandas as pd

import csv
import sys
import psutil

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


def read_csv(
    file_path: str, type: int, start_idx: int, end_idx: int, headers: list[str]
):
    if type == 0:
        resale_data = ResalePriceData()
    elif type == 1:
        resale_data = ResalePriceDataEncoded()
    elif type == 2:
        resale_data = ResalePriceDataZoneMapNum()
    elif type == 3:
        resale_data = ResalePriceDataZoneMapCat()
    elif type == 4:
        resale_data = ResalePriceDataMP()

    nrows = end_idx - start_idx + 1
    df = pd.read_csv(
        file_path,
        skiprows=range(0, start_idx + 1),
        nrows=nrows,
        header=None,
        names=headers,
    )

    for row in df.itertuples(index=False):
        row_values = list(row)  # Convert namedtuple to list
        resale_data.add_data(row_values)
    return resale_data


def get_csv_headers(file_path: str, encoding="utf-8"):
    with open(file_path, mode="r", encoding=encoding) as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
    return header


def split_csv(file_path: str, max_memory_mb=None, encoding="utf-8"):
    """
    Yield row index ranges ([start, end]) from a CSV that can fit within memory limit.

    Args:
        csv_path (str): Path to the CSV file.
        max_memory_mb (float): Max memory allowed per chunk in MB. If None, will use 80% of available memory.
        encoding (str): File encoding.

    Yields:
        Tuple[int, int]: (start_index, end_index) of each chunk
    """
    if max_memory_mb is None:
        available_memory = psutil.virtual_memory().available / (1024**2)
        max_memory_mb = available_memory * 0.2  # use x% of available memory

    chunk_start = 1
    chunk_memory = 0.0
    current_index = 1
    chunk_indices = []

    with open(file_path, mode="r", encoding=encoding) as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
        for row in reader:
            row_memory = sys.getsizeof(row) / (1024**2)  # in MB

            if chunk_memory + row_memory > max_memory_mb:
                chunk_indices.append((chunk_start, current_index - 1))
                chunk_start = current_index
                chunk_memory = 0.0

            chunk_memory += row_memory
            current_index += 1

        # Yield the final chunk
        if chunk_start < current_index:
            chunk_indices.append((chunk_start, current_index - 1))

    return chunk_indices


# You are expected to write a program to manage the data in a column-oriented manner,
# including data storage and processing. Your program should first receive queries, scan
# the data columns to find matched lines, and compute the results according to associated
# query content. To be specific, a query is composed of a target time (YYYY-MM to YYYY-
# (MM+1)), a matched town, and a query content. These factors are determined by your
# matriculation number as follows:
# a) The last digit of the year of the target time (YYYY) equals the last digit of the matriculation number;
# b) the commencing month (MM) equals the second last digit of the matriculation number (note that “0" represents October);
# c) the matched town depends on the third last digit of the matriculation number as Table 1 presents;
# d) there are four query contents in total that are listed in Table 2, and the area requirement (≥80m2) is applicable to all these contents.
# the area requirement (≥80m2) is applicable to all these contents


def main(args):
    # matric number
    if args.matric_number:
        matric_number = args.matric_number
    else:
        # Ask them to choose from the list
        print("Please choose a matric number from the list:")
        print("1. U2121223J")
        print("2. U2121763H")
        print("3. U2122055E")
        choice = input("Enter the number corresponding to your choice: ")
        if choice == "1":
            matric_number = "U2121223J"
        elif choice == "2":
            matric_number = "U2121763H"
        elif choice == "3":
            matric_number = "U2122055E"
        else:
            # Tell them that default value of
            # U2121223J will be used
            print("Invalid choice. Using default value U2121223J.")
            matric_number = "U2121223J"

    last_digit_year = int(matric_number[-2])
    year = year_map[last_digit_year]
    month = int(matric_number[-3])
    town_index = int(matric_number[-4])
    town = town_map[town_index]

    file_path = "ResalePricesSingapore.csv"

    final_res = defaultdict(dict)  # store results of each chunk
    time_res = defaultdict(dict)  # store time taken for each run
    results_calculated = False

    scenarios = [
        "original",
        "categorical_encoded",
        "zone_map_num",
        "zone_map_cat",
        "shared_scan",
        "vector_at_a_time_with_multiprocessing",
    ]
    # Add your keys from the 'scenarios' dictionary
    for key in scenarios:
        final_res[key]  # This will create a default empty dictionary for each key
        time_res[key]

    for _ in tqdm(range(args.num_runs), desc="Running repeated runs of queries."):
        splits = split_csv(file_path)
        csv_headers = get_csv_headers(file_path)

        split_timings = defaultdict(dict)
        for key in scenarios:
            split_timings[key]

        for start_idx, end_idx in splits:
            column_store = read_csv(
                file_path, 0, start_idx=start_idx, end_idx=end_idx, headers=csv_headers
            )
            column_store_encoded = read_csv(
                file_path, 1, start_idx=start_idx, end_idx=end_idx, headers=csv_headers
            )
            column_store_zone_map_num = read_csv(
                file_path, 2, start_idx=start_idx, end_idx=end_idx, headers=csv_headers
            )
            column_store_zone_map_cat = read_csv(
                file_path, 3, start_idx=start_idx, end_idx=end_idx, headers=csv_headers
            )
            column_store_mp = read_csv(
                file_path, 4, start_idx=start_idx, end_idx=end_idx, headers=csv_headers
            )

            # preprocess
            column_store_encoded.encode_town()
            if town not in column_store_encoded.town_encoder.mappings:
                column_store_encode_town = len(
                    column_store_encoded.town_encoder.mappings
                )
            else:
                column_store_encode_town = column_store_encoded.town_encoder.mappings[
                    town
                ]  # get the encoded town value

            column_store_zone_map_num.create_zone_map(16)

            column_store_zone_map_cat.create_zone_map("flat_type")

            scenarios = {
                "original": {"col_db": column_store, "town": town},
                "categorical_encoded": {
                    "col_db": column_store_encoded,
                    "town": column_store_encode_town,
                },
                "zone_map_num": {"col_db": column_store_zone_map_num, "town": town},
                "zone_map_cat": {"col_db": column_store_zone_map_cat, "town": town},
                "vector_at_a_time_with_multiprocessing": {
                    "col_db": column_store_mp,
                    "town": town,
                },
            }

            for k in scenarios.keys():
                start_time = time.time()
                x = scenarios[k]["col_db"].min_price(year, month, scenarios[k]["town"])
                end_time = time.time()
                times = split_timings[k].get("min_price", [])
                times.append(end_time - start_time)
                split_timings[k]["min_price"] = times
                res = final_res[k].get("min_price", [])
                res.append(x)
                final_res[k]["min_price"] = res

                start_time = time.time()
                x = scenarios[k]["col_db"].sd_price(year, month, scenarios[k]["town"])
                end_time = time.time()
                times = split_timings[k].get("sd_price", [])
                times.append(end_time - start_time)
                split_timings[k]["sd_price"] = times
                res = final_res[k].get("sd_price", [])
                res.append(x)
                final_res[k]["sd_price"] = res

                start_time = time.time()
                x = scenarios[k]["col_db"].avg_price(year, month, scenarios[k]["town"])
                end_time = time.time()
                times = split_timings[k].get("avg_price", [])
                times.append(end_time - start_time)
                split_timings[k]["avg_price"] = times
                res = final_res[k].get("avg_price", [])
                res.append(x)
                final_res[k]["avg_price"] = res

                start_time = time.time()
                x = scenarios[k]["col_db"].min_price_per_sqm(
                    year, month, scenarios[k]["town"]
                )
                end_time = time.time()
                times = split_timings[k].get("min_price_per_sqm", [])
                times.append(end_time - start_time)
                split_timings[k]["min_price_per_sqm"] = times
                res = final_res[k].get("min_price_per_sqm", [])
                res.append(x)
                final_res[k]["min_price_per_sqm"] = res

        if not results_calculated:
            original_res = final_res["original"]
            chunk_sizes = [end - start + 1 for start, end in splits]
            total_size = [
                splits[-1][-1],
                splits[-1][-1],
                splits[-1][-1],
                splits[-1][-1],
            ]

            print(original_res["sd_price"])

            keys = [k for k in original_res.keys()]
            for out_idx, k in enumerate(keys):
                cpy = original_res[k].copy()
                cur_list = []
                for idx, val in enumerate(cpy):
                    if isinstance(val, tuple):
                        if len(val) == 2:
                            _, row_used = val
                        elif len(val) == 3:
                            _, row_used, _ = val
                        if row_used == 0:
                            total_size[out_idx] -= chunk_sizes[idx]
                            continue
                        else:
                            cur_list.append(val)
                    elif val == "No Results":
                        total_size[out_idx] -= chunk_sizes[idx]
                    else:
                        cur_list.append(val)

                original_res[k] = cur_list

            # STEP: Determine min price
            min_price = min(original_res["min_price"])

            # STEP: Determine sd
            # sd_price = np.sqrt(
            #     sum((stdev**2) * row_used for stdev, row_used in original_res["sd_price"])
            #     / sum(row_used for _, row_used in original_res["sd_price"])
            # )
            numerator = 0
            total_n = 0

            # First calculate the overall mean
            overall_sum = sum(mean * n for _, n, mean in original_res["sd_price"])
            overall_n = sum(n for _, n, _ in original_res["sd_price"])
            print(original_res["sd_price"])
            overall_mean = overall_sum / overall_n

            # Now calculate the total variance
            for sd, n, mean in original_res["sd_price"]:
                numerator += (n - 1) * (sd**2) + n * ((mean - overall_mean) ** 2)
                total_n += n

            combined_variance = numerator / (total_n - 1)
            sd_price = np.sqrt(combined_variance)

            # STEP: Determine average
            avg_price = sum(
                avg * row_used for avg, row_used in original_res["avg_price"]
            ) / sum(row_used for _, row_used in original_res["avg_price"])

            # STEP: Determine min_price_per_sqm
            min_price_per_sqm = min(original_res["min_price_per_sqm"])

            scan_results = {
                "Minimum Price": min_price,
                "Standard Deviation of Price": sd_price,
                "Average Price": avg_price,
                "Minimum Price per Square Meter": min_price_per_sqm,
            }

            results = [
                {
                    "Year": year,
                    "Month": month,
                    "Town": town,
                    "Category": category,
                    "Value": round(value, 2),
                }
                for category, value in scan_results.items()
            ]

            with open(f"ScanResult_{matric_number}.csv", mode="w", newline="") as file:
                writer = csv.DictWriter(
                    file, fieldnames=["Year", "Month", "Town", "Category", "Value"]
                )
                writer.writeheader()
                for result in results:
                    writer.writerow(result)
            results_calculated = True

        # consolidate the timings
        for scenario in split_timings.keys():
            for query, query_runtimes in split_timings[scenario].items():
                consolidated_runtimes = time_res[scenario].get(query, [])
                consolidated_runtimes.append(sum(query_runtimes))
                time_res[scenario][query] = consolidated_runtimes

    print(f"{args.num_runs} runs concluded!")
    print()
    if args.aggregation == "mean":
        for k in scenarios.keys():
            print("Scenario: ", k)
            N = args.num_runs
            for q in time_res[k].keys():
                print(f"Avg time taken for {q} query: {sum(time_res[k][q]) / N}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description of your program")

    # Adding arguments
    parser.add_argument(
        "--matric_number", type=str, help="Matriculation number to be used"
    )

    # Adding arguments
    parser.add_argument(
        "--num_runs", type=int, default=1, help="Number of runs to repeat."
    )

    parser.add_argument(
        "--aggregation",
        type=str,
        default="mean",
        help="Method to aggregate runs results.",
    )

    args = parser.parse_args()

    main(args)
